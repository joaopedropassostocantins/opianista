# Registro de pre-registros e emendas

Regra: arquivos de pre-registro e emendas nao sao editados depois de
commitados. Correcoes entram como nova emenda. O historico do Git funciona como
carimbo de tempo publico complementar ao hash.

| Ordem | Arquivo | Data (UTC) | SHA-256 | Situacao |
|-------|---------|------------|---------|----------|
| 00 | 00_preregistro.md (gerado pelo agente) | 2026-10-26T04:13:03Z | a2d61a9569e5a3d96d3f80c2db5f2fb71fd73b95d20e68bfe97aace68bddbc3e | PENDENTE: arquivo ainda nao enviado ao repositorio |
| 00a | 00_prompt_preregistro_original_20261026.md | 2026-10-28 (arquivado) | 955b7f30535da7022c3f797fbaadc77aa471b06c5d569bcf42278607b60ef9ca | Prompt que originou o pre-registro 00 |
| 01 | 01_emenda_20261028_pianista.md | 2026-10-28 | aae751d0f5a7aa2a569dc795c3c65aad7918714bcb8e2be5958a4153983e4193 | Emenda: hipoteses de habilitacao sem biometria e rajadas |

## Pendencia critica

O hash do item 00 so tem valor se o arquivo `00_preregistro.md` original for
publicado aqui sem nenhuma alteracao, de modo que qualquer pessoa possa
conferir:

```
sha256sum protocolos/00_preregistro.md
```

O resultado deve ser identico ao hash da tabela. Se o arquivo original se
perdeu, registrar o fato nesta tabela; nao reconstrui-lo.

## Situacao da execucao do pre-registro 00

Em 26/10/2026, por volta de 01h12 (Brasilia), o agente consultou
https://dadosabertos.tse.jus.br e constatou que os Boletins de Urna por secao e
os arquivos de log do 2o turno de 2026 ainda nao estavam publicados. Nenhum
teste confirmatorio foi executado. Conclusao registrada: o desenho nao teve
dados para decidir; a hipotese permanece nao testada e o pre-registro continua
valido.


## Nova entrega registrada em 2026-10-29

| Ordem | Arquivo | Data (UTC) | SHA-256 | Situação |
|-------|---------|------------|---------|----------|
| 02 | `estudos/03_pianista/etapas/00_protocolo/02_protocolo_preregistro_etapa0_20261029.md` | 2026-10-29 | `160fca67437e45e4d269f728ee495202b60edddbb44582808269625be94ff05f` | Substituida pela versao 1.1 (entrada 03); arquivo mantido sem alteracao |
| 02a | `estudos/03_pianista/etapas/00_protocolo/02_checklist_etapa0_20261029.md` | 2026-10-29 | `807e87210dace19b42639dd38c56f389251cb85e2f122fd54484d78e4e8e6284` | Checklist da entrega 02 |
| 03 | `estudos/03_pianista/etapas/00_protocolo/03_protocolo_preregistro_etapa0_v1.1_20261029.md` | 2026-10-29 | `b75a5a502d1747518a238a36765a67c49afbecf454c8cccd29a4d9f81e71af2c` | GATE 0: versao 1.1, substitui a 02 para aprovacao; a 02 permanece inalterada |
| 04 | `protocolos/02_emenda_20261029_calibracao_piloto_TO.md` | 2026-10-29 | `34be261a7f2fa6d2e3ffb4efa9e58b07c152752463d76ff6be16c540e218c9d6` | Emenda 02: dt* = 60 s, poder, mapeamento validado; piloto TO; registrada antes da abertura do 2T 2026 |

A entrega 02 é adicional e não reconstitui nem substitui o arquivo histórico `00_preregistro.md` mencionado acima.

## Novo pré-registro do Estudo 05 — proposto para GATE E05-0

| Ordem | Arquivo | Data (UTC) | SHA-256 | Situação |
|---|---|---|---|---|
| 05 | `protocolos/04_estudo05_preregistro_v1_20261029.md` | 2026-10-29 | `9c6aaad29074c854982561a054d8bec726fb0cbb5820b311111ea55afc34e142` | Pre-registro E05-0, aprovado (ver Aprovacoes de GATE). Renumerado de 04 para 05 neste indice em 29/10/2026, porque a ordem 04 ja estava ocupada pela Emenda 02 do Estudo 03; o arquivo nao foi alterado. |

O SHA-256 foi computado por `sha256sum` no GitHub Actions (run 40820750825). Esta entrada não é declaração de aprovação do proponente e não supera o bloqueio D4. O texto já explicita o contato prévio com totais nacionais e contagens agregadas de horário, portanto a qualificação de "pré" limita-se aos microdados de seção ainda não abertos por este estudo. Após aprovação, qualquer modificação dependerá de emenda datada, sem sobrescrever a versão registrada.

## Aprovacoes de GATE

| Estudo | Gate | Versao aprovada | Data | Aprovado por |
|--------|------|-----------------|------|--------------|
| 03 Pianista | GATE 0 | Entrada 03 (protocolo v1.1, SHA-256 b75a5a50...e71af2c) | 2026-10-29 | Proponente (joaopedropassostocantins) |

A partir desta aprovacao, os parametros da versao 1.1 estao congelados. Qualquer
alteracao exige emenda nova, registrada antes da abertura dos dados do 2o turno
de 2026.

## Emenda 01 do Estudo 05 e aprovacao do GATE E05-0 (2026-10-29)

| Ordem | Arquivo | Data (UTC) | SHA-256 | Situacao |
|---|---|---|---|---|
| 06 | `protocolos/05_emenda01_estudo05_20261029.md` | 2026-10-29 | `eb5144a95b8b7c47498eff69813bb2a856b831d71772d74645400d22d0ce0861` | Emenda 01 ao E05-0: encerramento pelo ultimo voto, analise P-I condicional ao relogio da urna, verificacoes de coerencia, placebos e pedido LAI |

| Estudo | Gate | Versao aprovada | Data | Aprovado por |
|--------|------|-----------------|------|--------------|
| 05 Coortes de encerramento tardio | GATE E05-0 | Entrada 05 (SHA-256 9c6aaad2...afc34e142) com a emenda 01 (entrada 06) | 2026-10-29 | Proponente (joaopedropassostocantins), mensagem "Tudo aprovado" na sessao de trabalho |

Atualizacao de 29/10/2026: o item 1.6 do Estudo 03 foi cumprido para o piloto do
Tocantins (Emenda 02 do Estudo 03, entrada 04, incorporada com o PR #4). Para as demais
UFs, o Estudo 03 ainda depende de uma emenda nacional (dt* com todas as UFs). A liberacao
dos microdados do 2T 2026 para o Estudo 05 continua sendo decisao do proponente (D4 em
PLANEJAMENTO.md).

| Ordem | Arquivo | Data (UTC) | SHA-256 | Situacao |
|---|---|---|---|---|
| 07 | `protocolos/07_emenda02_estudo05_exposicao_TO_20261029.md` | 2026-10-29 | `55aff69832263cae05c15e4d33880eeda3d8fe09f04ec50e619fff358ccdaddf` | Emenda 02 ao E05-0: declara a exposicao aos microdados do Tocantins e exclui TO das analises confirmatorias do Estudo 05 |
