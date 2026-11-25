# Conciliacao do Estudo 05 com o contrato de evidencia e os Estudos 03 e 04

Data: 2026-11-25
Objeto: `PLANO.md` (versao 0) frente a `evidencias/AGENTS.md` (contrato v1.0,
entrada 05 do REGISTRO), ao Estudo 03 (parser de logs e BU) e ao Estudo 04
(poder de deteccao).
Situacao: APROVADO pelo proponente em 2026-11-25 (D1), com as emendas E1-E6
da secao 7, que prevalecem sobre o texto das secoes 3 a 6 em caso de
conflito. Texto original das secoes 1 a 6 mantido para rastreabilidade.

## 1 Conclusao em uma frase

O plano e o contrato sao o mesmo metodo em duas escalas: o contrato diz o que
uma evidencia precisa ter; o plano e a maquina que produz evidencias L1 em
serie. Ha seis conflitos de nomenclatura ou de regra do repositorio, todos
resolviveis sem mudar a logica, e um limite estrutural que vale para os dois:
por construcao, nenhum achado de F2 a F4 passa de B sem uma ligacao publica
entre o software lacrado e o software executado na urna.

## 2 Pontos ja alinhados (nenhuma acao)

| Plano | Contrato / repositorio |
|-------|------------------------|
| Vocabulario fechado (divergencia, anomalia, inconsistencia) | Aviso do README: anomalia nao e prova de crime |
| `g1..g4` binarios no `findings.jsonl` | Gate G1-G4 (secao 2 do contrato) |
| So R11/R12/R14/R15/R16 chegam a B; R17-R20 no maximo C | G4 falso rebaixa um grau; teto B para quem so le arquivo publicado |
| Achado sem ancora vira `indicio_fraco` | Falha em G1-G3 vai para `indicios_fracos` |
| Quarentena em vez de descarte; nunca `rm` | Rechecagem e registro de mudanca da fonte (secao 6) |
| Hash antes de qualquer leitura | Secao 4, passo 1 |
| L3 nunca acima de C | Secao 1 |
| Ponto de parada antes de F4 (decisao humana) | Pre-registro antes dos dados; mudanca so por emenda |

## 3 Conflitos e resolucao proposta

C01 - Camada dos achados de urna.
O exemplo do `findings.jsonl` marca um achado sobre `vota.vsc` como `L2`. No
contrato, L2 e software de terceiro; `.vsc`, BU, RDV, log e a lista de hashes
sao saidas do sistema oficial. Resolucao: todo achado do Estudo 05 cujo objeto
seja artefato do TSE e `L1`. Ferramentas de terceiros (DataUrnas-BR, var-ue)
continuam L2 e entram como instrumento de conferencia (C10).

C02 - Tres ou quatro perguntas.
A missao fala em tres perguntas; a secao 12 e o schema usam quatro. Resolucao:
G1-G4 do contrato em todo o estudo.

C03 - Arvore de artefatos.
Plano: `artefatos/L2/secao-.../`. Contrato: `evidencias/artefatos/<classe>/<slug>/`.
Resolucao: o estudo trabalha em `data/estudo05/` (bruto, fora do Git) e grava
metadados em `estudos/05_integridade_artefatos/out/`. Um achado so entra em
`evidencias/artefatos/<classe>/<slug>/` quando promovido, com slug igual ao
`id` (`f-2026-0001`). O dossie unico continua sendo `evidencias/`.

C04 - Nome da classe residual.
`indicio_fraco` (plano) passa a `indicios_fracos` (contrato e validador).

C05 - Dados brutos no Git.
O `.gitignore` raiz cobre `*.logjez`, `*.bu`, `*.rdv` e `*.zip`, mas nao `.jez`,
`.vsc` nem `.dat`. Feito: `.gitignore` do estudo cobre `raw/`, `quarantine/`,
`artefatos/`, `*.jez`, `*.vsc`, `*.dat`, chaves privadas e sqlite.

C06 - Carimbo de tempo.
Plano: sha256 + sha512 + RFC 3161 + OpenTimestamps + Rekor + minisign.
Contrato v1.0: sha256 + RFC 3161 + Rekor. O plano e superconjunto e melhor.
Resolucao: contrato v1.1 com sha512 obrigatorio, OpenTimestamps como segunda
ancora independente da TSA e assinatura minisign do coletor (identifica quem
coletou; nao prova data). Exige nova versao registrada (decisao D2).

C07 - Anterioridade da lista de hashes (o ponto mais importante).
A primeira coleta do estudo e de novembro de 2026, depois do pleito. R03
(ETag muda entre coletas) so detecta alteracao posterior a nossa primeira
coleta; nao diz nada sobre o que estava publicado antes de 25/10/2026. A unica
ancora de anterioridade disponivel para F2 e de terceiro: capturas do Internet
Archive (e similares) anteriores a lacracao e ao pleito. Resolucao:
- nova regra R04: hash publicado hoje diferente do hash na captura anterior ao
  pleito, mesmo sistema e UF; severidade alta; ancora = captura arquivada
  recuperada e carimbada por nos;
- excecao explicita ao contrato: captura arquivada vale como ancora de
  anterioridade para R03/R04, nao como prova de integridade do conteudo;
- sem captura anterior ao pleito, R04 vai para `ausente` e entra em
  `achados_negativos.md` como superficie nao coberta.

C08 - Pre-registro.
Regra 1 do repositorio: protocolo antes dos dados. As regras R01-R20 (mais
R04), os limiares (15 sistemas, 27 UFs, 10 vezes a mediana, 50 GB) e o desenho
amostral de F3 precisam ser congelados com hash antes de abrir a pagina de
resumos digitais em F2. O numero 15 do art. 3o da Res. 23.673 precisa ser
conferido na fonte em F1; se estiver errado, a primeira execucao de F2 faz HALT
por construcao. Resolucao: F1 coleta e confere a resolucao; o pre-registro do
Estudo 05 e registrado entre F1 e F2.

C09 - Sobreposicao com o Estudo 03 (logs do 2o turno).
O Estudo 03 trava a abertura nacional dos logs do 2T 2026 ate a emenda 1.6
(dt* e poder). F3 baixa 175 logs do 2T e F4 baixaria todos. Resolucao: o
Estudo 05 nao calcula metricas de habilitacao, ritmo ou intervalo entre votos;
de `logjez.py` usa apenas o esquema de eventos e o instante de encerramento
(R20). Se F4 for aprovado antes da emenda 1.6, os logs baixados ficam selados
para o Estudo 03 (nenhuma metrica de habilitacao e calculada sobre eles).

C10 - Duplicacao de codigo.
`estudos/03_pianista/etapas/02_parser/logs_urna.py` ja le `.logjez` com py7zr e
mascara digitos (LGPD); `bu.py` ja decodifica o BU com asn1tools e foi validado
contra o log; `01_coleta/resultados_secoes.py` ja monta as URLs por secao em
`resultados.tse.jus.br`. Resolucao: `logjez.py`, `bu.py` e `catalog.py` do
Estudo 05 importam esses modulos e acrescentam apenas o que falta (sha512,
aux.json, imgbu, vsc). Biblioteca ASN.1: manter asn1tools, ja em uso, em vez de
pyasn1. Python 3.12 e compativel com a regra 3.11+.

C11 - Privacidade nos logs.
Logs trazem numeros de titulo de mesario. O fingerprint de log do Estudo 05
reutiliza `mascarar()` do Estudo 03 e nunca grava linha bruta em `out/`.

C12 - Teto estrutural (vale para o plano inteiro).
O `.vsc` assina arquivos de resultado; o log registra nome do pacote e
"SUCESSO", nao o hash do programa. R10-R20 testam autenticidade e coerencia do
que saiu da urna, nao a identidade do software que rodou nela (argumento 1 do
Estudo 04). Logo G4 e falso para todos eles e o teto e B, como o proprio plano
ja preve. F2 (R01/R04) e a unica fase que mira o software, mas so fecha G4 se
houver ligacao publica entre a lista de hashes e a urna (relatorios das
cerimonias, pedido LAI do INVENTARIO). Sem isso, F2 tambem tem teto B.

C13 - Build reproduzivel.
O `buildinfo.json` do plano garante a reprodutibilidade do nosso pipeline, nao
do software do TSE. O caminho para A do INVENTARIO (reproduzir o build de um
modulo e comparar com a lista oficial) nao esta no plano. Resolucao: F6
opcional, fora do escopo de dados publicos, condicionada ao acesso ao codigo de
fiscalizacao; registrada aqui para nao se perder.

C14 - Ambiente de execucao.
Neste ambiente de nuvem, `www.tse.jus.br` e `freetsa.org` estao bloqueados pelo
proxy (403, verificado em 2026-11-25); `resultados.tse.jus.br` responde. F1 nao
fecha o gate aqui. Resolucao: F1 roda na maquina do proponente ou apos
liberacao desses hosts no ambiente (decisao D3).

## 4 O que o Estudo 05 acrescenta aos outros

| Destino | Contribuicao |
|---------|--------------|
| `evidencias/INVENTARIO.md` | Primeira rota capaz de produzir itens L1; hoje o inventario so tem L2 |
| Itens B do inventario (DataUrnas-BR, var-ue) | Viram implementacoes independentes: rodar os dois e o Estudo 05 na mesma amostra de F3. Divergencia entre implementacoes e defeito de ferramenta, nao achado; concordancia fortalece G3 dos tres |
| Estudo 04 | As 20 secoes do Teste de Integridade em F3 alimentam a simulacao de poder de deteccao |
| Estudo 03 | `baseline_tipo.json` e R20 (deriva de relogio BU x log) servem de controle de qualidade do relogio usado nas metricas de intervalo |

## 5 Decisoes pendentes do proponente

| No | Decisao | Efeito |
|----|---------|--------|
| D1 | Aprovar C01-C14 | Gera `PLANO.md` v1 e o pre-registro do Estudo 05 |
| D2 | Aprovar contrato v1.1 (C06, C07) | Nova versao de `evidencias/AGENTS.md` registrada |
| D3 | Onde rodar F1 (maquina propria ou liberar `www.tse.jus.br` e TSA no ambiente) | Desbloqueia F1 |
| D4 | Orcamento de F4 (500 GB) | So depois de F2 e F3, conforme ponto de parada do plano |

## 6 Proximo passo tecnico

`parse_hashes_list` nao deve ser escrito antes de a pagina real ser coletada e
congelada em F1: o invariante 4 proibe adivinhar o esquema. O que pode ser
feito ja, sem a pagina: `rules.py` com R01-R04, `uf_diff.py` sobre uma
estrutura `HashEntry` neutra e as fixtures com divergencia plantada, mais o
`selftest` (a) e (d) do plano.

## 7 Emendas aprovadas (E1-E6)

Correspondencia com os ajustes, por conteudo: E1 -> C01 e C03; E2 -> C07;
E3 -> C10; E4 -> C09; E5 -> C06; E6 -> C12. Os demais ajustes (C02, C04,
C05, C08, C11, C13, C14) foram aprovados sem emenda.

### E1 - Divisao da camada L1 (substitui a resolucao de C01)

Artefato do TSE nao e, por si, software. L1 se divide em:

- L1.1 `software`: o que executa (rol dos sistemas do art. 3o da Res. 23.673,
  `vota_web_wasm.wasm`, codigo-fonte, binarios, firmwares).
- L1.2 `saida`: o que o software produz ou o TSE publica sobre ele (BU, RDV,
  `.vsc`, imgbu, logjez, aux.json, lista de hashes, pagina de lacracao).

Regras duras:
- L1.2 nunca passa de B.
- L1.1 sem binario em maos nunca passa de C.

DataUrnas-BR e var-ue continuam L2. A conferencia tripla (essas duas
ferramentas e o Estudo 05 sobre a mesma amostra de F3) e teste de ferramenta:
divergencia entre implementacoes e defeito a corrigir, nunca achado.

Todo achado do Estudo 05 descrito em C01 como L1 passa a L1.2, salvo se o
objeto for o proprio binario.

### E2 - Teto e ordem de busca da regra R04 (complementa C07)

Enunciado de R04: hash publicado hoje diferente do hash publicado antes de
25/10/2026, mesmo sistema e UF. Severidade alta.

Limite declarado na propria regra: R04 detecta alteracao da LISTA PUBLICADA,
nao do software na urna. Se o software da urna foi alterado e a lista nao, R04
nao ve. Esse texto acompanha todo achado R04 no relatorio.

Ordem obrigatoria de busca da ancora de anterioridade, antes de declarar
ausencia:
1. Internet Archive (Wayback Machine);
2. archive.today;
3. PDF ou DOC da lista com data de emissao no proprio documento;
4. data da cerimonia de assinatura digital e lacracao de 04/09/2026
   (a confirmar na fonte em F1), como referencia de conteudo esperado.

Sem ancora anterior a 25/10/2026 nos quatro passos:
- `anterioridade: nao_provada`;
- todo achado sobre a lista de hashes fica limitado a classe C.

O ETag da primeira coleta propria nao serve para anterioridade; serve apenas a
R03 (mudanca entre coletas proprias).

### E3 - Reuso do Estudo 03 com pino, adaptador e teste de contrato (complementa C10)

- O Estudo 05 importa o codigo do Estudo 03 por commit SHA fixo, lido do
  objeto Git daquele commit, nunca da arvore de trabalho.
- O acesso passa por um adaptador (`src/adapter_estudo03.py`), unico ponto de
  contato.
- Teste de contrato: hash do arquivo-fonte no commit fixado e lista de funcoes
  e assinaturas esperadas. Qualquer divergencia = HALT. Proibido contornar com
  `try/except`.
- Atualizar o pino exige nova linha em `DECISOES.md` e nova execucao do teste.

### E4 - Novo objeto da fase F4 (substitui a F4 do PLANO e complementa C09)

Com as metricas de habilitacao e ritmo excluidas (C09), cai a justificativa
original de F4 (anomalia de log, T3). F4 passa a ser:

- varredura nacional de ANCORAS: `.vsc`, aux.json e BU, 27 UFs, 2o turno
  completo e 1o turno parcial, SEM logs;
- R20 (encerramento BU x log) sai do Estudo 05 e migra para o Estudo 03;
- R19 (fingerprint de QR) passa a opcional;
- orcamento estimado: cerca de 50 GB (antes 500 GB);
- ponto de parada mantido: F2 e F3 sem achado => F4 nao comeca sem decisao
  humana.

A pergunta terciaria do PLANO passa a ser: "existe ancora (assinatura, aux.json
ou BU) que nao fecha em escala nacional?".

### E5 - Limite do contrato v1.1 (complementa C06)

O contrato v1.1 absorve somente mecanica de custodia:
- sha512 obrigatorio ao lado do sha256;
- OpenTimestamps como segunda ancora temporal, independente da TSA;
- assinatura minisign do coletor e gestao de chave (chave privada fora do Git,
  chave publica versionada, rotacao registrada);
- verificacao obrigatoria do TSR (`openssl ts -verify`) contra o certificado
  da TSA;
- troca de TSA registrada.

Metodologia (regras R, fases, amostras, tetos de achado) fica no `PLANO.md` e
nesta conciliacao. Todo manifesto grava `contrato: "v1.1"` (ou a versao
vigente na coleta).

### E6 - Teto B no cabecalho do relatorio (complementa C12)

`report.py` imprime, antes do primeiro achado de `dossie.md` e no topo de
`resumo.md`, o aviso:

> Nenhum achado deste relatorio fecha o elo entre o software lacrado e o
> software executado na urna. Teto de classe: B (L1.2) e C (L1.1 sem binario
> e achados sobre a lista sem anterioridade provada).

O lint de redacao falha se o aviso estiver ausente ou depois do primeiro
achado.

## 8 Risco registrado pelo proponente: ausencia da dimensao UF

Se a pagina de resumos digitais publicar apenas hash agregado por sistema, sem
dimensao UF, R01 e R02 perdem o objeto e F2 perde a pergunta primaria. Regra:
na primeira coleta, a primeira verificacao e estrutural (contar colunas e
detectar a dimensao UF), antes de qualquer extracao de hash. Sem dimensao UF:
HALT com codigo `F2_SEM_DIMENSAO_UF` e reabertura do desenho da fase 2 por
decisao humana. Somente R03 e R04 continuam aplicaveis nesse cenario.
