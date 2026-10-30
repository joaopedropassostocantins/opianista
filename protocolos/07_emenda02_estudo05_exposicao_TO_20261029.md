# Emenda 02 ao pre-registro E05-0 - Exposicao aos microdados do Tocantins

Data: 2026-10-29
Pre-registro de referencia: `protocolos/04_estudo05_preregistro_v1_20261029.md` (SHA-256 9c6aaad2...afc34e142)
e Emenda 01 (`protocolos/05_emenda01_estudo05_20261029.md`).

## 1 Fato

Em 29/10/2026, o piloto do Estudo 03 abriu os microdados por secao do 2o turno de 2026 do
Tocantins (logs de urna e BU das 4.384 secoes com arquivos), depois da Emenda 02 do Estudo 03
(`protocolos/02_emenda_20261029_calibracao_piloto_TO.md`). Saidas derivadas foram publicadas no
branch `saidas-actions` e o resultado em
`estudos/03_pianista/etapas/05_inferencia/resultados_piloto_TO/`.

Entre as informacoes ja conhecidas sobre o Tocantins: a ultima habilitacao do 2o turno ocorreu as
17h11; houve 181 habilitacoes depois das 17h, em 165 secoes, e nenhuma depois das 17h49.

## 2 Consequencia para o Estudo 05

1. O registro do E05-0 so e prospectivo para microdados por secao ainda nao abertos. Os do
   Tocantins deixaram de ser.
2. O Tocantins fica excluido das analises confirmatorias do Estudo 05. Pode aparecer apenas em
   analises descritivas, rotuladas como pos-exposicao.
3. A exclusao praticamente nao reduz a amostra: pelo ultimo horario de habilitacao registrado no
   log (fonte interna, classe I do E05-0), nenhuma secao do Tocantins teve habilitacao depois das
   19h, uma teve depois das 17h10 e 165 depois das 17h.

## 3 O que nao muda

Hipoteses, estimador, classes de horario, controles e regras de exclusao do E05-0 e da Emenda 01
permanecem inalterados.
