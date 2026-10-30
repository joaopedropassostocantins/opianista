# Estudo 05 - validacao de esquema, placebo 2T2024 (Palmas) e inventario de fontes de horario

Data: 29/10/2026. Status: EXPLORATORIO (placebo). Nenhum dado do 2T2026 foi
aberto (decisao D4). Dados brutos ficam em `data/`, fora do controle de versao.

## 1 Recursos oficiais examinados

| Recurso | URL | Last-Modified (HTTP) | SHA-256 do arquivo obtido |
|---|---|---|---|
| Votacao por secao 2024 TO | cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2024_TO.zip | 22/06/2026 | 9258920a27193be86b7fa679c30baaf41eb57f63bcf2941f69df326b36665060 |
| Votacao nominal por municipio e zona 2024 | cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2024.zip | 28/10/2026 | caabf63a5cd5d91b7fa651422edc2c27e5e5ae7979d08a1ed70800f02e7a2353 |
| Arquivos transmitidos 2T2024 TO | cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2024/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2024_2t_TO.zip | 27/10/2024 | 60bb950101018e25480b6e1a19103b51f10aaebdbad6296eff51f18ccd351696 |

Recursos de 2026 verificados apenas por metadados (requisicao HEAD e API CKAN,
sem download de conteudo):

| Recurso | Last-Modified | Conclusao |
|---|---|---|
| votacao_secao_2026_UF.zip e _BR.zip | 26/10/2026 | Regravados apos o 2T2026; presumivelmente reunem os dois turnos. **Nao abrir** (D4). |
| detalhe_votacao_secao_2026.zip | 26/10/2026 | Idem. **Nao abrir**. |
| bu_imgbu_logjez_rdv_vscmr_2026_1t_TO.zip (arquivos transmitidos, 1o turno) | 22/10/2026 | Gravado antes do 2T2026 e separado por turno no nome: **candidato a recurso isolado do 1T2026** (765 MB em TO). |
| bu_imgbu_logjez_rdv_vscmr_2026_2t_TO.zip | 26/10/2026 | 2T2026. **Bloqueado** (D4). |

Consequencia: o placebo 1T2026 nao pode usar o CSV `votacao_secao_2026`; deve
usar os arquivos transmitidos do 1o turno, decodificando o `bu.dat` (ASN.1) ou a
imagem do BU. A tentativa de localizar copia anterior ao 2T no Internet Archive
falhou por erro de conexao; nao verificado.

## 2 Validacao do esquema 2024

1. `votacao_secao_2024_TO.zip`: um CSV (cp1252, separador `;`) e um `leiame.pdf`.
   O CSV contem 1T e 2T no mesmo arquivo (270.223 linhas do 1T; 2.495 do 2T, so
   Palmas, cargo 11). Os nove campos exigidos pelo pipeline existem. Ha tambem
   `NR_LOCAL_VOTACAO`, que permite o efeito fixo de local sem cadastro externo.
2. Arquivos transmitidos 2T2024 TO: 629 secoes, cada uma com `bu.dat`,
   `imgbu.dat`, `rdv.dat`, `log.jez` (ZIP com `logd.dat`) e `vota.vsc`.
3. O `logd.dat` contem eventos desde a carga da urna e **o 1o turno inteiro**,
   alem do 2o. A extracao filtra pela data da eleicao. Implicacao para o
   Estudo 03: o log do 2T2026 trara tambem o 1T2026.
4. O log registra o numero do titulo de eleitor digitado para o encerramento
   (dado pessoal). `horarios_secao.py` nao copia essa linha; ha teste para isso.

## 3 Reconciliacoes

| Verificacao | Resultado |
|---|---|
| Soma por secao (votacao_secao) x agregado por zona (votacao_candidato_munzona), Palmas 2T2024 | Diferenca 0 para os dois candidatos (20: 78.673; 22: 69.684) |
| Votos computados no log x comparecimento no BU, 629 secoes | 0 divergencias |
| Fechamento na imagem do BU x "Procedimento de encerramento confirmado" no log | 616 identicos; 13 diferem em 1 segundo (arredondamento) |

As tres verificacoes confirmam coerencia **interna ao dominio do TSE e da urna**;
nao constituem fonte externa (ver `ANALISE_INSIDER_BU_TOTALIZACAO.md`).

## 4 Distribuicao dos horarios (relogio da urna, classe I)

| Evento | > 17h00 | > 17h10 | > 18h | > 19h | Maximo |
|---|---:|---:|---:|---:|---|
| Ultimo voto computado | 112 | 0 | 0 | 0 | 17:04:06 |
| Fechamento da UE (BU) | 629 | 2 | 0 | 0 | 17:12 |
| Inicio da geracao do bu.dat | 629 | 6 | 0 | 0 | 17:13 |

Achados:

1. **100% das secoes tem fechamento registrado depois das 17h00.** O controle
   "comprovadamente encerrada antes ou as 17h00" do pre-registro E05-0 (secao 1),
   se medido pelo fechamento, e vazio por construcao. Com o ultimo voto, ha 517
   secoes ate 17h00 e 112 depois (fila).
2. No placebo, as coortes >17h10 e >19h por ultimo voto sao vazias: o 2T2024 de
   Palmas nao serve de placebo para esses cortes, apenas para o contraste de fila
   (ultimo voto > 17h00).
3. 583 de 629 urnas registram abertura exatamente as 08:00:01. O agrupamento e
   compativel com abertura condicionada ao proprio relogio e, por isso, **nao
   detecta** desvio de relogio: uma urna adiantada tambem registraria 08:00:01.

## 5 Contraste exploratorio dentro do local de votacao

Modelo: `y_s = alpha_local + beta * T_s`, ponderado por votos validos, erro-padrao
agrupado por local (CR1); `T_s = 1` se o ultimo voto foi depois das 17h00;
`y_s` = fracao do candidato 20 nos votos validos da secao (todos os votos).

| Medida | Valor |
|---|---|
| Diferenca bruta (sem efeito fixo) | +0,56 p.p. |
| beta (efeito fixo de local) | +0,40 p.p. |
| Erro-padrao agrupado | 0,43 p.p. |
| IC 95% | -0,44 a +1,24 p.p. |
| Locais informativos / secoes informativas / tratadas | 56 / 521 / 111 |

Resultado nulo, como esperado num placebo sem prorrogacao. Com esse erro-padrao,
o efeito minimo detectavel (poder 80%, alfa 5%) e de cerca de 2,8 x 0,43 = 1,2 p.p.
num municipio. Para o candidato 22 o resultado e espelhado (-0,40 p.p.).
Implementacao: `horarios_secao.py`, `contraste_local.py`, testes em
`test_horarios_contraste.py`.

## 6 Inventario de fontes externas de horario

| Fonte | Publica em massa? | Independente do relogio da urna? | Uso possivel |
|---|---|---|---|
| imgbu, bu.dat, logd.dat, rdv | Sim | Nao (classe I) | Apenas analise condicional ao relogio |
| Horario de recebimento do BU na totalizacao | Nao localizado nos dados abertos | Sim quanto ao relogio; mesmo dominio institucional | Limite superior do encerramento; a investigar |
| Ata da mesa receptora | Nao (papel, sob guarda do cartorio) | Parcial (preenchida pelos mesarios) | Pedido via LAI para amostra |
| Fotos de BU por fiscais e aplicativos de partidos | Esparsa | Nao (o BU impresso traz o relogio da urna) | Nenhum para horario |
| Logs Gedai (preparacao) | Sim | Nao se aplica ao encerramento | Nenhum para horario |
| Imprensa e observadores | Esparsa, nao sistematica | Sim | Casos isolados, nao estimacao |

**Conclusao:** com fontes publicas nao existe confirmacao externa (classe E) do
horario de encerramento em escala. Pela regra do pre-registro E05-0 (secao 2), o
teste principal seria classificado **NAO TESTAVEL**. Para torna-lo estimavel ha
dois caminhos, ambos a decidir **antes do congelamento**:

1. Emenda com analise principal condicional ao relogio da urna (classe I), com
   verificacoes de coerencia (log x BU, fechamento x geracao do BU, ultimo voto x
   fechamento) e controle redefinido pelo ultimo voto, nao pelo fechamento.
2. Obter fonte externa: horario de recebimento por secao junto ao TSE e atas de
   amostra estratificada via Lei de Acesso a Informacao, como limite superior e
   validacao amostral do relogio.

## 7 Proximos passos

1. Decidir o caminho 1, o 2 ou ambos e redigir a alteracao do E05-0.
2. Placebo 1T2026: baixar `bu_imgbu_logjez_rdv_vscmr_2026_1t_TO.zip` (gravado em
   22/10/2026), conferir que o log so contem datas ate 04/10/2026 e o BU so o
   1o turno, e rodar o mesmo pipeline. Esse recurso serve tambem ao item 1.3 do
   Estudo 03.
3. Estender o placebo 2T2024 aos demais municipios com 2o turno (51 no pais),
   para estimar a heterogeneidade entre municipios exigida pelo plano de poder.

## 8 Extensao nacional do placebo 2T2024 (todos os municipios com 2o turno)

Atualizacao de 29/10/2026. Arquivos transmitidos do 2T2024 das 20 UFs que tiveram
2o turno (51 municipios), processados um a um e apagados apos a extracao. URL,
Last-Modified e SHA-256 de cada arquivo: `resultados/manifesto_arqurna_2T2024.tsv`.
Fonte dos votos e do local: imagem do BU (validada contra `votacao_secao` em
Palmas: 0 divergencias em 629 secoes). Desfecho: fracao do vencedor de cada
municipio nos votos validos da secao. Verificacoes de coerencia da emenda 01
aplicadas.

### 8.1 Cobertura e exclusoes

| Item | Valor |
|---|---:|
| Secoes extraidas | 97.391 |
| Excluidas: votos no log diferentes do comparecimento do BU | 132 |
| Excluidas: campo de horario ausente | 5 |
| Secoes usadas | 97.254 |

Nas 135 secoes em que o log tem menos votos que o BU (132 excluidas por esse
motivo e 3 entre as de campo ausente), o log comeca no meio do dia (exemplo:
primeiro voto as 14h55 em secao com 332 votantes). O padrao e compativel com
substituicao de urna, caso que a emenda 01 (secao 3, item 5) ja manda tratar
como indeterminado. Nao foi verificado individualmente.

### 8.2 Horarios (relogio da urna, classe I)

| Evento | > 17h00 | > 17h10 | > 18h | > 19h | Maximo |
|---|---:|---:|---:|---:|---|
| Ultimo voto computado | 9.059 | 13 | 0 | 0 | 17:57:54 |
| Fechamento da UE (BU) | 88.847 | 747 | 3 | 0 | 18:07:13 |

O fechamento depois das 17h00 ocorre em 91% das secoes (em Palmas, 100%). Em 2024
nao houve secao com ultimo voto depois das 19h: os cortes primario (> 19h) e
secundario (> 17h10, 13 secoes) sao **nao estimaveis** neste placebo. Apenas o
contraste de fila (ultimo voto > 17h00) e estimavel.

### 8.3 Contraste de fila dentro do local de votacao

| Medida | Valor |
|---|---|
| beta (fila x sem fila, efeito fixo de local) | -0,06 p.p. |
| Erro-padrao agrupado por local | 0,046 p.p. |
| IC 95% | -0,15 a +0,03 p.p. |
| Locais informativos / secoes informativas / tratadas | 4.614 / 55.472 / 9.020 |
| Municipios / municipios com secoes tratadas | 51 / 47 |
| Efeito minimo detectavel (80%, alfa 5%) | cerca de 0,13 p.p. |

Heterogeneidade entre os 47 municipios com ao menos 10 locais informativos:
Q de Cochran = 40,3 com 46 graus de liberdade, I2 = 0%. A dispersao das
estimativas municipais (desvio-padrao 0,49 p.p.) e compativel com erro amostral.

### 8.4 Leitura

1. Num pleito sem prorrogacao, secoes com fila nao diferem, em composicao de
   votos, das demais secoes do mesmo local. O desenho nao gera falso positivo
   neste placebo.
2. Com escala nacional, o desenho detecta diferencas da ordem de 0,1 a 0,2 p.p.
   no contraste de fila; esse valor alimenta o plano de poder do E05-0.
3. O placebo nao informa sobre os cortes de 17h10 e 19h, que nao ocorreram em
   2024. O poder para o contraste primario do 2T2026 dependera do numero de
   secoes com ultimo voto depois das 19h, ainda nao observado (D4).
4. Todos os horarios sao do relogio da urna; vale a limitacao descrita no
   README do Estudo 05.

## 9 Placebo 1T2026: trava acionada

O arquivo `bu_imgbu_logjez_rdv_vscmr_2026_1t_TO.zip` (Last-Modified 22/10/2026)
foi bloqueado pela trava da emenda 01 (secao 5.2): 14 de 4.384 logs tem eventos
entre 05/10 e 12/10/2026. Nenhum evento em ou apos 25/10/2026. So as datas foram
contadas; o arquivo foi apagado sem analise. Usar os arquivos do 1T2026 exige
emenda que troque o criterio por "nenhum evento em ou apos 25/10/2026". TO esta
excluido das analises confirmatorias do Estudo 05 pela emenda 02.
