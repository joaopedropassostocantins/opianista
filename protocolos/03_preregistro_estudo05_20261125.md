# Pre-registro 03 - Estudo 05, integridade dos artefatos publicos do TSE

Data: 2026-11-25
Aprovacao: proponente, decisao D1 (CONCILIACAO.md, secao 7), condicionada a
redacao das emendas E1-E6, cumprida nesta data.

## 1 Documentos e codigo congelados

| Arquivo | SHA-256 |
|---------|---------|
| `estudos/05_integridade_artefatos/PLANO.md` (v0) | 3eeb308292e2a0622920a90d1b35f2fbe7358b408e996f96bfe98babb1ce3586 |
| `estudos/05_integridade_artefatos/CONCILIACAO.md` (C01-C14, E1-E6) | 14685f7e1836af83b4b281f9dd42e59902eb84c0552452c0eea9d72cd6d421c1 |
| `estudos/05_integridade_artefatos/src/contrato_pagina.py` (premissas P1-P4) | a1cd4d1c6fdb26a66c35b42dc0cdcd0a491da3fc254823ffe9179868d4370fbd |
| `estudos/05_integridade_artefatos/src/regras_lista.py` (R01-R04) | c92ea2698751b434744b28dd0e87f80f4671f35a4e1c488b4713183a5e762c02 |
| `estudos/05_integridade_artefatos/src/modelos.py` | 1d3a1f004628931d761ce42f4c5247f9367d63385e3a50466a2498887aeb9ccf |
| `estudos/05_integridade_artefatos/src/adapter_estudo03.py` (pino 6adf40d) | fe400831869dac7b62ec75bcfe662c20d16f5cc7cba19ec01ea8cdb2cde51d04 |
| `estudos/05_integridade_artefatos/src/selftest.py` | 8e5149ff750ddd26d2411f839a073221e92af0dbeed8d8d905e0e12139722104 |
| `evidencias/AGENTS.md` (contrato v1.1) | 2c7359ff65ff39ce5d7addf6f22e008c552f7187a8bfd6a4696cd39bc4ce5251 |

Selftest verde em 2026-11-25 (12 casos, fixtures sinteticas).

## 2 Declaracao de exposicao previa

Ate o registro deste documento, nenhuma pagina de resumos digitais, de
lacracao ou de hashes do TSE referente a 2026 foi aberta, baixada ou lida pelo
assistente ou pelo pipeline do estudo: `www.tse.jus.br` estava bloqueado no
ambiente (verificado em 2026-11-25) e as fixtures sao sinteticas (SIS01..SIS15,
hashes ficticios). O proponente declara a propria exposicao, se houver, em
linha separada de `DECISOES.md`.

## 3 Premissas que a F1 pode derrubar (HALT, nunca ajuste silencioso)

- P1: 15 sistemas no art. 3o da Res. 23.673. A lista de nomes da secao F2 do
  PLANO tem 16 itens (inclui "firmwares"); a contagem real decide.
- P2: 27 UFs. Linha do exterior (ZZ) dispara HALT ate decisao humana.
- P3: hash em hexadecimal de 64 ou 128 caracteres.
- P4: colunas identificaveis como sistema, UF e hash. Sem dimensao UF:
  HALT F2_SEM_DIMENSAO_UF e reabertura do desenho da F2.

Qualquer mudanca em P1-P4 ou em R01-R04 entra como emenda numerada, registrada
antes da execucao da F2 sobre a pagina real.

## 4 Ordem de execucao a partir deste registro

1. F1: coletar e carimbar as paginas L1 (contrato v1.1).
2. Verificacao estrutural da pagina de hashes (colunas, dimensao UF) antes de
   qualquer extracao de hash.
3. F2 somente se P1-P4 se sustentarem.
