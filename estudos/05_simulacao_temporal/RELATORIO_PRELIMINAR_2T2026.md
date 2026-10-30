# Relatório preliminar (versão 2): encerramento tardio das seções, prorrogação até 19h e composição dos votos no 2º turno de 2026

Projeto opianista. Estudo 05, com resultados do piloto do Estudo 03. Versão 2, de 30 de outubro de 2026, revisada a partir do parecer crítico do proponente (`PARECER_CRITICO_20261030.md`). Sujeita a revisão independente antes de qualquer divulgação.

## Resumo

Este relatório examina uma pergunta delimitada: se as seções eleitorais que encerraram a votação mais tarde no 2º turno das Eleições Gerais de 2026, inclusive as mantidas em funcionamento até 19h, apresentaram composição de votos diferente das demais seções do mesmo local de votação. Não se trata de auditoria abrangente da eleição. A unidade de análise é a seção, e o desfecho abrange todos os seus votos. Foram processados os arquivos públicos transmitidos para totalização de todas as unidades da Federação (499.178 seções). Os horários provêm do relógio da própria urna, convertidos para o horário de Brasília. Os dados reproduzem os números oficiais: a diferença de 798 votos nos totais de presidente corresponde a 70 seções do exterior ausentes dos arquivos transmitidos; os votos após 17h somam 34.330, ante 34.393 informados pelo Tribunal Superior Eleitoral. A prorrogação gerou pouca votação: 11 votos após 19h, ante 13 informados oficialmente, diferença ainda não reconciliada. Os contrastes confirmatórios, feitos dentro do local de votação, não identificaram associação estatisticamente significativa: último voto após 19h, +0,81 ponto percentual (IC 95%: -1,67 a +3,29; 11 seções); após 17h10, -0,08 p.p. (IC 95%: -0,27 a +0,12). Um contraste de calibração identificou efeito muito pequeno (-0,05 p.p.; p = 0,04), de magnitude semelhante à do placebo municipal de 2024; o contraste para governador após 19h não foi estimável. A diferença bruta de 3,5 p.p. nas seções que fecharam após 19h desaparece na comparação dentro do local. Os resultados dependem da exatidão dos registros da urna, não alcançam comprometimento uniforme do software e não substituem a calibração temporal por minuto exigida pela diretriz metodológica do projeto, que permanece pendente.

**Palavras-chave:** eleições 2026; urna eletrônica; boletim de urna; prorrogação da votação; inferência causal.

## 1 Introdução

No 2º turno de 25 de outubro de 2026, a votação foi mantida, por decisão excepcional, até 19h nas seções que ainda funcionavam às 17h. O Tribunal Superior Eleitoral (TSE) informou 6.766 seções encerradas depois das 19h e 34.393 votos registrados após 17h, sendo 32.399 entre 17h e 18h, 1.981 entre 18h e 19h e 13 após 19h (BRASIL, 2026a). A margem nacional foi de 4.430.191 votos.

A hipótese que motivou o estudo não se limita aos votos posteriores às 17h: se um agente com acesso privilegiado pudesse alterar a contabilização ou os horários registrados, a adulteração atingiria todos os votos das seções envolvidas. A pergunta deste relatório é, portanto, se as seções que permaneceram abertas por mais tempo diferem, na composição integral de seus votos, das seções comparáveis.

### 1.1 Escopo e limites deste relatório

Este relatório **não** constitui auditoria abrangente da eleição presidencial de 2026. Permanecem sem execução nacional: a cadência de votação por minuto ao longo de toda a jornada, as habilitações sem biometria, a análise de abstenção e de votos inválidos por seção, a detecção abrangente de anomalias e os ensaios de segurança (insider e cadeia de suprimentos). Um resultado nulo sobre encerramento tardio não equivale a resultado nulo de uma auditoria de integridade.

Há também uma limitação de identificabilidade: os testes usam registros produzidos pela própria urna (log, imagem do BU), e a hipótese investigada inclui a possibilidade de comprometimento desses registros. Coerência interna entre esses registros não é prova independente.

## 2 Hipóteses e protocolo

O protocolo foi pré-registrado (E05-0) e complementado por duas emendas, todas com SHA-256 em `protocolos/REGISTRO.md`. A diretriz metodológica 01, de 30/10/2026, veda o uso de segundos turnos presidenciais como referência de normalidade temporal; nenhum parâmetro deste relatório foi calibrado em turno presidencial: os contrastes são internos ao 2º turno de 2026 e o placebo usa o 2º turno municipal de 2024.

1. Hipótese nula: dentro de um mesmo local de votação, a diferença média da participação do candidato 13 nos votos válidos entre seções de encerramento tardio e seções encerradas até 17h é zero.
2. Contraste primário: último voto após 19h, comparado com último voto até 17h00.
3. Contraste secundário: último voto após 17h10, com o mesmo controle. Os dois recebem correção de Holm.
4. Contraste de calibração: último voto após 17h00 (fila), comparável ao placebo de 2024.
5. O Tocantins fica fora das análises confirmatórias (emenda 02); as seções no exterior também, porque lá a votação segue a hora local.

O encerramento da votação é definido pelo último voto computado no log (emenda 01). A classificação por fechamento é exploratória.

## 3 Dados e métodos

### 3.1 Fontes

Arquivos públicos "Arquivos transmitidos para totalização" do 2º turno de 2026 (28 arquivos, 124 GB) e do 2º turno de 2024 (20 unidades da Federação, 51 municípios), além do detalhamento oficial por município e zona de 2026 (BRASIL, 2026b). URL, data de gravação e SHA-256 de cada arquivo constam nos manifestos em `resultados/`. Os arquivos brutos não foram redistribuídos.

### 3.2 Extração

De cada seção foram extraídos, da imagem do boletim de urna (BU), o local, o comparecimento e os votos para presidente e governador; e, do log, o primeiro e o último voto computado, o encerramento confirmado, a geração do BU e um histograma de votos por hora. A linha do log com o título de eleitor do responsável pelo encerramento não foi copiada. Em Palmas (2024), os votos da imagem do BU coincidiram com o arquivo oficial por seção em 629 de 629 seções.

### 3.3 Eventos temporais distintos

São tratados como eventos diferentes, sem substituição de um pelo outro: último voto no log (relógio interno), encerramento confirmado (transição administrativa), fechamento declarado no BU, geração do BU, impressão, transmissão, recepção central e totalização. Este relatório usa apenas os quatro primeiros, todos do relógio da urna. A recepção central seria referência externa de processamento, mas não do horário do último voto, e não está nos dados abertos.

### 3.4 Horário de Brasília

O relógio da urna registra a hora local. A conversão foi feita por município, a partir da hora de abertura mais frequente, e confrontada com uma regra externa por unidade da Federação (Acre, -2 h; Amazonas, Rondônia, Roraima, Mato Grosso e Mato Grosso do Sul, -1 h; demais, 0). Dos 5.571 municípios, 12 divergem da regra por UF, e todos pertencem às regiões de exceção conhecidas: 11 no oeste do Amazonas (-2 h) e Fernando de Noronha (+1 h). A lista legal de municípios do oeste do Amazonas em UTC-5 ainda deve ser conferida em fonte normativa.

### 3.5 Verificações de coerência e população de auditoria

Separam-se duas populações. A **população estatística** reúne as 497.735 seções que passam nas verificações (votos no log iguais ao comparecimento do BU; fechamento e encerramento confirmado com diferença de até 2 segundos; ordem dos eventos). A **população de auditoria** inclui também as 1.443 seções restantes, inventariadas em `resultados/inventario_secoes_incoerentes_2T2026.csv`: 1.419 com menos votos no log que no BU (déficit total de 153.492 votos no log), 21 com campos ausentes e 3 com divergência temporal. Em 1.411 das 1.419, o log começa após 8h30, padrão compatível com substituição de urna; 8 permanecem sem explicação. Inconsistência não implica fraude, e a hipótese de substituição ainda não foi verificada nas atas.

### 3.6 Estimador

Modelo linear ponderado pelos votos válidos, com efeito fixo de local de votação e erro-padrão agrupado por local.

## 4 Resultados

### 4.1 Validação contra os números oficiais

| Verificação | Dados extraídos | Número oficial | Diferença |
|---|---:|---:|---:|
| Votos de Lula (13) nos BUs | 64.255.787 | 64.256.232 | -445 |
| Votos de Flávio (22) nos BUs | 59.825.688 | 59.826.041 | -353 |
| Comparecimento | 128.235.243 | 128.236.074 | -831 |
| Votos entre 17h e 18h | 32.337 | 32.399 | -62 |
| Votos entre 18h e 19h | 1.982 | 1.981 | +1 |
| Votos após 19h | 11 | 13 | -2 |
| Seções com geração do BU após 19h | 6.858 | 6.766 | +92 |
| Votos após 17h nessas seções | 4.722 | 4.773 | -51 |

A diferença de 831 no comparecimento está inteiramente no exterior (27 zonas): o TSE lista 499.248 seções principais e os arquivos transmitidos contêm 499.178; as 70 seções do exterior ausentes explicam a diferença. As contagens por horário aproximam-se mais das oficiais quando o "encerramento" é a geração do BU do que quando é o fechamento declarado (6.336 seções); o TSE não especifica o evento. A diferença de 2 votos após 19h ainda não foi reconciliada evento por evento.

### 4.2 O que ocorreu depois das 17h e das 19h

| Evento (horário de Brasília) | Após 17h | Após 17h10 | Após 18h | Após 19h |
|---|---:|---:|---:|---:|
| Último voto, 2T 2026 (seções) | 29.609 (5,9%) | 2.961 | 1.667 | 11 |
| Fechamento da urna, 2T 2026 (seções) | 497.897 (100%) | 13.356 | 7.086 | 6.336 |
| Último voto, 2T municipal 2024 (seções) | 10.546 (10,8%) | 16 | 0 | 0 |

Os 11 votos após 19h ocorreram em 11 seções, um em cada (BA, RJ e SP). Das 6.336 seções que fecharam após 19h, o último voto ocorreu, em mediana, às 16h59: a maioria permaneceu aberta sem receber eleitores. Essas seções concentram-se no Rio de Janeiro (2.799), em São Paulo (1.567), na Bahia (933), em Pernambuco (657) e na Paraíba (272). A contagem de votos por hora de 2024 não está disponível, porque a extração de 2024 antecede o campo de histograma; o valor zero que constava da versão 1 era um defeito e foi removido.

### 4.3 Placebo: 2º turno municipal de 2024

Sem prorrogação, as seções com fila após 17h não diferiram significativamente das demais do mesmo local: -0,07 p.p. (IC 95%: -0,16 a +0,01; p = 0,08; 5.242 locais).

### 4.4 Contrastes pré-registrados no 2º turno de 2026

| Contraste | Estimativa (p.p.) | IC 95% | p | p (Holm) | Seções tratadas |
|---|---:|---|---:|---:|---:|
| Primário: último voto após 19h | +0,81 | -1,67 a +3,29 | 0,52 | 0,89 | 11 |
| Secundário: último voto após 17h10 | -0,08 | -0,27 a +0,12 | 0,44 | 0,89 | 2.923 |
| Calibração: último voto após 17h00 | -0,05 | -0,11 a -0,002 | 0,04 | não se aplica | 29.287 |
| Governador: último voto após 19h | não estimável | - | - | - | 0 |

Os contrastes confirmatórios não identificaram associação estatisticamente significativa. O primário tem poder muito baixo (11 seções). O contraste de calibração, fora da família confirmatória, identificou efeito muito pequeno e estatisticamente detectável, de magnitude semelhante à do placebo de 2024 (-0,07 p.p.), o que sugere característica estrutural das seções com fila, e não efeito da prorrogação; essa leitura é uma interpretação, não um teste. O contraste do governador após 19h não foi estimável, por ausência de locais com seções tratadas.

### 4.5 Contrastes exploratórios

| Contraste | Estimativa (p.p.) | IC 95% | Seções tratadas |
|---|---:|---|---:|
| Fechamento após 19h x fechamento até 17h10 | -0,04 | -0,26 a +0,19 | 6.304 |
| Fechamento após 17h10 x fechamento até 17h05 | +0,01 | -0,11 a +0,14 | 13.225 |
| Governador, último voto após 17h00 | -0,08 | -0,25 a +0,10 | 2.512 |

Nenhum desses contrastes foi estatisticamente significativo.

### 4.6 Comparação bruta e comparação dentro do local

Nas seções que fecharam após 19h, o candidato 13 obteve 55,2% dos votos válidos; nas demais, 51,7%. A diferença bruta, de 3,5 p.p., desaparece na comparação dentro do local de votação (-0,04 p.p.), o que indica que decorre da localização dessas seções.

### 4.7 Materialidade

| Coorte | Votos válidos | Fração mínima a transferir para inverter a margem |
|---|---:|---:|
| Último voto após 19h | 3.273 | 677 vezes o total da coorte |
| Último voto após 17h10 | 842.888 | 2,63 vezes |
| Fechamento após 19h | 1.789.091 | 1,24 vez |
| Último voto após 17h00 | 7.767.196 | 28,5% |

Uma transferência de votos exclusivamente entre os dois finalistas, limitada aos votos válidos registrados nas seções identificadas como tardias pelo critério utilizado, não seria suficiente para inverter a margem nacional nas três primeiras coortes. Esse limite vale apenas para esse mecanismo: não exclui alterações distribuídas entre seções de outros horários nem comprometimento anterior à geração do BU, e a própria classificação das coortes depende do relógio da urna.

### 4.8 Abstenção e votos inválidos entre os turnos

| Indicador | 1º turno | 2º turno | Variação |
|---|---:|---:|---:|
| Comparecimento | 125.275.835 | 128.236.074 | +2.960.239 |
| Abstenção | 33.469.244 (21,08%) | 30.509.005 (19,22%) | -1,86 p.p. |
| Brancos e nulos | 5.975.047 | 4.153.801 | -1.821.246 |
| Lula (13) | 53.879.538 | 64.256.232 | +10.376.694 |
| Flávio (22) | 56.104.503 | 59.826.041 | +3.721.538 |
| Votos dos eliminados | 9.316.747 | - | - |

Fonte dos números: detalhamento oficial por município e zona do TSE. A identidade contábil fecha: o crescimento conjunto dos finalistas (14.098.232) é igual à soma dos votos dos eliminados (9.316.747), do aumento do comparecimento (2.960.239) e da redução de brancos e nulos (1.821.246). O fechamento contábil não explica comportamento: não identifica quais eleitores mudaram de candidato nem quem deixou de se abster. Uma regressão ecológica exploratória por município produziu coeficientes fora do intervalo admissível (por exemplo, 1,42 e -0,21), o que mostra que o modelo linear simples é inadequado para estimar transferências; a inferência ecológica apropriada fica para o Estudo 02.

### 4.9 Estudo 03: hipótese do mesário (piloto no Tocantins)

No Tocantins, nenhum teste da família pré-registrada rejeitou a hipótese nula (q = 1,0). Pela diretriz metodológica 01, porém, os componentes que usam o 2º turno presidencial de 2022 como referência (H1a e o diagnóstico de poder) passam a descritivos, e a conclusão desse piloto não pode ser apresentada como teste contra referência independente. Fora do Tocantins, o Estudo 03 é exploratório.

## 5 Discussão e limitações

1. Identificabilidade: os testes usam registros da própria urna; um relógio incorreto, ou um software que registrasse horários ou votos falsos de forma coerente, passaria em todas as verificações internas.
2. Comprometimento uniforme do software, que afetasse todas as urnas igualmente, não é detectável pelo contraste dentro do local.
3. A conciliação entre BU e totalização foi feita por zona e no agregado nacional, não por seção contra cópias independentes do BU.
4. O contraste primário tem poder muito baixo, porque o fenômeno quase não ocorreu (11 seções).
5. Estimativas dentro do local reduzem, mas não eliminam, o confundimento.
6. As 1.443 seções da população de auditoria foram excluídas dos contrastes; a causa de 8 delas não foi identificada.
7. A cadência por minuto, as habilitações sem biometria em escala nacional e a calibração temporal pelos grupos de referência da diretriz 01 não foram executadas.
8. O pré-registro foi redigido após o conhecimento dos agregados nacionais; o caráter prospectivo limita-se aos microdados por seção.

## 6 Conclusões preliminares

1. Os dados públicos de urna reproduzem os totais oficiais; a diferença de 798 votos é explicada por 70 seções do exterior ausentes dos arquivos transmitidos.
2. A prorrogação até 19h gerou pouca votação: 11 votos após 19h nos dados extraídos (13 segundo o TSE), em seções que, na maioria, ficaram abertas sem eleitores.
3. Os contrastes confirmatórios não identificaram associação estatisticamente significativa entre encerramento tardio e composição dos votos; o contraste de calibração identificou efeito muito pequeno, semelhante ao do placebo; o contraste do governador após 19h não foi estimável.
4. A diferença bruta de 3,5 p.p. nas seções abertas até 19h é compatível com a localização dessas seções.
5. Uma transferência entre os dois finalistas restrita às coortes tardias, tal como classificadas, não alcançaria a margem nacional.
6. Essas conclusões dizem respeito ao encerramento tardio, sob a hipótese de registros corretos da urna. A hipótese de comportamento temporal atípico nas eleições presidenciais permanece não testada de forma abrangente diante do paradigma histórico definido na diretriz 01.

## 7 Próximos passos

1. Reconciliar evento por evento os 2 votos após 19h e os 62 votos entre 17h e 18h.
2. Extrair a série por minuto de habilitações e votos de toda a jornada e reextrair 2024 com o histograma.
3. Construir as referências da diretriz 01: levantar documentação de eleições anteriores à urna eletrônica (1990, 1992, 1994), registrando como não observados os parâmetros sem fonte; consolidar segundos turnos municipais (2000 a 2024) e estaduais.
4. Estimar o modelo de intensidade por minuto nas referências e aplicá-lo ao 2º turno de 2026, com poder estatístico e controles negativos.
5. Verificar nas atas a causa das 1.443 seções da população de auditoria.
6. Enviar o pedido de acesso à informação sobre recepção dos BUs e atas.
7. Inferência ecológica adequada da transferência de votos (Estudo 02).
8. Revisão independente do código e do relatório.

## Referências

BRASIL. Tribunal Superior Eleitoral. **Eleições 2026**: mais de 34 mil votos foram registrados após as 17h no 2º turno. Brasília, DF: TSE, 2026a. Disponível em: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno. Acesso em: 30 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Portal de Dados Abertos do TSE**: resultados 2026, detalhamento por município e zona e arquivos transmitidos para totalização. Brasília, DF: TSE, 2026b. Disponível em: https://dadosabertos.tse.jus.br. Acesso em: 30 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Esclarecimento sobre prorrogação da votação**. Brasília, DF: TSE, 2026c. Disponível em: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/esclarecimento-sobre-prorrogacao-da-votacao. Acesso em: 30 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Resolução nº 23.751, de 26 de fevereiro de 2026**. Brasília, DF: TSE, 2026d. Disponível em: https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-751-de-26-de-fevereiro-de-2026. Acesso em: 30 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Portal de Dados Abertos do TSE**: resultados 2024 e arquivos transmitidos para totalização. Brasília, DF: TSE, 2024. Disponível em: https://dadosabertos.tse.jus.br/dataset/resultados-2024. Acesso em: 30 out. 2026.
