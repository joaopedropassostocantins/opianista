# Emenda 01 ao pre-registro 00 - Hipotese do mesario pianista

Data: 2026-10-28
Pre-registro de referencia: 00_preregistro.md (SHA-256 a2d61a95...bddbc3e)
Especificacao detalhada: `estudos/03_pianista/prompts/prompt_agentico_analise_logs_2T2026.md`

## 1 O que esta emenda acrescenta

Hipoteses confirmatorias adicionais sobre o mecanismo de habilitacao, que o
pre-registro 00 tratava apenas de forma descritiva (`n_sem_bio_pre17`,
`n_sem_bio_pos17` e ritmo de votacao):

- H1a: excesso de habilitacoes sem biometria (ano de nascimento) na janela
  final do 2o turno de 2026, relativo a mesma secao no 1o turno, alem da
  variacao entre turnos observada em 2022 e 2018.
- H1b: excesso de rajadas de votos com intervalo entre votos abaixo do limiar
  calibrado no 1o turno de 2026 (percentil 1 do dt entre habilitacoes
  biometricas, 9h-15h), alem do esperado por processo de Poisson nao
  homogeneo ajustado a propria secao.
- H1c: associacao ecologica entre intensidade da anomalia e votacao, testada
  de forma simetrica para ambos os candidatos.

O teste primario do pre-registro 00 (beta em dL sobre V17) permanece o unico
teste confirmatorio primario. H1a a H1c sao secundarias, com controle de FDR
(Benjamini-Hochberg, q = 0,05).

## 2 Janelas temporais (alinhamento com o pre-registro 00)

A classificacao das secoes quanto a prorrogacao segue as janelas de S8:
17h00-17h48 (fila regular) e a partir de 17h49 (comunicacao do TSE aos TREs).
A decisao do STF foi divulgada por volta das 17h03, mas a ordem so chegou aos
TREs as 17h49; por isso 17h49 e o marco da prorrogacao efetiva.

## 3 Declaracao de exposicao previa aos dados

Antes desta emenda, o proponente examinou uma amostra de cerca de 2,1% das
secoes do 2o turno de 2026 e observou: 553 votos apos 17h; 15,0% de
habilitacoes sem biometria apos 17h contra 10,6% antes; diferenca pareada no
voto em Lula de 0,0 p.p. (IC95% de -2,0 a +2,1) entre secoes sinalizadas e
controles da mesma zona.

Consequencias obrigatorias:
1. A diferenca de 15,0% contra 10,6% motivou parcialmente H1a. Essa amostra
   nao pode ser usada como evidencia confirmatoria de H1a.
2. As secoes dessa amostra devem ser identificadas e analisadas
   separadamente (com e sem elas), se for possivel reconstitui-las.
3. A diferenca antes/depois das 17h, sozinha, nao distingue pianista de
   explicacoes alternativas: eleitores tardios podem ter perfil diferente
   (idade, ocupacao, falha biometrica) e a fila acumulada aumenta a pressao
   para liberar por ano de nascimento. O controle e a comparacao com a mesma
   secao no 1o turno e com 2022 e 2018.

## 4 O que nao muda

Hipoteses, especificacao, regras de exclusao, alfa e tabela de interpretacao
do pre-registro 00 permanecem inalterados.
