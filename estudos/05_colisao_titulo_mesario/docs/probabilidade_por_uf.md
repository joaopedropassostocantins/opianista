# PROBABILIDADE POR UF DE O ERRO DE DIGITAÇÃO GERAR COLISÃO COM OUTRO MESÁRIO

Análise exploratória, anterior ao teste confirmatório e fora do código congelado (`src/probabilidade_uf.py`). Ela não usa nenhuma contagem de colisões observadas: só os parâmetros do nulo, medidos no censo parcial do 1º turno de 2026 (273.969 registros de presença, UFs AC, AL, AM, AP completas e BA parcial) e no piloto nacional de 2.000 seções. Os números serão substituídos pela Via 2 do teste confirmatório quando o censo terminar.

## 1 A CADEIA DE CONDIÇÕES

Para um erro de digitação no registro de presença virar colisão entre seções, três condições precisam ocorrer em sequência:

1. P1, o número digitado errado passa na validação da urna (DV/UF);
2. P2, esse número válido é o título de outro mesário registrado;
3. esse outro mesário está em outra seção. Se estiver na mesma urna e já registrado, a urna recusa com `Mesário <T> já registrado` e não há colisão.

A urna libera o registro qualquer que seja o dono do número: 70% dos registros vêm com `não é eleitor da seção` e são aceitos. A conferência da digital só ocorre quando o número é de eleitor da própria seção e, mesmo com `não corresponde`, o registro prossegue.

## 2 PARÂMETROS MEDIDOS

| Parâmetro | Valor | Origem |
|---|---|---|
| Registros de presença medidos (N) | 273.969 | censo parcial 1T 2026 |
| Quase-duplicados na mesma seção (erros válidos visíveis) | 51 (corpo 41, transposição 5, prefixo UF 4, gêmeo 1) | idem |
| Probabilidade de o erro ficar visível (d) | 0,809 | fração de mesários registrados 2 ou mais vezes na seção |
| p2 ponderado pelos tipos observados | 1,64% | enumeração do DV sobre os títulos reais |
| **p1 (erros de digitação por registro)** | **1,40% (IC 95%: 1,05% a 1,85%)** | U / d / p2 / N |
| p1 se todas as tentativas inválidas fossem erros de um dígito | 23,5% | cenário de limite superior |
| h, fração dos erros que cai em título de outro mesário em outra seção | 1,30 × 10⁻⁴ | medido nas UFs completas (AC, AL, AM, AP) |

O p1 medido, de 1,4%, fica próximo do 1% suposto na análise do proponente. A medida vem do rastro no log, não de suposição.

Aprovação no DV por posição do erro (p2): corpo sequencial 1,89%; prefixo de UF 0,76%; dígito verificador 0%; transposição adjacente 1,25%; transposição com salto 1,31%; gêmeo 10,3%. O valor varia pouco entre UFs (1,3% a 2,0%), exceto ZZ (0,6%).

## 3 O QUE A MEDIÇÃO REFUTA NA ANÁLISE POR DENSIDADE DE ELEITORADO

A análise do proponente supunha que P2 é a densidade média de títulos por UF: eleitorado ou mesários divididos pelo espaço de números da UF. Nesse modelo, estados grandes produzem muito mais colisões por erro e estados pequenos quase nenhuma.

Os logs contradizem esse modelo. Nas quatro UFs com censo completo, a fração de erros que cai em título de outro mesário é:

| UF | h medido | h previsto pelo modelo de densidade | Fontes |
|---|---|---|---|
| AC | 1,45 × 10⁻⁴ | 0,04 × 10⁻⁴ | 8.695 |
| AL | 1,39 × 10⁻⁴ | 0,07 × 10⁻⁴ | 26.426 |
| AM | 1,13 × 10⁻⁴ | 0,12 × 10⁻⁴ | 30.429 |
| AP | 1,47 × 10⁻⁴ | 0,01 × 10⁻⁴ | 6.533 |

Os valores medidos são de 10 a 100 vezes maiores e praticamente constantes entre UFs de tamanhos muito diferentes. A razão é estrutural. Um erro de um dígito leva a um número vizinho do original, e títulos vizinhos foram emitidos no mesmo cartório e na mesma época; mesários da mesma zona tendem a ter números próximos. A probabilidade relevante é a densidade **local** de mesários na vizinhança numérica, não a densidade média da UF. Consequências:

1. Estados pequenos não são imunes. A expectativa por UF acompanha o número de registros (seções), não o quadrado do eleitorado.
2. A concentração em SP, MG e RJ prevista pela análise por densidade não é uma assinatura do mecanismo. Pelo nulo medido, SP responde por cerca de 20% da expectativa, proporcional ao número de seções.
3. Ocorrências em UFs pequenas não são, por si, estranhas.
4. Pela mesma razão, a colisão gerada por erro tende a ligar seções próximas (mesma zona). Distância curta não distingue erro de outra causa, e distância longa é menos provável sob o nulo, mas não impossível.

Os valores de h são limites inferiores: títulos de mesário com o mesmo prefixo registrados em UFs ainda não processadas não entram no conjunto-alvo.

## 4 EXPECTATIVA POR UF (1º TURNO DE 2026)

E_u = N_u × p1 × h. N_u é a projeção censitária dos registros (seções com log × 7,48 registros por seção). Colunas: p1 × 0,5, central e × 2 (sensibilidade pré-registrada) e o cenário de limite superior baseado nas tentativas inválidas.

| UF | Registros N | P1 (erro vira válido) | p1 × 0,5 | Central | p1 × 2 | Limite sup. |
|---|---|---|---|---|---|---|
| SP | 746.665 | 1,50% | 0,68 | 1,36 | 2,72 | 22,8 |
| MG | 389.437 | 1,53% | 0,36 | 0,71 | 1,42 | 11,9 |
| RJ | 278.375 | 1,62% | 0,25 | 0,51 | 1,01 | 8,5 |
| BA | 272.713 | 1,67% | 0,25 | 0,50 | 0,99 | 8,3 |
| RS | 199.328 | 1,78% | 0,18 | 0,36 | 0,73 | 6,1 |
| PR | 196.439 | 1,33% | 0,18 | 0,36 | 0,72 | 6,0 |
| CE | 184.324 | 1,65% | 0,17 | 0,34 | 0,67 | 5,6 |
| PE | 158.748 | 1,72% | 0,14 | 0,29 | 0,58 | 4,9 |
| PA | 158.684 | 1,52% | 0,14 | 0,29 | 0,58 | 4,9 |
| MA | 142.242 | 1,74% | 0,13 | 0,26 | 0,52 | 4,3 |
| SC | 126.174 | 1,50% | 0,12 | 0,23 | 0,46 | 3,9 |
| GO | 116.602 | 1,81% | 0,11 | 0,21 | 0,42 | 3,6 |
| PI | 80.923 | 1,62% | 0,07 | 0,15 | 0,29 | 2,5 |
| PB | 77.933 | 1,79% | 0,07 | 0,14 | 0,28 | 2,4 |
| ES | 72.745 | 1,86% | 0,07 | 0,13 | 0,27 | 2,2 |
| MT | 64.495 | 1,88% | 0,06 | 0,12 | 0,23 | 2,0 |
| AM | 61.635 | 1,68% | 0,06 | 0,11 | 0,22 | 1,9 |
| RN | 59.903 | 1,42% | 0,05 | 0,11 | 0,22 | 1,8 |
| MS | 52.344 | 1,72% | 0,05 | 0,10 | 0,19 | 1,6 |
| AL | 52.071 | 1,61% | 0,05 | 0,09 | 0,19 | 1,6 |
| DF | 50.662 | 1,88% | 0,05 | 0,09 | 0,18 | 1,6 |
| SE | 43.598 | 2,04% | 0,04 | 0,08 | 0,16 | 1,3 |
| RO | 35.507 | 1,64% | 0,03 | 0,06 | 0,13 | 1,1 |
| TO | 32.266 | 1,86% | 0,03 | 0,06 | 0,12 | 1,0 |
| ZZ | 19.510 | 0,61% | 0,02 | 0,04 | 0,07 | 0,6 |
| AC | 17.326 | 1,68% | 0,02 | 0,03 | 0,06 | 0,5 |
| AP | 14.164 | 1,61% | 0,01 | 0,03 | 0,05 | 0,4 |
| RR | 11.692 | 1,64% | 0,01 | 0,02 | 0,04 | 0,4 |
| **Brasil** | **3.716.505** | — | **3,4** | **6,8** | **13,5** | **113** |

## 5 LEITURA

1. Expectativa nacional por turno: cerca de 7 colisões (3 a 14 na sensibilidade pré-registrada). A ordem de grandeza da análise do proponente (1 a 5) se confirma: são unidades, não milhares. A distribuição entre UFs, porém, é proporcional ao número de seções, não à densidade do eleitorado.
2. Sob o nulo, a contagem segue aproximadamente uma Poisson. Com média 6,8, o intervalo central de 95% vai de 2 a 12. Um número observado dentro dessa faixa é compatível com o acaso; acima de 12, num turno, é excesso de volume sob a calibração central. O critério formal é o da Via 2 no teste congelado, que inclui geografia e intervalo de tempo.
3. O parâmetro mais sensível continua sendo p1. A diferença entre a medida pelo rastro (1,4%) e a leitura ingênua das tentativas inválidas (23,5%) é de 17 vezes, e o veredito depende dela. Por isso o pré-registro fixa o rastro como medida central.
4. Nenhum dado de colisão observada foi aberto para esta análise. Os casos citados no vídeo de referência não foram verificados aqui e serão tratados apenas pelo censo.

## 6 LIMITAÇÕES

- h medido em quatro UFs pequenas e aplicado às demais; o teste confirmatório mede h por UF no censo completo.
- h é limite inferior enquanto o censo não estiver completo.
- N_u é projetado do piloto (7,48 registros por seção); no teste confirmatório, N_u é contado.
- O nulo não inclui causas legítimas não aleatórias, como a mesma pessoa trabalhando em duas seções; elas aparecem como observado acima do nulo e são separadas pelo teste de caso.
