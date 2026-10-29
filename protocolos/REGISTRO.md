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

## Aprovacoes de GATE

| Estudo | Gate | Versao aprovada | Data | Aprovado por |
|--------|------|-----------------|------|--------------|
| 03 Pianista | GATE 0 | Entrada 03 (protocolo v1.1, SHA-256 b75a5a50...e71af2c) | 2026-10-29 | Proponente (joaopedropassostocantins) |

A partir desta aprovacao, os parametros da versao 1.1 estao congelados. Qualquer
alteracao exige emenda nova, registrada antes da abertura dos dados do 2o turno
de 2026.
