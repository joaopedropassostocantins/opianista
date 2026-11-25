# PRE-REGISTRO 03 — ESTUDO 05: COLISÃO DE TÍTULO NO REGISTRO DE PRESENÇA DE MESÁRIO (ELEIÇÕES 2026)

Congelado antes da execução do teste principal (`src/simulacao.py` sobre os dados do censo). Os hashes SHA-256 do código estão na seção 12. Nenhuma colisão real foi calculada ou inspecionada antes deste congelamento: o piloto (2.000 seções) foi usado apenas para estimar parâmetros de taxa de erro e de poder, e o pipeline foi validado com dados sintéticos (`estudos/05_colisao_titulo_mesario/tests/teste_sintetico.py`).

## 1 OBJETIVO E HIPÓTESES

Medir se a repetição do mesmo número de título no registro de presença de mesário, em seções diferentes e no mesmo turno, ocorre em volume ou concentração superiores aos previstos por um modelo de erro de digitação.

- H0 (mecanismo banal): as colisões resultam de (1) erro de digitação, (2) aprovação do número errado na validação estrutural da urna e (3) coincidência do número errado com o título de outro mesário registrado em outra seção.
- H1v (excesso de volume): número observado acima do limite superior do intervalo de 95% do nulo.
- H1c (excesso de concentração): número observado dentro do intervalo, porém aglomerado em poucas seções ou UFs além do previsto pelo nulo.

## 2 FONTES E UNIVERSO

- Logs por seção: `resultados.tse.jus.br/oficial/ele2026/arquivo-urna/{3220|3221}/dados/...` (1º turno, pleito 3220, 04/10/2026; 2º turno, pleito 3221, 25/10/2026). Catálogo oficial: 517.179 seções por turno (27 UFs + ZZ); seções agregadas não possuem arquivo próprio (HTTP 404) e entram no denominador como "sem arquivo".
- Linha de base homologada: pacotes por UF de 2022 em `cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2022/arqurnatot/` (lidos por HTTP Range, só as entradas `.logjez`).
- 2018: os pacotes equivalentes não estão publicados no CDN do TSE (HTTP 404 em `eleicoes2018/arqurnatot/`), e o portal de resultados não mantém mais `ele2018`. A comparação com 2018 fica registrada como **não executável**; se houver tempo, 2024 (eleição municipal homologada, mesma estrutura de log) é usada como segunda referência, declarada como substituta e não equivalente.
- Coordenadas e eleitorado (M): `eleitorado_local_votacao_2026.zip` e `_2022.zip` (dadosabertos.tse.jus.br). M(2026) = 158.745.463; M(2022) = 156.454.011.
- Convocação de mesários (`convocacao_mesarios_<ano>.zip`): publicada apenas de forma agregada por zona, sem título nem seção; **não permite cruzamento individual** de designação.

Escala: **censo** de todas as seções com arquivo, nos dois turnos. O arquivo bruto não é mantido integralmente em disco (aproximadamente 50 GB por turno); para cada arquivo, ficam no manifesto a URL e o SHA-256 do original, o que permite baixá-lo de novo e provar a identidade byte a byte. Os brutos das seções envolvidas em colisões são baixados novamente e conferidos contra o hash.

## 3 FASE 0 — VOCABULÁRIO E REGRA DE VALIDAÇÃO

Vocabulário levantado em 30 seções de 5 UFs (TO, SP, BA, RS, AM; `registro/fase0_amostra.csv`, `registro/fase0_vocab_bruto.txt`) e confirmado em 3.000 logs do piloto. As strings são idênticas em 2022 e 2026.

| Evento | String exata (campo 5 da linha) |
|---|---|
| Início do registro | `Operador indagado se ocorrerá registro de mesários`; `Registrando mesários antes da votação` / `durante a votação` / `após a votação` |
| Digitação do título (válido) | `Pedido de leitura da biometria do mesário <T12>` |
| Erro de título inválido | `Digitado título inválido para o registro de mesário` (o número rejeitado não é gravado) |
| Confirmação (unidade de análise) | `Mesário <T12> registrado` |
| Duplicata na mesma seção | `Mesário <T12> já registrado` |
| Vínculo com a seção | `Mesário <T12> é eleitor da seção` / `Mesário <T12> não é eleitor da seção` |
| Biometria coincide | `Realizada a conferência da biometria do mesário` |
| Biometria não coincide | `Digital capturada não corresponde a digital do eleitor: ... [score n]` |
| Habilitação de eleitor | `Eleitor foi habilitado`; o título do eleitor **não** é gravado (`Identificador digitado pelo mesário foi: (Título de eleitor)`) |
| Título inválido de eleitor | `Identificador do eleitor digitado inválido` (2026) / `Título inválido` (2022), fora do ciclo de mesário |
| Reinício e contingência | `Início das operações do logd`, `Urna ligada em ...`; urna substituta aparece como segundo hash no `aux.json` da seção; identificador da urna no campo 3 |

Separação mesário x eleitor: **inequívoca**. O título só aparece em claro no ciclo de registro de mesário; o log nunca grava o título digitado para habilitar eleitor. O confundidor "título digitado para liberar eleitor confundido com título de mesário" fica eliminado por construção.

Regra de validação (determinada empiricamente):

1. Todos os títulos registrados no piloto passam no algoritmo público do DV (0 de 14.948 falham), o que é compatível com rejeição por DV/UF.
2. 70% dos registros vêm com `não é eleitor da seção` e são aceitos: a urna **não** exige que o título pertença à lista da seção.
3. Quando o título é de eleitor da seção, a urna confere a digital; em 26% das conferências o resultado é `não corresponde` e, mesmo assim, o registro prossegue (sequência `Pedido > não corresponde > é eleitor > registrado`, 1.984 casos em 3.000 logs).
4. Os números rejeitados não são gravados, de modo que a regra de rejeição não pode ser auditada pelo lado negativo; a conclusão é que a validação é estrutural (DV/UF), sem consulta à lista, com conferência biométrica apenas informativa e apenas para eleitores da própria seção.

## 4 DESVIO JUSTIFICADO EM RELAÇÃO AO PROTOCOLO SOLICITADO: MEDIDA DE p1

O protocolo propunha usar a mensagem de biometria não coincidente como rastro do erro. A Fase 0 mostra que isso é inválido por duas razões: (i) a conferência só existe quando o título digitado é de eleitor **da própria seção**, e numa colisão entre seções o título errado pertence, em regra, a mesário de outra seção, de modo que a mensagem não pode ocorrer; (ii) a mensagem `não corresponde` ocorre em 26% das conferências com scores baixos e é dominada por falha de leitura da digital, não por título errado.

Medida adotada (rastro direto no log): **quase-duplicado na mesma seção**. Cada mesário é registrado em regra duas vezes (antes e após a votação). Um erro que passa no DV registra um título válido errado; a outra digitação, correta, registra o título verdadeiro. Ficam então dois títulos registrados na mesma seção a um único erro de distância (substituição, transposição adjacente, transposição com salto ou erro gêmeo). Definições:

- U_obs = número de pares quase-duplicados na mesma seção;
- d = probabilidade de visibilidade = fração de ocorrências (título, seção) com 2 ou mais registros, entre as não envolvidas em quase-duplicados;
- U = U_obs / d = títulos válidos errados registrados;
- p2_k = fração de vizinhos de tipo k que passam no DV, calculada por enumeração sobre os títulos reais. Valores do piloto: corpo sequencial 1,88%; prefixo de UF 0,65%; DV 0,00%; transposição adjacente 1,13%; salto 1,28%; gêmeo 10,5%. O valor de ~27% citado para o prefixo de UF não se confirma, porque a UF entra no cálculo do segundo DV;
- distribuição de todos os erros por tipo: w_k ∝ (quase-duplicados observados do tipo k) / p2_k; p2 = Σ w_k p2_k;
- E = U / p2 (erros totais); p1 = E / N.

Alternativa registrada como limite superior: E_inv = (tentativas `Digitado título inválido`) / (1 − p2). No piloto, ela implica cerca de 15 vezes mais títulos válidos errados do que o quase-duplicado mostra (2 observados contra ~38 previstos), indicando que a maior parte das tentativas inválidas não é erro de um dígito em número de 12 dígitos (por exemplo, entrada incompleta).

## 5 DEFINIÇÕES OPERACIONAIS

- Registro: linha `Mesário <T> registrado`, aplicação VOTA, data igual à data oficial do turno, sessão em fase `Oficial`. Unidade de análise.
- Ocorrência: par (título, seção) com pelo menos um registro.
- Colisão: par não ordenado de seções distintas com ocorrência do mesmo título no mesmo turno.
- Exclusões: (a) duplicata na mesma seção (não é colisão por definição); (b) pontas que compartilham identificador de urna ou hash de linha (replicação por contingência ou restart); (c) logs com relógio inconsistente: registro fora de 05:00–23:59 do dia do turno ou retrocesso superior a 300 s entre linhas VOTA consecutivas; (d) linhas fora da fase Oficial (treinamento ou simulado).
- Faixas de distância (haversine entre coordenadas dos locais de votação; mesmo local de votação = 0 km): A) <1 km; B) 1–50 km; C) >50 km; ND sem coordenada.
- Faixas de intervalo (menor |Δt| entre registros das duas pontas): <60 s; 1–30 min; 30 min–4 h; >4 h.
- As faixas são reportadas cruzadas e **nunca somadas** entre si para o veredito.

## 6 MODELO NULO

- Via 1 (analítica): colisões ≈ N × p1 × p2 × q, com q = (títulos únicos registrados por mesários) / M.
- Via 2 (simulação, preferida): fonte de cada erro = evento de registro sorteado uniformemente entre os N; tipo ~ w; resultado uniforme entre os vizinhos do tipo; há colisão quando o resultado pertence ao **multiconjunto de títulos efetivamente registrados por mesários** em seção diferente da fonte (nunca ao eleitorado inteiro). E erros por réplica; 10.000 réplicas; semente 20261004. O nulo herda a geografia e a distribuição real dos títulos.
- Via 3 (segunda ordem): dois erros distintos que caem no mesmo título válido não pertencente a nenhum mesário, em seções diferentes; Monte Carlo com geração explícita do número digitado.
- Divergência superior a 50% entre Via 1 e Via 2 é investigada e explicada antes da conclusão.

## 7 TESTE DE CASO (cada colisão)

Classificação hierárquica, nesta ordem:

1. `excluida_*` — mesma urna ou linha idêntica;
2. `erro_digitacao_evidenciado` — existe, em uma das pontas, título registrado a um erro de distância do título colidido (o titular verdadeiro digitou o próprio número na outra vez);
3. `mesmo_predio_<1km` — faixa A, sem anomalia;
4. `dono_conferido_por_biometria_em_uma_ponta` — em uma ponta o título é de eleitor da seção e a biometria coincidiu;
5. `residuo_sem_explicacao_no_log` — nenhum dos anteriores. É o resíduo que o mecanismo não cobre.

Registram-se também o vínculo com a seção e o resultado biométrico em cada ponta, e a designação legítima para duas seções, que não é verificável individualmente (seção 2).

## 8 TESTES ESTATÍSTICOS

- Por faixa de distância × intervalo: observado O; esperado E (média da Via 2); intervalo de 95% do nulo (quantis 2,5% e 97,5% das réplicas); razão O/E com IC 95% exato de Poisson (Garwood) para O, dividido por E; p = P_sim(X ≥ O).
- Dispersão e concentração: índice de dispersão das colisões por seção; P_sim(máximo de colisões numa seção ≥ observado); qui-quadrado da distribuição por UF contra a distribuição esperada pela Via 2; fração de seções envolvidas.
- Comparação histórica: mesmo pipeline em 2022 (ambos os turnos); taxa de colisões por 10^6 registros por faixa, com IC 95% exato; 2026 dentro do IC de 2022 → compatível com a referência homologada.
- Sensibilidade: E × 0,5; E × 2; E_inv (tentativas inválidas). Se o veredito muda em qualquer cenário, o resultado é declarado **frágil**.

## 9 REGRA DE DECISÃO (por faixa de distância B e C; A e ND reportadas sem juízo de anomalia)

- (a) Acaso, encerrado: O ≤ limite superior do intervalo de 95% do nulo **e** P_sim(máximo por seção) ≥ 0,05 **e** p(qui-quadrado UF) ≥ 0,05.
- (b) Excesso de volume: O > limite superior do intervalo de 95% do nulo; informar magnitude (O − E, O/E com IC) e faixa.
- (c) Mecanismo insuficiente por concentração: O dentro do intervalo, mas P_sim(máximo por seção) < 0,05 ou p(qui-quadrado UF) < 0,05, com as colisões concentradas em menos de 5% das seções.
- A ausência de excesso, quando ocorrer, abre o relatório.

## 10 PODER

Com o rastro calibrado (quase-duplicado), o piloto projeta λ0 de unidades no censo (0,08 com 10% de amostra; ~8 no censo), e o poder para detectar razão 2 com α = 0,05 unilateral chega a ~69% no censo (`estudos/05_colisao_titulo_mesario/registro/poder.json`). O poder mínimo de 80% **não é atingível** nem com censo sob a calibração central; isso é declarado na primeira linha do relatório. O censo é obrigatório porque qualquer amostra torna o teste inconclusivo por construção (λ0 escala com f²).

## 11 CONFUNDIDORES E COMO ENTRAM

| Confundidor | Tratamento |
|---|---|
| Mesário eleitor de outra seção digitando o próprio título | não gera colisão sozinho (exige registro do mesmo título em duas seções); flag `eleitor_secao` em cada ponta |
| Mesmo mesário em turnos diferentes | fora da definição (colisão é intra-turno) |
| Substituição no mesmo dia / outra mesa | faixa A e faixas de intervalo; classe `mesmo_predio_<1km` |
| Mesa incompleta | contagem de registros por seção em `colisoes.csv` |
| Restart/contingência replicando linhas | exclusão por id de urna e hash de linha |
| Título de eleitor confundido com mesário | eliminado: o log não grava título de eleitor |
| Designação legítima para duas seções | não verificável (convocação só agregada); ressalva quantificada pelo número de resíduos |

## 12 HASHES DO CÓDIGO CONGELADO

Ver `estudos/05_colisao_titulo_mesario/registro/HASHES_CODIGO.txt`, gerado no momento do congelamento e incluído no mesmo commit.

## 13 PROTEÇÃO DE DADOS E PUBLICAÇÃO (CONTRIBUTING, REGRA 4)

Os títulos de mesário são dados pessoais (Lei n. 13.709/2018, art. 5º, I). O processamento usa o número em claro apenas em memória e em `data/` (fora do Git), porque a detecção de quase-duplicados e a simulação dependem dos dígitos. Toda saída versionada passa por `src/pseudonimizar.py`: cada título é substituído por HMAC-SHA256 com chave de 32 bytes guardada em `data/chave_pseudonimo.bin`, truncado em 16 hexadecimais. A igualdade entre títulos é preservada; o tipo de erro, as posições dos dígitos divergentes e o prefixo de UF do título são mantidos. Os logs brutos não são redistribuídos; o repositório publica URL e SHA-256.

## 14 CONTATO COM DADOS DO 2º TURNO DE 2026 (RELAÇÃO COM O ESTUDO 03)

Este estudo lê os logs do 2º turno de 2026 (pleito 3221) em todas as UFs, mas extrai exclusivamente as linhas do ciclo de registro de mesário e os contadores de integridade listados no `parsing.py`. Nenhuma estatística do Estudo 03 (habilitação por ano de nascimento, rajadas, cadência, dt*) é calculada, e nenhum dado de habilitação de eleitor ou de voto é gravado. O contato fica declarado aqui para a avaliação do proponente quanto ao bloqueio do item 1.7 do PLANEJAMENTO.

## 15 ORIGEM E CONGELAMENTO

Este protocolo reproduz, com os caminhos adaptados a este repositório e com as seções 13 a 15 acrescentadas, o pré-registro congelado em 2026-11-25T00:41:22Z no repositório `forense-tse-2022` (branch `claude/intelligent-wright-dufdp6`, commit 25e59f4). O código é byte a byte idêntico ao daquele congelamento (hashes em `estudos/05_colisao_titulo_mesario/registro/HASHES_CODIGO.txt`). O único arquivo acrescentado depois é `pseudonimizar.py`, que atua só sobre as saídas e não altera nenhuma contagem. Nenhuma colisão real havia sido calculada até este registro.
