# Resposta ao parecer critico de 30/10/2026

Cada ponto do parecer (`PARECER_CRITICO_20261030.md`), o que foi verificado nos dados
e o que mudou. Relatorio revisado: `RELATORIO_PRELIMINAR_2T2026.md` (versao 2).

| Ponto | Verificacao nos dados | Situacao |
|---|---|---|
| 1 Escopo | Procedente. | Relatorio delimitado (secao 1.1): nao e auditoria abrangente; limite de identificabilidade nas conclusoes. |
| 2 Onze secoes x onze votos | O relatorio contava votos: o histograma por hora registra 11 votos apos 19h, em 11 secoes distintas (1 voto cada; BA, RJ, SP). O TSE informa 13. Decomposicao: 17h-18h 32.337 (TSE 32.399), 18h-19h 1.982 (1.981), apos 19h 11 (13). Votos apos 17h nas secoes com geracao do BU apos 19h: 4.722 (TSE 4.773). | Corrigido e decomposto; restam 2 votos apos 19h e 62 entre 17h e 18h a reconciliar evento por evento. |
| 3 Testes nao conclusivos | Procedente: fila p = 0,04 e governador apos 19h nao estimavel estavam mal resumidos. | Conclusoes reescritas com a formulacao sugerida; governador incluido na tabela. |
| 4 Zero em 2024 | Defeito confirmado: a extracao de 2024 foi feita antes do campo `votos_por_hora_log`; o campo vazio virava 0. | Codigo corrigido: sem histograma, o valor e "nao disponivel". Reextracao de 2024 pendente. |
| 5 Excluidos | 1.443 secoes: 1.419 log < BU (deficit de 153.492 votos no log), 21 campos ausentes, 3 temporais. Em 1.411 das 1.419 o log comeca apos 8h30 (compativel com substituicao de urna); 8 sem explicacao. | Inventario publicado em `resultados/inventario_secoes_incoerentes_2T2026.csv`; populacao de auditoria separada da estatistica. |
| 6 Fuso e relogio | Regra externa por UF aplicada aos 5.571 municipios: 12 divergencias, todas em regioes de excecao conhecidas (11 no oeste do AM, Fernando de Noronha). | Validacao incluida; lista legal do oeste do AM a conferir. Eventos temporais distinguidos (secao 3.3). Continua valendo que nada disso valida o relogio contra fonte externa. |
| 7 Materialidade | Procedente. | Formulacao restrita adotada (secao 4.7). |
| 8 Abstencao e invalidos | Identidade conferida com o detalhamento oficial: 14.098.232 = 9.316.747 + 2.960.239 + 1.821.246. A diferenca de 798 votos entre BU e oficial e explicada por 70 secoes do exterior ausentes dos arquivos transmitidos (comparecimento -831, todo na ZZ). | Secao 4.8 nova. Regressao ecologica simples inadequada (coeficientes fora de [0, 1]); inferencia ecologica fica para o Estudo 02. |
| 9 Referencias historicas | Os contrastes do Estudo 05 nao usam turno presidencial como referencia. O piloto TO do Estudo 03 usa o 2T 2022 em H1a e no diagnostico de poder. | Diretriz registrada em `protocolos/08_diretriz01_referencias_historicas_20261030.md`; componentes do Estudo 03 dependentes de 2022 rebaixados a descritivos; calibracao temporal por minuto pendente. |

## Observacao sobre a secao 9 (dados anteriores a urna eletronica)

Os dados abertos do TSE para 1990, 1992 e 1994 trazem resultados agregados, sem
registro de horario por voto. Pela propria diretriz, parametros como votos por minuto
nesses pleitos devem ser registrados como nao observados. Fontes possiveis para
horarios de abertura, encerramento e filas: atas e relatorios dos TREs, acervos
documentais e imprensa da epoca. Essa pesquisa documental ainda nao foi iniciada.
