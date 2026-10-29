# Estudo 05 - revisao metodologica do desenho de coortes

Data: 29/10/2026. Documento de revisao; nao altera protocolos registrados.

## 1 Identificabilidade: o que o desenho de coortes consegue testar

O contraste "secoes com encerramento tardio x secoes comparaveis" so tem poder
contra mecanismos cuja acao **dependa do horario** (por exemplo, um
comportamento condicionado ao relogio interno ultrapassar determinado limite).

Um comprometimento generico do software, ativo em todas as urnas, afetaria
igualmente coortes e controles; a diferenca entre grupos seria nula e o teste
nao o detectaria. Portanto:

1. Resultado nulo no contraste de coortes **nao refuta** a hipotese generica de
   insider; refuta apenas a familia de mecanismos condicionados ao horario.
2. A hipotese generica so e enfrentada por referencias externas ao dominio do
   software: testes de integridade (votacao paralela) e confronto entre BU
   impresso custodiado por fiscais e BU publicado.
3. A extensao ate 19h decorreu de decisao tomada no proprio dia. Um mecanismo
   previamente instalado nao poderia selecionar "secoes prorrogadas" senao por
   meio do relogio ou do estado de encerramento. Isso torna a familia
   condicionada ao horario a unica coerente com a hipotese de exploracao da
   prorrogacao, e e justamente ela que o desenho testa.

## 2 Materialidade

O protocolo original exige calcular o impacto maximo possivel sobre a margem
nacional (4.430.191 votos; votos validos 124.082.273, conforme
`protocolos/00_prompt_preregistro_original_20261026.md`; [VERIFICAR] contra a
divulgacao oficial do TSE). Cada voto transferido entre candidatos altera a
margem em 2. A fracao minima de votos validos da coorte que precisaria ser
transferida e `q = margem / (2 x votos validos da coorte)`.

Tamanho medio de secao estimado: 124.082.273 / 497.333 = 249,5 votos validos.
Como 497.333 e limite inferior do numero total de secoes, 249,5 e limite
superior da media nacional. Secoes que encerram tarde tendem a ser maiores;
por isso se apresentam multiplicadores 1,5 e 2,0.

| Coorte | Secoes | Votos validos por secao | Votos validos da coorte | q minimo |
|--------|-------:|------------------------:|------------------------:|---------:|
| > 19h | 6.766 | 249,5 | 1.688.086 | 1,312 (impossivel) |
| > 19h | 6.766 | 374,2 | 2.532.128 | 0,875 |
| > 19h | 6.766 | 499,0 | 3.376.171 | 0,656 |
| > 17h10 | 24.268 | 249,5 | 6.054.753 | 0,366 |
| > 17h10 | 24.268 | 374,2 | 9.082.130 | 0,244 |
| > 17h10 | 24.268 | 499,0 | 12.109.507 | 0,183 |
| Votos apos 17h | - | - | 34.393 | 64,4 (impossivel) |

Consequencias:

1. Uma alteracao capaz de inverter o resultado, se confinada as coortes
   tardias, exigiria transferir entre 18% e 100% ou mais dos votos validos
   dessas secoes. Efeito dessa magnitude seria grosseiramente visivel na
   comparacao com secoes do mesmo local de votacao; o problema de poder do
   estudo restringe-se a efeitos pequenos, que nao seriam materiais.
2. O resultado deve ser relatado em duas camadas separadas: existencia de
   anomalia (questao de integridade) e materialidade (questao de resultado).
3. Implementacao: `materiality()` em `site/src/lib/cohort-model.ts`, com
   testes em `site/tests/cohort.test.mjs`. Ao obter os dados por secao, a
   media estimada deve ser substituida pela soma observada.

## 3 Confundimento e desenho de comparacao recomendado

Encerramento tardio e selecionado: secoes grandes, urbanas, com filas, falhas
de biometria ou contingencia. Essas caracteristicas correlacionam-se com
preferencia partidaria, de modo que comparar coortes com a media nacional ou
estadual produziria diferenca espuria.

Desenho principal recomendado: **efeito fixo de local de votacao**. Secoes do
mesmo local (mesma escola) compartilham territorio e perfil de eleitorado;
compara-se a composicao integral do BU das secoes tardias com a das demais
secoes do mesmo local. Locais sem variacao no status de encerramento nao
contribuem para a estimativa. Erro-padrao agrupado por local; covariaveis:
aptos, comparecimento, secao agregada, modelo de urna, contingencia.
Placebo: o mesmo contraste no 2o turno municipal de 2024 e no 1o turno de 2026,
em que nao houve prorrogacao excepcional.

## 4 Conflito com o bloqueio do Estudo 03

O planejamento determina que nada do 2o turno de 2026 seja aberto antes do item
1.6 (emenda com dt* e diagnostico de poder do protocolo v1.1). A classificacao
de secoes por horario de encerramento exige logs ou metadados do 2T 2026, que
sao exatamente os dados-alvo do Estudo 03. Executar a parte empirica do Estudo
05 agora contaminaria o pre-registro aprovado.

Opcoes (decisao D4 em `PLANEJAMENTO.md`):

1. Manter o Estudo 05 empirico bloqueado ate o item 1.6 (recomendado).
2. Abrir antes apenas BU e totalizacao do 2T 2026 (reconciliacao BU x
   resultado divulgado), sem logs nem horarios, registrando a excecao por
   emenda.
3. Abrir integralmente, aceitando que o Estudo 03 perca o carater
   confirmatorio para o 2T 2026.

Decisao registrada em 29/10/2026: o proponente escolheu a opcao 1. A parte
empirica do Estudo 05 permanece bloqueada ate a aprovacao do item 1.6 do
Estudo 03. Ate la, o trabalho admissivel limita-se a: desenho e pre-registro
do Estudo 05; codigo testado com dados sinteticos; e execucao do mesmo
pipeline em dados ja abertos (2o turno municipal de 2024 e 1o turno de 2026)
como placebo e validacao.

## 5 Referencias

BRASIL. Tribunal Superior Eleitoral. **Eleicoes 2026**: mais de 34 mil votos
foram registrados apos as 17h no 2o turno. Brasilia, DF: TSE, 2026. Disponivel
em: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno.
Acesso em: 29 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Esclarecimento sobre prorrogacao da
votacao**. Brasilia, DF: TSE, 2026. Disponivel em:
https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/esclarecimento-sobre-prorrogacao-da-votacao.
Acesso em: 29 out. 2026.
