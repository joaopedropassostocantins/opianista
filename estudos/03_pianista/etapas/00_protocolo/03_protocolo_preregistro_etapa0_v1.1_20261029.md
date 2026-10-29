# Protocolo de pré-registro - Etapa 0 - versão 1.1

**Estudo:** 03 - Hipótese do mesário pianista
**Versão:** 1.1 - rascunho para aprovação humana explícita (GATE 0)
**Data de redação:** 29/10/2026
**Substitui:** versão 1.0 (`02_protocolo_preregistro_etapa0_20261029.md`, SHA-256 `160fca67437e45e4d269f728ee495202b60edddbb44582808269625be94ff05f`), que permanece no repositório sem alteração.
**Vincula-se a:** pré-registro 00 (SHA-256 `a2d61a9569e5a3d96d3f80c2db5f2fb71fd73b95d20e68bfe97aace68bddbc3e`) e Emenda 01 (`protocolos/01_emenda_20261028_pianista.md`).
**Status:** não aprovado. Nenhum dado do 2o turno de 2026 foi aberto para esta etapa.

## 0 Alterações em relação à versão 1.0

| No | Ponto da v1.0 | Correção na v1.1 | Seção |
|----|---------------|------------------|-------|
| 1 | Janela única 17h00-19h00 | Janelas J2 (17h00-17h48) e J3 (17h49-19h00), alinhadas ao pré-registro 00 (S8) e à Emenda 01 | 2 |
| 2 | Sem declaração de exposição prévia | Declaração incluída, com consequências obrigatórias | 3 |
| 3 | H1a-H1c tratadas como confirmatórias principais | Família secundária, subordinada ao teste primário do pré-registro 00 | 4 |
| 4 | Comparador e modelo de H1a e teste de H1b em aberto | Estimador de tripla diferença para H1a e teste por simulação condicional para H1b, fixados agora | 6.1, 6.2 |
| 5 | H1c redefinida como "assinatura conjunta" | H1c restaurada como associação simétrica com a votação; a assinatura conjunta passa a H1d | 6.3, 6.4 |
| 6 | Efeito mínimo de 5 p.p. e 2 rajadas sem registro de decisão | Valores mantidos por decisão explícita, com diagnóstico de poder obrigatório antes da abertura | 2, 9 |

Tudo o que a v1.0 estabelece e não é alterado acima permanece válido, em especial: as definições da Resolução TSE no 23.759/2026 para os fluxos de habilitação (v1.0, seção 3.1), a recusa em presumir a leitura da digital do mesário em todo fluxo sem biometria, a exclusão de Benford como teste confirmatório, as regras de privacidade (v1.0, seção 12) e a cautela quanto à licença dos logs do 2o turno de 2026.

## 1 Pergunta de pesquisa

Nas janelas finais de votação de 25/10/2026, as seções eleitorais apresentam, além do esperado pela própria seção no 1o turno, pelo padrão da mesma seção no início do dia e pela variação observada no 2o turno de 2022, (i) excesso de habilitações sem biometria e (ii) excesso de rajadas de habilitações sem biometria com intervalos abaixo do tempo mínimo operacional, e esse excesso se associa à votação de algum candidato?

A análise não pretende provar fraude, autoria, intenção ou causalidade. Um resultado positivo será tratado como anomalia estatística compatível com a hipótese operacional, sujeita a explicações alternativas, validação documental e investigação pela autoridade competente.

## 2 Parâmetros fixados

- **ESCOPO_UF:** todas as UFs.
- **AMOSTRA:** censo das seções elegíveis com logs disponíveis.
- **COMPARADORES:** 1o turno de 2026 (mesma seção); 2o turno de 2022 (placebo temporal); 2o turno de 2018 somente se os logs forem disponíveis e comparáveis.
- **ALFA:** 0,05, com controle de FDR (Benjamini-Hochberg, q = 0,05) dentro da família definida na seção 4.
- **EFEITO_MINIMO:** 5 pontos percentuais no excesso da taxa de habilitação sem biometria; 2 rajadas por seção e janela. Valores mantidos da v1.0 por decisão do proponente em 29/10/2026. O diagnóstico de poder da seção 9 informará qual tamanho de inserção esses limiares conseguem detectar; esse diagnóstico não autoriza alterar os limiares depois de aberto o 2o turno.
- **JANELAS:**
  - J0 (referência): 09h00:00-14h59:59;
  - J1: 16h00:00-16h59:59;
  - J2: 17h00:00-17h48:59 (fila regular após o horário);
  - J3: 17h49:00-19h00:00 (após a comunicação do TSE aos TREs, às 17h49, da decisão na Rcl 101.673/BA).
- **HORÁRIO:** horário de Brasília. Timestamps de seções em outros fusos serão convertidos pela regra documentada no log da urna ou no dicionário do TSE; se a conversão não for determinável, a seção é sinalizada e excluída da análise de janelas.
- **SEED:** 20261025.

Fato de contexto, sem valor de evidência para as hipóteses: o TSE informou 34.393 votos registrados após 17h no território nacional, número muito inferior à margem de 4.430.191 votos. Isso limita o impacto possível de J2 e J3 sobre o resultado, mas não o de J1.

## 3 Declaração de exposição prévia aos dados

Antes da Emenda 01, o proponente examinou uma amostra de cerca de 2,1% das seções do 2o turno de 2026 e observou 15,0% de habilitações sem biometria após 17h contra 10,6% antes; 553 votos após 17h; e diferença pareada de 0,0 p.p. (IC95% de -2,0 a +2,1) no voto em Lula entre seções sinalizadas e controles da mesma zona.

Consequências obrigatórias:

1. Essa observação motivou parcialmente H1a e não pode servir de evidência confirmatória de H1a.
2. Se as seções da amostra puderem ser reconstituídas, todas as análises confirmatórias serão reportadas com e sem elas. Se não puderem, isso será declarado como limitação.
3. A diferença antes/depois das 17h, isoladamente, é compatível com explicações não fraudulentas (perfil dos eleitores tardios, fila, pressão para liberar por ano de nascimento). Por isso o estimador de H1a usa o mesmo período do 1o turno e o início do dia da própria seção como controles.

## 4 Hierarquia de testes

1. **Primário (inalterado):** o teste do pré-registro 00 (beta de V17 sobre dL, com efeitos fixos de local de votação) continua sendo o único teste confirmatório primário do projeto.
2. **Família secundária S-PIANISTA (este protocolo):** 9 testes, com Benjamini-Hochberg q = 0,05 dentro da família:
   - H1a-J1, H1a-J2, H1a-J3;
   - H1b-J1, H1b-J2, H1b-J3;
   - H1c-Lula, H1c-Flávio;
   - H1d.
3. **Exploratório:** análises por UF, por modelo de urna, limiares alternativos, outras janelas e qualquer análise não listada acima. Rotuladas como exploratórias, com FDR próprio, sem linguagem confirmatória.

## 5 Definições operacionais

### 5.1 Habilitação e taxa sem biometria

Mantida a definição da v1.0 (seção 3.1). Para seção s, turno t e janela w:

r(s,t,w) = N_NB(s,t,w) / N_H(s,t,w)

onde N_NB é o número de habilitações sem biometria e N_H o total de habilitações. Se o log não separar ausência de biometria e biometria não reconhecida, usa-se a categoria agregada e a limitação é reportada. Taxa com N_H = 0 é não estimável, não zero.

### 5.2 Limiar dt*

dt* é o percentil 1 dos intervalos entre habilitações biométricas consecutivas na janela J0 do 1o turno de 2026, agregando todas as seções elegíveis do país, calculado antes de qualquer acesso ao 2o turno de 2026.

Regras fixadas:

- intervalo calculado apenas entre habilitações consecutivas da mesma seção, ambas biométricas e ambas válidas;
- método de quantil: interpolação linear entre estatísticas de ordem (tipo 7 de Hyndman e Fan, padrão de `numpy.quantile`);
- empates: dt = 0 é mantido; eventos com timestamp idêntico conservam a ordem em que aparecem no log;
- mínimo: o cálculo exige pelo menos 100.000 intervalos válidos; abaixo disso, dt* fica não estimado e H1b não é executada;
- robustez (exploratória): dt* por UF e, se o log identificar o modelo de urna, por modelo.

O valor de dt*, o número de intervalos e o hash do arquivo de saída são registrados em emenda antes da abertura do 2o turno.

### 5.3 Rajada sem biometria

Uma rajada sem biometria é uma sequência de pelo menos 3 habilitações consecutivas da mesma seção, todas sem biometria, com todos os intervalos internos menores ou iguais a dt*. Rajadas não se sobrepõem: uma nova rajada só começa depois de um intervalo maior que dt* ou de uma habilitação biométrica. K(s,t,w) é o número de rajadas da seção s no turno t e janela w.

Rajadas compostas apenas de habilitações biométricas são registradas de forma descritiva, mas não entram em H1b, porque o fluxo biométrico não é o mecanismo da hipótese.

### 5.4 Índice de anomalia

Para cada seção, A(s) é a média de dois componentes padronizados (escore z nacional): o maior excesso de tripla diferença D(s,w) entre J1, J2 e J3 (seção 6.1) e o maior K(s,2T,w) entre J1, J2 e J3. O índice é definido antes da abertura do 2o turno e não é recalibrado depois.

## 6 Hipóteses e testes

### 6.1 H1a - excesso de habilitações sem biometria

Estimador por seção (tripla diferença):

D(s,w) = [r(s,2T,w) - r(s,2T,J0)] - [r(s,1T,w) - r(s,1T,J0)]

A diferença dentro do dia controla a composição do eleitorado e o desempenho do leitor biométrico da seção; a diferença entre turnos controla o padrão habitual daquela seção no fim do dia.

Estatística nacional por janela: média de D(s,w) ponderada por N_H(s,2T,w), comparada com a mesma estatística calculada no 2o turno de 2022 (delta = média 2026 - média 2022).

- **H0a(w):** delta(w) <= 0.
- **H1a(w):** delta(w) > 0.
- **Teste:** unilateral, com erro-padrão por bootstrap em blocos de zona eleitoral (10.000 réplicas, seed fixada). O p-valor entra na família S-PIANISTA.
- **Relevância material:** o resultado só é descrito como excesso materialmente relevante se o limite inferior do IC95% de delta(w) for maior ou igual a 5 p.p. Rejeitar H0a com estimativa abaixo de 5 p.p. é reportado como excesso estatisticamente detectável, mas abaixo do efeito mínimo.
- **Sinalização de seções (não confirmatória):** modelo hierárquico beta-binomial (seção dentro de zona, município e UF) para o excesso em cada janela; uma seção é sinalizada se P(D(s,w) >= 5 p.p. | dados) >= 0,95. A lista serve apenas para priorizar verificação documental.
- **Se 2022 não for comparável:** delta é substituído pela média de D(s,w) em 2026, testada contra zero, e o resultado é rebaixado a exploratório.
- **Janela J3:** em 2022 não houve prorrogação, e só seções com fila residual terão habilitações após 17h49. Se menos de 500 seções de 2022 tiverem N_H > 0 em J3, a comparação de J3 com 2022 é rebaixada a exploratória e H1a-J3 usa apenas a comparação com o 1o turno de 2026, declarada como limitação.

### 6.2 H1b - rajadas sem biometria

Estatística por seção: K(s,2T,w).

Distribuição nula por seção, condicionada ao número de habilitações observadas: 10.000 simulações que mantêm o número de habilitações e de habilitações sem biometria da seção na janela w, sorteando os intervalos da distribuição empírica dos intervalos da mesma seção em J0 do 2o turno, e a ordem biométrica/sem biometria por permutação. O p-valor da seção é a proporção de simulações com K maior ou igual ao observado.

Estatística nacional por janela: proporção de seções com K(s,2T,w) >= 2, comparada com a mesma proporção em K(s,1T,w) (mesmas seções), e esta diferença comparada com a do 2o turno de 2022.

- **H0b(w):** a diferença entre turnos na proporção de seções com K >= 2 em 2026 não excede a de 2022.
- **H1b(w):** excede.
- **Teste:** unilateral, bootstrap em blocos de zona (10.000 réplicas). O p-valor entra na família S-PIANISTA.
- **Sinalização de seções (não confirmatória):** seções com K >= 2 e p-valor de seção com q <= 0,05 após Benjamini-Hochberg sobre todas as seções da janela.

### 6.3 H1c - associação simétrica com a votação

Mesma especificação do teste primário do pré-registro 00, com A(s) no lugar de V17:

dL(s) = alfa_local + beta * A(s) + gama * X(s) + e(s)
dF(s) = alfa_local + beta' * A(s) + gama' * X(s) + e'(s)

onde dL e dF são as variações de Lula e de Flávio entre turnos, medidas sobre o comparecimento (não sobre os válidos, para que brancos e nulos impeçam que um teste seja o espelho exato do outro). Efeitos fixos de local de votação; erros-padrão agrupados por zona; mesmas covariáveis X do pré-registro 00.

- **H0c(Lula):** beta = 0. **H1c(Lula):** beta diferente de 0.
- **H0c(Flávio):** beta' = 0. **H1c(Flávio):** beta' diferente de 0.
- Os dois testes são bilaterais, executados com o mesmo código e reportados lado a lado, qualquer que seja o resultado.
- **Limite de materialidade:** o efeito implicado não pode exceder o número de habilitações sem biometria em rajada das seções; se exceder, declara-se má especificação, não fraude.

### 6.4 H1d - assinatura conjunta

Contagem de seções sinalizadas ao mesmo tempo em H1a e H1b, em qualquer janela.

- **H0d:** a contagem conjunta não excede a esperada sob independência entre as duas sinalizações.
- **H1d:** excede.
- **Teste:** permutação das sinalizações de H1b entre seções do mesmo município (10.000 permutações). O p-valor entra na família S-PIANISTA.

## 7 Regras de exclusão e sinalização

Mantidas da v1.0 (seção 6), com dois acréscimos:

1. Seções com urna substituída, votação manual ou mais de um arquivo de log no 2o turno são excluídas das estatísticas de janela e reportadas à parte, porque a sequência de eventos pode estar fragmentada.
2. A análise de robustez repete H1a e H1b excluindo seções em municípios com denúncia registrada de problema de transporte público em 25/10/2026, cuja lista deve ser congelada em emenda antes da abertura do 2o turno.

## 8 Explicações alternativas a testar

Mantidas da v1.0 (seção 9), com atenção especial a:

- fila acumulada por falta de transporte, que aumenta a pressão por liberação manual;
- eleitores tardios com perfil diferente (idade, trabalho manual, digital desgastada);
- falha ou troca de leitor biométrico ao longo do dia;
- no 2o turno de 2022, as operações de fiscalização viária no dia da votação, que também alteraram o fluxo de eleitores; o placebo de 2022 não é um dia sem perturbação.

## 9 Diagnóstico de poder (obrigatório antes da abertura do 2o turno)

Com dados do 1o turno de 2026 apenas:

1. Injetar inserções sintéticas do tipo pianista (k habilitações sem biometria em rajada, k = 5, 10, 20 e 50, em J1) em seções sorteadas.
2. Estimar, para cada k, a sensibilidade de H1a e H1b e a taxa de falsos positivos em seções sem injeção.
3. Reportar o menor k detectado com poder maior ou igual a 0,80 sob os limiares fixados (5 p.p.; 2 rajadas).

Se nenhum k testado for detectável, o resultado do 2o turno será reportado como inconclusivo quanto a inserções desse porte, e não como ausência de anomalia.

## 10 Tabela de interpretação

| Resultado | Interpretação |
|-----------|---------------|
| H1a e H1b não rejeitadas, com poder adequado | Não há excesso detectável de habilitações sem biometria nem de rajadas acima do porte detectável |
| H1a rejeitada, H1b não | Mais liberações manuais no fim do dia, sem padrão temporal de inserção; compatível com fila e falha biométrica |
| H1b rejeitada, H1a não | Rajadas sem aumento da taxa; investigar registro de horário e modelo de urna antes de qualquer outra leitura |
| H1a, H1b e H1d rejeitadas, H1c nula para os dois candidatos | Anomalia operacional concentrada, sem associação com o resultado |
| H1a, H1b e H1d rejeitadas, H1c rejeitada para um candidato dentro do limite de materialidade | Único cenário que justifica encaminhar as seções sinalizadas para verificação documental (atas, caderno de votação e perícia de assinaturas) pela autoridade competente |
| Qualquer resultado com poder inadequado | Inconclusivo |

Em todos os cenários: reportar o número máximo de votos que as anomalias poderiam representar e compará-lo com a margem nacional.

## 11 Decisões ainda pendentes (sem efeito sobre as hipóteses)

1. Confirmação, por inspeção de metadados, de que os logs registram modalidade de habilitação, timestamp e seção; se não registrarem, a análise correspondente não é executada.
2. Verificação da licença dos logs do 2o turno de 2026.
3. Lista de municípios com denúncia de transporte (seção 7).
4. Valor de dt* e hash do cálculo (seção 5.2).

Os itens 3 e 4 entram em emenda antes da abertura do 2o turno.

## Referências

Mantidas as referências da versão 1.0, que permanecem válidas.

HYNDMAN, Rob J.; FAN, Yanan. Sample quantiles in statistical packages. *The American Statistician*, v. 50, n. 4, p. 361-365, 1996.
