# Estudo 02 - Transferencia de votos entre turnos

## Pergunta

A captacao de votos entre o 1o e o 2o turno de 2026 foi atipica quando
comparada com a dinamica observada em 2022?

## Registro do que ja foi feito (a reproduzir com codigo)

1. Verificacao aritmetica de um infografico de transferencia de votos: contas
   corretas dentro do arredondamento.
2. Simulacao Monte Carlo (1 milhao de iteracoes, varios cenarios de priors):
   a captacao de Lula de 73,6% do "estoque" de votos disponiveis em 2026 ficou
   comparavel a captacao de Bolsonaro de 69,8% em 2022, sob dinamica
   semelhante.
3. Goias: o ganho de Flavio foi o maior do pais e a captacao de Lula a menor,
   o que contraria a leitura de que votos de Caiado migraram para Lula.
   Atencao a falacia ecologica: dados agregados nao revelam a migracao
   individual.

## Proximos passos

- Inferencia ecologica R x C (Rosen multinomial-Dirichlet ou modelo bayesiano
  de transicao) por UF, prevista no pre-registro 00 como analise descritiva.
- Mesmo modelo para 2022 e 2018 como referencia.
- Publicar o script da simulacao Monte Carlo com seed fixa.
