# Verificação da margem nacional oficial — segundo turno de 2026

**Data da conferência:** 29/10/2026. **Objeto:** somente totais agregados publicamente divulgados pelo TSE. **Não foram abertos BU, RDV, log ou tabelas de seção do 2T2026.**

## Resultado oficial

Fonte primária 1: TSE, "Presidente do TSE anuncia reeleição de Lula e faz balanço do 2º turno", 25/10/2026.
https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/presidente-do-tse-anuncia-reeleicao-de-lula-e-faz-balanco-do-2o-turno-das-eleicoes-2026

Fonte primária 2: TSE, "Como a totalização dos votos evoluiu nas Eleições 2026?", 28/10/2026, atualização 21:13.
https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/como-a-totalizacao-dos-votos-evoluiu-ferramenta-do-tse-permite-acompanhar-o-processo

| Campo | Valor |
|---|---:|
| Luiz Inácio Lula da Silva (13) | 64.256.232 |
| Flávio Bolsonaro (22) | 59.826.041 |
| **Votos válidos = soma** | **124.082.273** |
| **Margem absoluta = diferença** | **4.430.191** |
| Participação Lula sobre válidos | 51,79% (TSE, arredondado) |
| Participação Flávio sobre válidos | 48,21% (TSE, arredondado) |

As duas publicações oficiais concordam. Logo, a anotação \`[VERIFICAR]\` da seção 2 de \`estudos/05_simulacao_temporal/REVISAO_METODOLOGICA_20261029.md\` está **RESOLVIDA nesta verificação independente**. Preservar o documento histórico; não sobrescrever para alegar que a verificação já existia na versão anterior.

## Consequência aritmética

- Para **transferência entre candidatos** o impacto na margem é 2 por voto, e o número inteiro mínimo para inverter a diferença (sem empate) é \`floor(4.430.191/2)+1 = 2.215.096\`.
- Para **acréscimo unilateral de votos** ou redução unilateral, impacto máximo de 1 por alteração, mínimo \`4.430.191+1=4.430.192\`.
- Para toda coorte tardia, definir \`V_c = soma de todos os votos válidos de todas as seções da coorte\`. A condição necessária para que uma transferência restrita à coorte pudesse inverter o resultado é \`V_c >= 2.215.096\`. É também necessário haver **pelo menos 2.215.096 votos atribuídos ao candidato de origem** dentro da coorte, no sentido de transferência exigido; o total \`V_c\` não basta.
- A fração requerida é \`2.215.096 / V_c\`, sem imputar média de seção quando houver BUs reais. Isso **não é estimativa de fraude**.

**Aviso central:** não substituir \`V_c\` pela quantidade de votos registrados após 17h. Coorte = **seções classificadas por encerramento**; votos = **totalidade dos seus BUs**. As 6.766 seções registradas após 19h e as 24.268 após 17h10 são números agregados de seções, não votos. O horário de encerramento técnico/BU pode ser posterior ao último voto.

## Limites probatórios

A margem e a materialidade são dados aritméticos, não teste de integridade. O material não examina se ocorreu adulteração do BU, um comprometimento do relógio, ou divergência de totalização. A avaliação dessas hipóteses fica bloqueada até o GATE 1.6 do Estudo 03 e a aprovação humana do pré-registro E05-0.