# CONTRATO DE EVIDENCIA - software de manipulacao de resultados, 2o turno 2026

Versao: 1.1
Data: 2026-11-25
Versao anterior: `versoes/AGENTS_v1.0.md` (SHA-256 4f2e5002...ec2f62)
Escopo: toda coleta, classificacao e publicacao de evidencia sob `evidencias/`.
Este arquivo vale como instrucao para pessoas e para agentes de IA que operem
neste diretorio. Alteracoes entram como nova versao registrada em
`protocolos/REGISTRO.md`, nunca por edicao silenciosa.

Mudancas da v1.1 (decisao D2 e emenda E5 do Estudo 05): sha512 obrigatorio,
OpenTimestamps, assinatura minisign do coletor e gestao de chave, verificacao
obrigatoria do TSR, registro de troca de TSA, campo `contrato` no manifesto.
Por necessidade de classificacao, a definicao de L1 foi dividida em L1.1 e
L1.2 (emenda E1). Metodologia de estudos nao pertence a este contrato.

## 0 Premissa

Concreto, consistente e verificavel sao condicoes necessarias, nao
suficientes. O artefato tambem precisa pertencer a classe que MANIPULA (nao a
que apenas le) e fechar a cadeia urna -> totalizacao. Build reproduzivel de
artefato irrelevante continua irrelevante.

O pleito ocorreu em 25/10/2026. Data de commit NAO prova data:
`GIT_COMMITTER_DATE` e forjavel. Para um achado valer como A, a anterioridade
tem de vir de terceiro (token RFC 3161 com `genTime` anterior a 25/10/2026 e
entrada em log de transparencia), e o achado precisa explicar como sobreviveu
ao pleito (ex.: alteracao aplicada antes da lacracao e ainda presente), nao
ser descoberta retroativa sem lastro temporal.

## 1 Camadas (campo obrigatorio `camada` no manifesto)

- L1.1 `software`: software que o TSE usa e que pode estar alterado (VOTA,
  GAP, GEDAI, lacracao, assinatura, totalizacao, firmwares,
  `vota_web_wasm.wasm`, codigo-fonte).
- L1.2 `saida`: o que esse software produz ou o que o TSE publica sobre ele
  (BU, RDV, `.vsc`, imgbu, logjez, aux.json, lista de hashes, pagina de
  lacracao).
- L2: software de terceiro que le, simula ou altera artefato eleitoral.
- L3: software hipotetico, descrito em texto, sem existencia demonstrada.

Tetos por camada:
- L1.2 nunca passa de B.
- L1.1 sem binario em maos (`binario_em_maos: false`) nunca passa de C.
- L3 nunca e promovido a A ou B; teto = C.

## 2 Gate das 4 perguntas (todas obrigatorias, binarias)

| Gate | Nome | Criterio | Consequencia da falha |
|------|------|----------|-----------------------|
| G1 | CONCRETO | Existe arquivo? Se a evidencia e texto, classe maxima = C. | indicios_fracos |
| G2 | CONSISTENTE | Compativel com a arquitetura conhecida? Se nao se sabe qual arquivo toca, falha. | indicios_fracos |
| G3 | VERIFICAVEL | Terceiro reproduz ou confere sem o autor? Hash publicado + carimbo de terceiro. | indicios_fracos |
| G4 | CADEIA | Fecha o elo urna -> totalizacao? Se so le BU/RDV publicado, teto = B. | rebaixa um grau |

Falha em G1, G2 ou G3: o item vai para `artefatos/indicios_fracos/`, com a
razao registrada. Falha em G4: rebaixa um grau, nao descarta.

## 3 Classes

- A: G1-G4 aprovados, build reproduzido (secao 5), carimbo de terceiro anterior
  ao pleito ou sobrevivencia documentada.
- B: G1-G3 aprovados; G4 falha ou build nao reproduz.
- C: evidencia textual ou L3; sem arquivo executavel ou sem verificacao.
- D: print, video ou alegacao sem artefato.

## 4 Carimbo de tempo (obrigatorio em toda coleta)

Executar `scripts/coletar.sh <arquivo> <classe> <slug> <url_fonte>`, que faz:

1. `sha256sum` e `sha512sum` do arquivo bruto, gravados antes de qualquer
   outra acao.
2. Token RFC 3161 sobre o digest (TSA primaria: freetsa.org) e verificacao
   obrigatoria com `openssl ts -verify` contra o certificado da TSA
   (`tsa.crt` e `cacert.pem` da propria TSA, guardados com seus hashes).
   Token que nao verifica conta como ausente.
3. Entrada no log de transparencia Sigstore Rekor (`rekor-cli upload`),
   se o binario estiver instalado; o retorno traz indice e hora de inclusao.
4. Gravar AMBOS. O Rekor v2 nao carimba sozinho; a hora vem da TSA. Um sem o
   outro nao prova nada.
4a. OpenTimestamps (`ots stamp`) como segunda ancora temporal, independente da
   TSA. O `.ots` e completado depois (`ots upgrade`), quando a transacao
   Bitcoin confirma.
4b. Assinatura minisign do coletor sobre o arquivo `.sha512`. Identifica quem
   coletou; nao prova data. Chave privada fora do Git; chave publica
   versionada em `keys/`; rotacao de chave registrada em `DECISOES.md` do
   estudo ou neste contrato.
4c. Situacao do carimbo gravada em `stamp.status`: `completo` (TSR
   verificado + Rekor) ou `incompleto` (lista do que falta). Coleta com
   carimbo incompleto e mantida, nunca descartada, e nao passa de C ate ser
   completada.
4d. Troca de TSA (indisponibilidade, custo, confiabilidade) registrada no
   manifesto (`carimbo.tsa`) e em `DECISOES.md`.
5. Limite declarado: a TSA prova que o digest existia ate `genTime` +
   `accuracy`, nao o instante exato; o campo `accuracy` costuma vir omitido.
   Registrar isso no manifesto (`carimbo.accuracy_ausente`).
6. freetsa e TSA de custo zero; para credibilidade, segunda TSA (comercial
   ou ICP-Brasil) sobre o mesmo digest.
7. Data de commit so conta acompanhada de (2) + (3). Commit "de 12/10/2026"
   sozinho = C.

## 5 Build reproduzivel (so para A)

- `SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)`, `TZ=UTC`, `LC_ALL=C.UTF-8`.
- Toolchain e dependencias pinados por digest (`FROM image@sha256:...`,
  lockfile commitado).
- Sem rede durante o build.
- Duas builds em maquinas distintas -> `diffoscope` entre os artefatos ->
  zero diferenca semantica.
- Publicar `.buildinfo` ou receita equivalente e o comando exato.
- Build que nao reproduz -> classe B no maximo, com a divergencia registrada.

## 6 Arquivamento

- WARC via ArchiveBox auto-hospedado, com SHA-256 do WARC no manifesto.
- Arquivo bruto publicado em IPFS ou anexo de release (binario, nunca print).
  Arquivos brutos NAO entram no Git (regra 3 do README do repositorio);
  em `artefatos/<classe>/<slug>/` ficam metadados, hashes e carimbos.
- Wayback/archive.today como redundancia, nao como prova principal.
- Rechecar ETag/MD5 da fonte apos 24 h e apos 7 dias; registrar se mudou
  (`scripts/rechecar.sh`).
- Coleta dependente de login (foruns fechados): marcar
  `acesso: "pago/fechado"` e guardar a sessao fora do repositorio.

## 7 Rejeicao automatica

- Print como prova primaria.
- "Fonte confiavel disse" sem link.
- Analise estatistica sem artefato de software.
- Reincidencia de tese de 2018/2022 sem artefato novo datado em 2025-2026.
- Hash gerado por quem nao e o autor nem repositorio publico.

## 8 Estrutura por item

```
artefatos/<classe>/<slug>/
  manifesto.json      (schema: manifesto.schema.json; campo contrato obrigatorio)
  <arquivo>.sha256
  <arquivo>.sha512
  <arquivo>.sha512.minisig  (assinatura do coletor)
  <arquivo>.tsq       (requisicao RFC 3161)
  <arquivo>.tsr       (resposta RFC 3161)
  <arquivo>.tsr.verify      (saida de openssl ts -verify)
  <arquivo>.ots       (OpenTimestamps)
  stamp.status        (completo | incompleto: <faltas>)
  rekor.json          (quando houver)
  fonte.url
  arquivado.url
  coleta.utc
  autor.md
  gate.md             (G1-G4 com justificativa)
  bruto/              (ignorado pelo Git)
```

Validar antes de cada commit: `python3 -I scripts/validar_manifesto.py artefatos`.

## 9 Regras herdadas do repositorio

Valem integralmente as regras do README raiz: nada presumido, nenhum dado
pessoal (LGPD), simetria entre candidatos, anomalia nao e prova de crime.
