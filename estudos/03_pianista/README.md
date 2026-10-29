# Estudo 03 - Hipotese do mesario pianista

## Pergunta

Os logs de urna do 2o turno de 2026 mostram assinaturas compativeis com
insercao de votos por membros da mesa receptora em periodos de baixo movimento
(excesso de habilitacoes por ano de nascimento, rajadas de votos com intervalo
fisicamente implausivel, concentracao por operador), alem do explicado por
fila, prorrogacao, falha biometrica e perfil do eleitorado?

## Protocolo

Emenda 01 ao pre-registro 00: `protocolos/01_emenda_20261028_pianista.md`.
Especificacao completa em `prompts/prompt_agentico_analise_logs_2T2026.md`.

## Estrutura

```
prompts/                     prompt agentico e comando do piloto TO
fundamentacao_metodologica.md
etapas/00_protocolo ... 07_relatorio
```

## Status

| Etapa | Agente      | Status   |
|-------|-------------|----------|
| 0     | Protocolo   | Aprovado em 29/10/2026 (versao 1.1) |
| 1     | Coleta      | Piloto TO concluido (1T/2T 2026, 1T/2T 2022) |
| 2     | Parser      | Concluido; validado contra o BU |
| 3     | Qualidade   | Pendente |
| 4     | Descritivo  | Pendente |
| 5     | Inferencia  | Piloto TO concluido: hipoteses nao sustentadas (ver resultados_piloto_TO) |
| 6     | Red team    | Pendente |
| 7     | Relatorio   | Pendente |

O parser de logs (Etapa 2) e compartilhado com o Estudo 01.


## Nova entrega da Etapa 0 — 2026-10-29

Foi acrescentado o protocolo produzido nesta execução em:

- `etapas/00_protocolo/02_protocolo_preregistro_etapa0_20261029.md`
- `etapas/00_protocolo/02_checklist_etapa0_20261029.md`

Esta entrega é um artefato adicional e não substitui o pré-registro histórico nem a Emenda 01. O documento permanece em **GATE 0**, aguardando aprovação humana explícita. Nenhum dado-alvo foi aberto nesta execução.

## Revisao de escopo integral (29/10/2026)

A hipotese do mesario pianista se aplica a **todo o periodo de funcionamento da secao**, nao apenas 16h–19h ou 17h–19h. A implementacao historica J0–J3 tem lacunas 08h–09h, 15h–16h e apos 19h e seu diagnostico de poder testa insercoes sinteticas apenas na J1. Nao apresentar conclusoes destas janelas como conclusoes sobre todo o dia.

A proposta para nova emenda, **ainda nao aprovada**, esta em [PROPOSTA_EMENDA_ESCOPO_INTEGRAL_20261029.md](PROPOSTA_EMENDA_ESCOPO_INTEGRAL_20261029.md). O arquivo [dia_integral.py](etapas/05_inferencia/dia_integral.py) e um diagnostico exploratorio, sem acesso a 2T2026. Relatorio de [auditoria transversal](../../auditoria/AUDITORIA_TRANSVERSAL_20261029.md) e [conclusoes revisadas](../../relatorios/CONCLUSOES_REVISADAS_20261029.md).

**Governanca atual:** GATE 0 consta como aprovado no `protocolos/REGISTRO.md`; Emenda 02 registra piloto autorizado de TO, sem validar a nova especificacao integral. Para outras UFs e novas hipoteses, verificar aprovacoes especificas antes de qualquer acesso. O trecho historico que afirmava 'GATE 0 aguardando aprovacao' esta superado; nao alterar os pre-registros originais.
