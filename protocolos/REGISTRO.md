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
| 02 | `estudos/03_pianista/etapas/00_protocolo/02_protocolo_preregistro_etapa0_20261029.md` | 2026-10-29 | `160fca67437e45e4d269f728ee495202b60edddbb44582808269625be94ff05f` | GATE 0: aguardando aprovação humana |
| 02a | `estudos/03_pianista/etapas/00_protocolo/02_checklist_etapa0_20261029.md` | 2026-10-29 | `807e87210dace19b42639dd38c56f389251cb85e2f122fd54484d78e4e8e6284` | Checklist da entrega 02 |

A entrega 02 é adicional e não reconstitui nem substitui o arquivo histórico `00_preregistro.md` mencionado acima.
