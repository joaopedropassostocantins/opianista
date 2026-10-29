# Auditoria transversal de erros e inconsistencias — O Pianista
Data: 29/10/2026. Escopo: inventario de main e da branch de PR #3, com leitura de codigo, documentos, workflows e metadados. Sem acesso a microdados de secao do segundo turno de 2026. **Nao e pericia externa ou reproducao de todas as execucoes.**

## Achados priorizados
| ID | Gravidade | Local | Evidencia e falha | Medida |
|---|---|---|---|---|
| A01 | CRITICA | `estudos/03_pianista/etapas/05_inferencia/pianista.py:39-45` | J0 09–15, J1 16–17, J2 17–17h49, J3 17h49–19h00: **nao cobre** 08–09, 15–16 e depois das 19h. Mesmo o intervalo de 15–16 nao tem janela. | Analisar o dia integral; J0–J3 apenas legado/estratos. |
| A02 | CRITICA | `pianista.py:319-376` | Diagnostico de poder injeta NB apenas em J1. Nao mede a deteccao de sinais distribuidos ao longo do dia. | Recalibrar injeções sintéticas em todas as horas antes de teste confirmatorio. |
| A03 | ALTA | `pianista.py:55-59` | Em 2026, todos os `DESC` sao convertidos em `NB_SEM`, regra generalizada a partir de validacao relatada em TO. | Tratar DESC como indeterminado ate validacao empirica por versao/UF e relatar sensibilidade. |
| A04 | ALTA | PR #3, arvore de 3bcd5384 | Branch intitulada migracao do site nao contem `site/`; versao anterior 48d9d6c incluiu aproximadamente 70 entradas em `site/`. | Restaurar arvore preservada em branch de reparo; revalidar build/CI. |
| A05 | ALTA | `estudos/03_pianista/README.md` | Status 'GATE 0 aprovado' e, adiante, 'aguardando aprovacao' no mesmo arquivo. | Corrigir status corrente, nao editar documento de preregistro. |
| A06 | ALTA | `PLANEJAMENTO.md` | Piloto real TO e dt* constam como realizados no topo, mas linhas finais dizem 'nenhuma execucao real' e 'dt* nao calculado'. | Marcar afirmacoes finais como superadas, com referencia aos registros. |
| A07 | ALTA | `estudos/05_simulacao_temporal/REVISAO_METODOLOGICA_20261029.md:42-50` | Cenários usam contagem de encerramentos administrativos para extrapolar coortes de **ultimo voto**. | Somente cenarios ilustrativos; nenhuma estimativa populacional com esses denominadores. |
| A08 | ALTA | `REVISAO_METODOLOGICA_20261029.md:55-57` | Afirma que efeito material seria necessariamente 'grosseiramente visivel' por comparacao local. | Detectabilidade depende de mecanismo, potencia e distribuicao; remover inferencia categorica de conclusoes atuais. |
| A09 | ALTA | `protocolos/05_emenda01_estudo05_20261029.md` | Recebimento central de BU e fonte de limite temporal superior, nao confirma hora do ultimo voto. | Separar rigorosamente 'observacao externa de recepcao' de 'observacao externa do ultimo voto'. |
| A10 | ALTA | `protocolos/REGISTRO.md`, `PLANEJAMENTO.md` e README | Aprovacoes variam entre marcos: gate TO do Estudo 03, E05-0 aprovado, D4 para outras UFs pendente; textos antigos parecem regras atuais. | Quadro unico de aplicabilidade por estudo e UF, com hash e data. |
| A11 | MEDIA | `pianista.py:419-420` | Soma das habilitacoes nas janelas J0–J3 e chamada de 'habilitacoes', apesar dos periodos nao cobertos. | Identificar como `habilitacoes_nas_janelas` e computar total integral separadamente. |
| A12 | ALTA | `estudos/03_pianista/prompts/comando_inicio_piloto_TO.md` | Parametros antigos de 2 p.p. e 1 rajada conflitam com v1.1 aprovado (5 p.p., 2 rajadas). | Rotular comando como historico/obsoleto; nao executa-lo como especificacao vigente. |
| A13 | MEDIA | `estudos/05_simulacao_temporal/PIPELINE_PLACEBOS.md` | Afirma nao haver execucao real de 2024, mas ha relatorio posterior de 629 secoes em Palmas. | Marcar como historico e apontar relatorio do placebo. |
| A14 | ALTA | `.github/workflows/etapa1_2t2026.yml` | Workflow para TO faz downloads/analises do 2T2026; sua aplicabilidade a outras UFs e a novos testes nao pode ser presumida. | Revisar gates, autorizacao por UF, destino dos artefatos e publicacao antes de nova execucao. |
| A15 | ALTA | codigo de log e `eventos.py` | Dados normalizados tem segundos desde meia-noite, sem hora do ultimo voto por secao. | Nao equiparar fim da serie de habilitacoes a ultimo voto; reconciliar com log completo. |
| A16 | ALTA | `RESULTADO_PLACEBO_2T2024_TO_20261029.md` | Das 629 secoes, 629 fecharam administrativamente apos 17h, mas so 112 registram ultimo voto apos 17h; zero apos 17h10. | Usar ultimo voto com ressalva de relogio; Palmas nao calibra extremos. |
| A17 | ALTA | estudos 2022 externos | Divergencias entre key_findings.txt e resultados_forense.json; pesos heuristicos rotulados posteriors. | Reproducao e revisao estatistica antes de reutilizacao. |
| A18 | ALTA | protocolo historico / politica de exposicao | Houve exposicao parcial declarada e piloto TO no escopo antigo. | Nao reclassificar analises reconfiguradas apos exposicao como confirmatorias para TO. |

## Abrangencia e limite
Auditoria de referencias e logica, nao execucao de todas as rotinas. Nesta revisao nao foram abertos BU, RDV, logs ou resultados por secao do 2T2026. A presenca de workflow e relatorios de piloto foi constatada por nomes, status e documentos de governanca; seus microdados/saidas nao foram examinados. O codigo reconstruido do simulador web nao equivale ao binario eleitoral lacrado.

## Correcoes sem reescrever protocolo congelado
1. Adicionar `PROPOSTA_EMENDA_ESCOPO_INTEGRAL_20261029.md` para revisao humana.
2. Criar `dia_integral.py` exploratorio e testes sinteticos, com 2T2026 bloqueado.
3. Atualizar README e planejamento **na branch de reparo**, mantendo logs documentais antigos intactos.
4. Restaurar `site/` do ultimo snapshot integro localizado (commit 48d9d6c), sujeito a build e revisao.
5. Adicionar conclusoes revisadas e apontar documentos historicos com ressalvas, sem alterar hashes existentes.

## Nao executar
Nao executar ferramentas de ingestao do 2T2026; nao tomar o TO exposto como confirmacao prospectiva de novas hipoteses; nao incluir dados brutos nos commits.
