# Plano de execução — agente de código

Nota de arquivo: versão 0 do plano do Estudo 05, recebida do proponente em
2026-11-25 e reproduzida sem alteração de conteúdo (apenas omitida a pergunta
final dirigida ao assistente). Ajustes de conciliação com o contrato de
evidência e com os Estudos 03 e 04 estão em `CONCILIACAO.md` e só valem depois
de aprovados e registrados em `protocolos/REGISTRO.md`.

---

Especificação operacional. Pressupõe shell, rede, Python 3.12, e nenhuma decisão de julgamento delegada ao agente: as regras estão escritas, o agente só as aplica. Onde houver ambiguidade, o agente **para** e registra — não infere.

---

## 0. Missão e não-objetivos

**Missão:** produzir `dossie.md`, `achados_negativos.md`, `matriz_aderencia_edital.csv`, `resumo.md` e `artefatos/` a partir de artefatos públicos do TSE do pleito 2026, classificados A–D, com carimbo de tempo e cadeia de custódia, segundo as três perguntas (concreto / consistente / verificável).

**Não-objetivos:** concluir se houve fraude; analisar estatística de voto como achado; baixar o acervo inteiro de logs antes de a fase 2 fechar; promover L3 a A/B.

**Pergunta primária:** existe hash de sistema divergente entre UFs no mesmo pleito? (fase 2)
**Pergunta secundária:** existe artefato de assinatura que não fecha? (fase 3)
**Pergunta terciária:** existe anomalia de log compatível com injeção? (fase 4, só com orçamento)

---

## 1. Invariantes — o agente não pode violar

1. Hash do arquivo bruto **antes** de qualquer leitura. sha256 + sha512, ambos.
2. Nunca recompactar `.jez`. Nunca sobrescrever `raw/`. Republicação = `raw/orig.2` + novo carimbo.
3. Comparação de integridade é sempre sobre conteúdo descompactado, nunca sobre o ZIP.
4. `HALT` em schema desconhecido. Não adivinhar campo, não usar `try/except: pass`.
5. Falha de rede não é achado. Timeout, 429 e 503 vão para `retry`, com backoff, e depois para `pendente`.
6. 404 vai para `ausente`, não para `falha` — o 2º turno expira.
7. Todo achado precisa de **regra** + **âncora** (vsc, aux.json ou hash publicado). Sem âncora, é `indicio_fraco`.
8. Nenhum texto no relatório afirma fraude. Vocabulário fechado: `divergência`, `anomalia`, `inconsistência`, `sem explicação benigna identificada`.
9. Toda saída é idempotente por chave `(turno, uf, municipio, zona, secao, tipo)`.
10. Quarentena em vez de descarte. Nunca `rm`.

---

## 2. Árvore do repositório

```
.
├── PLANO.md
├── DECISOES.md              # append-only, uma linha por decisão com timestamp
├── buildinfo.json           # versões pinadas, SOURCE_DATE_EPOCH, commit
├── keys/                    # minisign do coletor
├── fixtures/                # amostras sintéticas + reais pequenas para teste
├── src/
│   ├── catalog.py           # descoberta de URLs e aux.json
│   ├── fetch.py             # download com retry, ETag, quarentena
│   ├── stamp.py             # sha256/sha512/tsq/tsr/ots/rekor
│   ├── hashes_list.py       # parse da página de resumos digitais
│   ├── uf_diff.py           # fase 2
│   ├── bu.py                # ASN.1 BU (spec TSE)
│   ├── rdv.py               # ASN.1 RDV
│   ├── vsc.py               # assinatura, tipo HW/SW, cert, cadeia
│   ├── imgbu.py             # extração de bitmap, decode QR, fingerprint
│   ├── logjez.py            # 7z, esquema de eventos, fingerprint
│   ├── baseline.py          # distribuições por modelo de urna
│   ├── rules.py             # motor de regras R01..R20
│   ├── triage.py            # aplica regras, exige âncora
│   ├── report.py            # gerador dos entregáveis
│   └── db.py                # sqlite, fila e estado
├── artefatos/
├── quarantine/
├── out/
└── run.sh
```

`db.py` é sqlite com tabela `fila(chave PK, turno, uf, mun, zona, secao, tipo, estado, tentativas, motivo)`. Estados: `novo`, `baixado`, `carimbado`, `analisado`, `ausente`, `quarentena`, `pendente`. O agente nunca reprocessa `analisado`.

---

## 3. Fases e gates

Cada fase termina em gate binário. Gate reprovado → não avança, escreve o parcial e para.

### F0 — Bootstrap
Pin de versões em `buildinfo.json` (`python`, `pyasn1`, `asn1crypto`, `cryptography`, `pyzbar`, `py7zr`, `minisign`, `rekor-cli`, `ots`). `SOURCE_DATE_EPOCH` do commit. Par minisign gerado. `sqlite` inicializado.
**Gate F0:** `./run.sh selftest` verde nas fixtures.

### F1 — Congelamento de L1
Baixar e carimbar, nesta ordem: página de resumos digitais 2026 (1º e 2º), página de hashes raiz, página de lacração, Res. 23.673, Relatório Parcial TPS 2025, manuais de QR/ASN.1, lista das 15 sistemas do art. 3º.
**Gate F1:** 8 artefatos com `.sha256`, `.tsr` verificado por `openssl ts -verify`, `rekor.json` com `logIndex`. Falta de TSA = gate reprovado (freetsa cai; tentar 5×, depois TSA alternativa).

### F2 — Divergência de hash entre UFs ← **prioridade máxima**
Parse da página de resumos digitais: extrair por sistema × UF o hash publicado. Normalizar nome de sistema (Gedai-UE, Sistot, VOTA, GAP, RecArquivos, Transportador, InfoArquivos, SIS, Kit JE-Connect, SAVP-Sorteio, SAVP-Votação, AVPART, VAD, VAP, VPP, firmwares).
Comparar matriz UF × sistema. Aplicar R01–R03.
**Gate F2:** matriz completa 27 UFs × sistemas, com célula `presente/ausente/divergente` preenchida. Qualquer célula vazia por erro de parse = HALT.
**Saída imediata:** se R01 disparar, escrever `out/ALERTA_F2.md` e publicar parcial antes de continuar.

### F3 — Varredura de assinatura (amostra estratificada)
Amostra: 5 seções por UF (135), estratificadas por modelo de urna, mais as 20 seções do Teste de Integridade, mais 20 seções sem biometria como controle.
Por seção: baixar `-vota.vsc`, `aux.json`, `-bu.dat`, `-imgbu.dat`, `-log.jez`. Verificar assinatura, tipo HW/SW, cadeia, CN↔urna, QR↔BU, BU↔aux.json.
**Gate F3:** baseline de tipo de assinatura por modelo calculada e escrita em `out/baseline_tipo.json`. Se a distribuição for homogênea (100% HW em todos os modelos), marcar R10 como `morto` e seguir.

### F4 — Varredura nacional de T3 (só com orçamento ≥ 500 GB)
Fila completa 27 UFs × 2 turnos. Só logs + vsc + aux.json.
**Gate F4:** 2º turno 100% baixado e carimbado (o 1º pode ficar parcial).

### F5 — Triagem e relatório
`triage.py` aplica regras sobre tudo que tem âncora. `report.py` emite os entregáveis.

---

## 4. Schemas

`findings.jsonl`, uma linha por achado:

```json
{
  "id": "F-2026-0001",
  "regra": "R11",
  "classe": "B",
  "camada": "L2",
  "turno": 2, "uf": "RR", "municipio": "1400100", "zona": "0001", "secao": "0012",
  "artefato": "artefatos/L2/secao-1400100-0001-0012/vota.vsc",
  "ancora": ["vota.vsc", "aux.json"],
  "hash_artefato": "sha256:…",
  "observado": "CN=UE0012345, código da urna no BU=UE0012367",
  "confundidor_testado": ["troca de modelo", "reuso de cert"],
  "g1": true, "g2": true, "g3": true, "g4": false,
  "o_que_falta": "binário da urna para fechar G4",
  "data_artefato": "2026-11-04T23:51Z",
  "coleta_utc": "2026-11-12T10:03Z"
}
```

`baseline_tipo.json`, `out/matriz_uf_sistema.csv`, `run.json` (contadores por estado), `DECISOES.md` (append-only).

---

## 5. Regras — contrato fechado

Cada regra: `id`, `entradas`, `predicado`, `severidade`, `confundidor`, `ancora_obrigatoria`. O motor só emite achado se predicado verdadeiro **e** âncora presente.

| ID | Predicado | Sev | Confundidor | Âncora |
|---|---|---|---|---|
| R01 | hash(sistema, UF_A) ≠ hash(sistema, UF_B), mesmo turno | alta | sistema não se aplica à UF | página de hashes carimbada |
| R02 | sistema presente em A, ausente em B | média | UF com pleito suplementar | idem |
| R03 | ETag da página de hashes muda entre coletas | média | republicação legítima | duas coletas carimbadas |
| R10 | `tipo_assinatura == SW` e baseline do modelo é HW | alta | modelo antigo legítimo | vsc + baseline |
| R11 | `CN != codigo_urna` | **alta** | nenhum conhecido | vsc + BU |
| R12 | cadeia não fecha na AC publicada | **alta** | cert de teste | vsc + conjunto de AC |
| R13 | validade do cert fora da janela do pleito | alta | cert de teste em urna de teste | vsc |
| R14 | hash no payload do QR ≠ sha512 recalculado do BU | **alta** | QR truncado por impressora | imgbu + BU |
| R15 | contagem por candidato RDV ≠ BU | alta | seção sem RDV publicado | rdv + bu |
| R16 | sha512 do BU ≠ aux.json | alta | regeneração benigna | aux.json + bu |
| R17 | votos > comparecimento | média | comparecimento parcial | bu |
| R18 | branco+nulo+nominal ≠ comparecimento | média | cargo sem candidato | bu |
| R19 | fingerprint de QR fora da distribuição do modelo | baixa | troca de fabricante | imgbu + baseline |
| R20 | timestamp de encerramento BU ≠ log | baixa | deriva de relógio | bu + log |

Severidade alta + âncora = candidato a B. Só R11/R12/R14/R15/R16 podem virar B com mérito. R17–R20 no máximo C.

---

## 6. Contratos de função

```python
def fetch(chave: Chave, url: str, *, etag: str | None = None) -> Path:
    """Baixa para raw/orig. 3 tentativas, backoff 15/60/240s.
    Retorna path. Levanta Ausente em 404, Pendente após 3 falhas de rede.
    Grava headers.txt. Nunca segue redirect para domínio fora de *.tse.jus.br."""

def stamp(path: Path) -> Stamp:
    """sha256+sha512 em arquivo separado, tsq, tsr com retry, ots, rekor.
    Levanta StampIncompleto se faltar tsr ou rekor. Idempotente por sha256."""

def parse_hashes_list(html: Path) -> list[HashEntry]:
    """Extrai (sistema, uf, hash). HALT se o número de sistemas != 15
    ou se o número de UFs != 27. Nunca adivinha por posição."""

def diff_uf(entries: list[HashEntry]) -> list[Finding]:
    """Aplica R01-R03 sobre a matriz. Determinístico, ordenado por (sistema, uf)."""

def parse_vsc(path: Path) -> Vsc:
    """Retorna tipo (HW|SW), cert DER, lista de (arquivo, sha512).
    HALT se o ASN.1 não casar com o esquema congelado."""

def verify_chain(cert: Certificate, acs: list[Certificate]) -> bool: ...

def qr_payload_hash(imgbu: Path) -> str:
    """Localiza o bitmap no fim do stream ESC/P2, decodifica, extrai o hash.
    HALT se decodificar 0 ou >1 QR."""

def sweep(secao: Chave) -> list[Finding]:
    """Executa R10-R20 com âncoras. Grava findings.jsonl. Idempotente."""

def triage(findings: list[Finding]) -> list[Finding]:
    """Deduplica por (regra, secao), aplica teto de classe, marca indicio_fraco
    quando falta âncora. Nunca descarta: rebaixa."""
```

---

## 7. Falhas, retomada, quarentena

- `HALT` (para tudo, escreve parcial): schema divergente, contagem de sistemas ≠ 15, UFs ≠ 27, QR ambíguo, TSA indisponível após 5 tentativas, disco < 50 GB.
- `Pendente`: 3 falhas de rede consecutivas na mesma chave.
- `Quarentena` (move, não apaga): hash do ZIP ≠ esperado, `logd.dat` ausente dentro do `.jez`, cert não parseável, tamanho fora de 10× a mediana do tipo.
- Retomada: `run.sh resume` relê a fila por estado. Nenhuma chave em `analisado` é reprocessada.
- `run.sh status` imprime contadores. O agente roda a cada 15 min e anexa em `DECISOES.md`.

---

## 8. Fixtures e testes

`fixtures/` com: 1 BU real pequena, 1 vsc real HW, 1 vsc sintético SW, 1 cert autoassinado, 1 imgbu com QR decodificável, 1 logjez de 3 eventos, 1 par de listas de hash com divergência plantada.

`selftest` deve: (a) casar os 3 R11/R12/R14 plantados; (b) não disparar em seção controle; (c) recusar vsc com schema alterado via HALT; (d) reproduzir o mesmo `findings.jsonl` em duas execuções.

**Gate:** `selftest` verde é pré-requisito de F0. Regra nova exige fixture nova.

---

## 9. Gerador de relatório

`report.py` monta `dossie.md` nesta ordem fixa: sumário do estado, camada L1, camada L2, camada L3, indícios fracos com razão, tabela de cobertura, limites. `achados_negativos.md` é gerado a partir dos estados `ausente` e das superfícies sem resultado — inclusive as buscas de fórum feitas na fase 1.

Regras de redação, verificáveis por lint: nenhuma frase com "provou", "comprovou", "houve fraude"; todo achado cita `artefato` e `ancora`; todo número tem link; toda seção sem achado aparece em `achados_negativos.md`.

`resumo.md` tem exatamente 10 linhas e é gerado por template com os contadores reais.

---

## 10. Orçamento

F1–F3: ~6 GB, ~2 h, 4 workers, 2 req/s por host. F4: ~500 GB, 2–3 dias. Pausa de 10 s a cada 500 requisições. User-Agent identificável com contato no `autor.md`.

---

## 11. Entrega

`dossie.md`, `achados_negativos.md`, `matriz_aderencia_edital.csv`, `resumo.md`, `artefatos/**` com hash+tsr+rekor, `run.json`, `buildinfo.json`, `DECISOES.md`. Empacotar com `tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner`, sha256 do tarball no `MANIFESTO.md`.

---

## 12. Critérios de aceitação finais

O agente só declara concluído se: as 4 perguntas de cada achado estão respondidas em binário; todo achado A/B tem hash, TSA e rekor; a matriz cobre 27 UFs; nenhum item de L3 está acima de C; `selftest` verde; `lint` de redação verde.

**Ponto de parada obrigatório:** se F2 não disparar nada e F3 não disparar nada, o agente **não** parte para F4 sozinho — escreve `out/PARCIAL_SEM_ACHADO.md` e para. Gastar 500 GB para confirmar vazio é decisão humana.
