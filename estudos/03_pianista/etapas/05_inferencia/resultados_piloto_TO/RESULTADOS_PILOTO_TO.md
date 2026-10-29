# Resultados do piloto no Tocantins - Estudo 03 (hipotese do mesario pianista)

Data: 29/10/2026
Protocolo: v1.1 (GATE 0 aprovado) e Emenda 02 (`protocolos/02_emenda_20261029_calibracao_piloto_TO.md`),
registrada antes da abertura dos dados do 2o turno de 2026.
Escopo: somente Tocantins. Os resultados nao se estendem ao pais.

## 1 Conclusao

No Tocantins, os dados nao sustentam a hipotese do mesario pianista. Nenhum dos testes da familia
pre-registrada foi rejeitado (todos os q-valores iguais a 1,0). O excesso de habilitacoes sem
biometria no fim do dia foi **menor** em 2026 do que em 2022, nenhuma secao apresentou duas ou
mais rajadas de habilitacoes sem biometria, e a intensidade das anomalias nao se associou a
votacao de nenhum dos candidatos.

Esse nulo vale para o porte de insercao que o metodo detecta (secao 5): a partir de cerca de 10
habilitacoes sem biometria por secao em J1, ou cerca de 20 em grupos. Insercoes menores, ou
feitas por eleitores com biometria, ficam fora do alcance destes testes.

## 2 Dados

| Periodo | Secoes | Habilitacoes | Sem biometria |
|---------|--------|--------------|---------------|
| 1T 2026 | 4.384 | 965.340 | 8,2% |
| 2T 2026 | 4.384 | 954.608 | 7,8% |
| 1T 2022 | 3.957 | 889.403 | 17,3% |
| 2T 2022 | 3.957 | 868.968 | 15,5% |

Validacao do leitor de logs contra o BU oficial, no 1o e no 2o turno de 2026: votos computados no
log iguais ao comparecimento do BU em 99,9% das secoes; diferenca mediana zero, por secao, entre
habilitacoes sem biometria no log e no BU.

## 3 Premissa da pergunta original

A premissa de que as secoes ficam vazias depois das 16h nao se confirma em TO:

| Periodo | Habilitacoes 16h-17h | Mediana por secao | Secoes sem nenhuma | Depois das 17h | Depois das 17h49 |
|---------|----------------------|-------------------|--------------------|----------------|------------------|
| 2T 2026 | 58.986 | 13 | 26 de 4.384 | 181 | 0 |
| 2T 2022 | 58.701 | 14 | 14 de 3.957 | 248 | 0 |

A prorrogacao ate 19h nao teve efeito observavel em TO: a ultima habilitacao do 2o turno de 2026
ocorreu as 17h11.

## 4 Testes pre-registrados (familia S-PIANISTA, FDR de Benjamini-Hochberg)

| Teste | Estimativa | IC95% | p | q |
|-------|-----------|-------|---|---|
| H1a-J1 (16h-17h): excesso sem biometria, 2026 menos 2022 | -0,99 p.p. | -1,58 a -0,49 p.p. | 0,9998 | 1,0 |
| H1a-J2 (17h00-17h48) | -3,9 p.p. (81 secoes) | -16,5 a +5,9 p.p. | 0,75 | 1,0 |
| H1a-J3 (17h49-19h00) | nao estimavel: nenhuma habilitacao | - | - | - |
| H1b-J1: secoes com 2 ou mais rajadas, 2T menos 1T, 2026 menos 2022 | -0,03 p.p. (0 secoes em 2026) | -0,09 a 0,00 p.p. | 0,83 | 1,0 |
| H1b-J2 e H1b-J3 | nao estimaveis: nenhuma secao com rajada | - | - | - |
| H1c-Lula: associacao com a variacao de Lula | beta = +0,0002 | -0,0006 a +0,0010 | 0,64 | 1,0 |
| H1c-Flavio: associacao com a variacao de Flavio | beta = -0,0001 | -0,0010 a +0,0007 | 0,75 | 1,0 |
| H1d: secoes sinalizadas nos dois criterios | 0 observadas; 0 esperadas | - | 1,0 | 1,0 |

Leitura de H1a-J1: entre 9h-15h e 16h-17h, a proporcao de habilitacoes sem biometria sobe um
pouco em todas as eleicoes observadas. No 2T 2026 essa subida, descontado o padrao da mesma secao
no 1o turno, foi de 0,50 p.p.; no 2T 2022, de 1,48 p.p. O 2T 2026 ficou abaixo da referencia
de 2022, com intervalo inteiramente negativo.

H1c usou efeitos fixos de zona eleitoral (140 zonas), e nao de local de votacao, porque o cadastro
de locais nao foi obtido; a emenda 02 previa essa alternativa.

## 5 Poder do metodo (estimado antes da abertura, com dados de 2022)

| Insercoes por secao em J1 | H1a | H1b, bloco unico | H1b, grupos de 4 |
|---------------------------|-----|------------------|------------------|
| 5 | 0,71 | 0,00 | 0,00 |
| 10 | 0,90 | 0,04 | 0,28 |
| 20 | 0,97 | 0,04 | 0,96 |
| 50 | 0,99 | 0,04 | 1,00 |

## 6 Secoes sinalizadas (nao confirmatorio)

A sinalizacao por secao de H1a marcou 4 secoes em J1 (de 4.352), abaixo da taxa de falsos
positivos estimada no diagnostico de poder (1,3%, ou cerca de 57 secoes). Marcou ainda 8 secoes em
J2 (de 81), cada uma com 1 ou 2 habilitacoes na janela; essas marcas decorrem do agrupamento
hierarquico com amostras minimas e nao tem valor informativo. Uma analise de sensibilidade que
limita a concentracao do agrupamento mantem 3 marcas em J1 e 4 em J2. A lista, pseudonimizada,
esta em `secoes_sinalizadas_TO_pseudonimizadas.csv`.

Nenhuma secao apresentou duas rajadas. A analise exploratoria H1b-L (maior sequencia continua de
habilitacoes sem biometria abaixo de 60 s) nao encontrou nenhuma secao com 5 ou mais em 2026.

## 7 Limitacoes

1. Piloto em uma UF; dt* calculado em TO, e nao no pais.
2. J3 nao testavel em TO e J2 com apenas 81 secoes: a hipotese ligada a prorrogacao nao pode ser examinada aqui. Ela depende de UFs onde houve votacao depois das 17h49.
3. O software de 2026 nao registra a mensagem de eleitor sem biometria cadastrada; esse modo foi inferido pela ausencia de marcador e validado contra o BU.
4. A amostra de 2,1% examinada antes do protocolo nao pode ser excluida (secoes nao reconstituiveis).
5. O BU foi decodificado com a especificacao ASN.1 da reconstrucao publica do VOTA; a decodificacao foi validada pela igualdade entre comparecimento do BU e votos computados no log.
6. Os testes detectam insercoes por habilitacao sem biometria. Nao alcancam manipulacao do software, nem votos inseridos com a biometria de eleitores presentes.
7. A sinalizacao por secao (secao 6) tem uma fragilidade de implementacao com amostras muito pequenas, descrita acima, que deve ser corrigida por emenda antes da execucao nacional.

## 8 Proximos passos

1. Execucao nacional com o mesmo codigo, priorizando as UFs com votacao depois das 17h49, onde J2 e J3 sao testaveis.
2. Emenda para a sinalizacao por secao com amostras pequenas (minimo de habilitacoes na janela) antes da execucao nacional.
3. Obter o cadastro de locais de votacao para H1c com efeitos fixos de local.
