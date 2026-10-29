# opianista

Analisando o Brasil: deteccao de anomalias de habilitacao e votacao nos registros
de urna do 2o turno das Eleicoes 2026 ("hipotese do mesario pianista").

## Objetivo

Testar, com desenho pre-registrado e reprodutivel, se os logs de urna do 2o turno
de 25/10/2026 apresentam assinaturas compativeis com insercao de votos por
membros da mesa receptora em periodos de baixo movimento, distinguindo-as de
explicacoes alternativas (prorrogacao do horario ate 19h, crise de transporte,
falha biometrica, urnas substituidas, fuso e relogio).

O projeto detecta e quantifica ANOMALIAS. Nao afirma fraude. Todo teste que
relacione anomalia a resultado eleitoral e executado de forma simetrica para
ambos os candidatos.

## Estrutura

```
prompts/                 Prompt agentico e comandos de execucao
docs/                    Fundamentacao metodologica e referencias
etapas/00_protocolo/     Pre-registro (hipoteses, limiares, regras de exclusao)
etapas/01_coleta/        Download e inventario de logs, BU e RDV (TSE)
etapas/02_parser/        Catalogo de mensagens e tabela de eventos
etapas/03_qualidade/     Reconciliacao log x BU, flags, classe de prorrogacao
etapas/04_descritivo/    Curvas de chegada, taxas de habilitacao, dt
etapas/05_inferencia/    Poder (Monte Carlo), DiD, modelo hierarquico, rajadas
etapas/06_red_team/      Explicacoes alternativas e curva de especificacoes
etapas/07_relatorio/     Relatorio final em ABNT
data/                    Dados brutos e intermediarios (fora do Git)
```

## Status

| Etapa | Agente      | Status   |
|-------|-------------|----------|
| 0     | Protocolo   | Pendente |
| 1     | Coleta      | Pendente |
| 2     | Parser      | Pendente |
| 3     | Qualidade   | Pendente |
| 4     | Descritivo  | Pendente |
| 5     | Inferencia  | Pendente |
| 6     | Red team    | Pendente |
| 7     | Relatorio   | Pendente |

Cada etapa termina em um GATE de aprovacao humana ("APROVADO ETAPA N").

## Regras do projeto

1. Hipoteses, limiares e regras de exclusao sao fixados na Etapa 0, antes de
   abrir os dados do 2o turno de 2026.
2. Nenhum dado, URL, mensagem de log ou resultado e presumido ou inventado.
3. Dados pessoais eventualmente presentes nos arquivos sao pseudonimizados na
   ingestao (LGPD). Nenhum mesario ou eleitor e identificado.
4. Filmagens e dados de telecomunicacoes estao fora do escopo; constam apenas
   como recomendacao de diligencia a autoridade competente, mediante ordem
   judicial.
5. Codigo em Python 3.11+, seeds fixas, scripts completos, sem emojis.

## Como executar

1. Carregar `prompts/prompt_agentico_analise_logs_2T2026.md` no agente.
2. Enviar o comando de `prompts/comando_inicio_piloto_TO.md`.
3. Revisar os artefatos de cada etapa e aprovar o GATE para prosseguir.

## Dados

Os arquivos brutos (logs, BU, RDV) nao sao versionados por volume e por
cautela com dados pessoais. As URLs exatas e os hashes SHA-256 de cada arquivo
ficam registrados em `etapas/01_coleta/fontes.md` e `inventario.csv`.
