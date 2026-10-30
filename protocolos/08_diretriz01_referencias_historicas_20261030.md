# Diretriz metodologica 01 - referencias historicas independentes

Data: 30/10/2026. Determinacao do proponente (joaopedropassostocantins),
registrada a partir do parecer critico de 30/10/2026
(`estudos/05_simulacao_temporal/PARECER_CRITICO_20261030.md`, secao 9). Aplica-se a
todos os estudos do projeto a partir desta data. Nao altera arquivos ja registrados;
os efeitos sobre resultados anteriores estao na secao 5.

## 1 Pressuposto investigativo

O projeto adota, como hipotese de trabalho e nao como constatacao, a possibilidade de
comprometimento do sistema eletronico de votacao originado na cadeia de
desenvolvimento, inclusive desde sua implantacao. Consequencia: dados cuja
integridade e objeto da investigacao nao podem servir de referencia de normalidade.

## 2 Vedacao

Fica vedado usar segundos turnos de eleicoes presidenciais brasileiras como parametro
de calibracao da normalidade temporal da votacao, inclusive: eleitores por minuto ou
por hora; intervalos entre habilitacoes e votos; distribuicao temporal do
comparecimento; horarios de reducao do fluxo; frequencia de secoes sem movimento;
velocidade operacional dos mesarios; frequencia de rajadas de habilitacoes; horarios
de encerramento e filas; e estimativas probabilisticas de normalidade baseadas nesses
padroes. Dados presidenciais historicos podem ser usados como objeto de investigacao
ou em comparacoes descritivas, identificados como pertencentes a populacao
potencialmente afetada.

## 3 Hierarquia das referencias

1. Grupo A, prioridade 1: eleicoes estaduais e municipais anteriores a urna
   eletronica (1990, 1992, 1994 e outras com documentacao adequada). Parametros nao
   documentados (por exemplo, votos por minuto) sao registrados como **nao
   observados**, nunca estimados ficticiamente.
2. Grupo B, prioridade 2: segundos turnos municipais (2000 a 2024); prioridade 3:
   segundos turnos estaduais. Ambos eletronicos, portanto nao automaticamente
   independentes da hipotese. Segundo turno estadual simultaneo ao presidencial
   (mesma urna) e apenas complementar.
3. Grupo C: populacao investigada (eleicoes presidenciais eletronicas, em especial o
   2T 2026). Nao pode definir parametros dos grupos A e B.

Resultados apresentados separadamente por grupo, com analise de sensibilidade.

## 4 Programa de trabalho exigido

Modelo de intensidade por minuto por secao, lambda_s(t) = E[N_s(t, t+1) | X_s],
calibrado nos grupos A e B; analise da jornada integral (nao so apos 17h); periodos
sem movimento (5, 10, 15, 30 e 60 min); sequencias excepcionalmente rapidas;
habilitacoes sem biometria em baixo fluxo; relacao entre ultimo voto, encerramento e
emissao do BU; poder estatistico para mecanismos distribuidos ao longo do dia;
controles negativos e sensibilidade. Diferencas estatisticas nao sao interpretadas
como fraude sem exame de explicacoes alternativas.

## 5 Efeitos sobre resultados ja produzidos

1. Estudo 05 (relatorio preliminar de 29/10/2026): os contrastes sao internos ao
   2T 2026 (secoes do mesmo local) e o placebo usa o 2T municipal de 2024; nenhum
   parametro foi calibrado em 2T presidencial. Permanecem validos, com o escopo
   restrito descrito no relatorio revisado.
2. Estudo 03, piloto TO: H1a-J1 compara o 2T 2026 com o 2T 2022 (presidencial) como
   referencia, e o diagnostico de poder usou 2022. Pela diretriz, esses componentes
   passam a **descritivos**; a conclusao de nulo de H1a nao pode ser apresentada como
   teste contra referencia independente. H1b e H1d, que comparam turnos e secoes do
   proprio 2026, devem ser reavaliados quanto ao uso de 2022 na calibracao.
3. Fica pendente a calibracao temporal nacional com os grupos A e B.
