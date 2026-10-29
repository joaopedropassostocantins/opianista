# Relatório preliminar: encerramento tardio das seções, prorrogação até 19h e composição dos votos no 2º turno de 2026

Projeto opianista. Estudo 05, com resultados do piloto do Estudo 03. Versão preliminar de 29 de outubro de 2026, sujeita a revisão (red team) antes de qualquer divulgação.

## Resumo

Este relatório examina se as seções eleitorais que encerraram a votação mais tarde no 2º turno das Eleições Gerais de 2026, inclusive aquelas mantidas em funcionamento até 19h por decisão excepcional, apresentaram composição de votos diferente das demais seções do mesmo local de votação. A unidade de análise é a seção, e o desfecho abrange todos os votos de cada seção, e não apenas os registrados após 17h. Foram processados os arquivos públicos transmitidos para totalização de todas as unidades da Federação: 499.178 seções, com imagem do boletim de urna e log da urna eletrônica. Os horários provêm do relógio da própria urna, convertidos para o horário de Brasília. Os dados extraídos reproduzem os números oficiais: a soma dos boletins difere em 798 votos dos totais oficiais de presidente (0,0006%), e a contagem de votos após 17h (34.330) difere em 0,18% da informada pelo Tribunal Superior Eleitoral (34.393). A prorrogação teve efeito material mínimo sobre a votação: 6.336 seções fecharam após 19h, mas o último voto dessas seções ocorreu, em mediana, às 16h59, e apenas 11 votos foram registrados no país após 19h. Nos contrastes pré-registrados, realizados dentro do local de votação, não se observou diferença estatisticamente significativa: último voto após 19h, +0,81 ponto percentual (IC 95%: -1,67 a +3,29; 11 seções); após 17h10, -0,08 p.p. (IC 95%: -0,27 a +0,12). O contraste exploratório com todas as seções que fecharam após 19h resultou em -0,04 p.p. (IC 95%: -0,26 a +0,19). A diferença bruta de 3,5 p.p. a favor do candidato 13 nessas seções decorre de sua concentração geográfica e desaparece na comparação dentro do local. O placebo do 2º turno municipal de 2024, sem prorrogação, também foi nulo. Mesmo a transferência de todos os votos das seções que fecharam após 19h não alteraria o resultado. A conclusão é condicionada à exatidão do relógio da urna e não alcança hipóteses de comprometimento uniforme do software.

**Palavras-chave:** eleições 2026; urna eletrônica; boletim de urna; prorrogação da votação; inferência causal.

## 1 Introdução

No 2º turno de 25 de outubro de 2026, a votação foi mantida, por decisão excepcional, até 19h nas seções que ainda funcionavam às 17h. O Tribunal Superior Eleitoral (TSE) informou que 497.333 seções encerraram depois das 17h, 24.268 depois das 17h10 e 6.766 depois das 19h, e que 34.393 votos foram registrados após 17h (BRASIL, 2026a). A margem nacional foi de 4.430.191 votos.

A hipótese que motivou o estudo não se limita aos votos posteriores às 17h. Se um agente com acesso privilegiado (insider) pudesse alterar a contabilização ou os horários registrados, a eventual adulteração atingiria a totalidade dos votos das seções envolvidas. Por isso, a pergunta central é: as seções que permaneceram abertas por mais tempo apresentam, na composição integral de seus votos, diferenças não explicadas por fatores eleitorais e operacionais?

## 2 Hipóteses e protocolo

O protocolo foi pré-registrado (E05-0) e complementado por duas emendas, todas com SHA-256 em `protocolos/REGISTRO.md`, antes da abertura dos microdados do 2º turno de 2026 fora do Tocantins.

1. Hipótese nula: dentro de um mesmo local de votação, a diferença média da participação do candidato 13 nos votos válidos entre seções de encerramento tardio e seções encerradas até 17h é zero.
2. Contraste primário: último voto após 19h, comparado com último voto até 17h00.
3. Contraste secundário: último voto após 17h10, com o mesmo controle. Os dois contrastes recebem correção de Holm.
4. Contraste de calibração: último voto após 17h00 (fila), comparável ao placebo de 2024.
5. O Tocantins fica fora das análises confirmatórias, porque seus microdados foram examinados antes no Estudo 03 (emenda 02). As seções no exterior ficam fora porque lá a votação segue a hora local.

O encerramento da votação é definido pelo horário do último voto computado no log, e não pelo fechamento da urna, que inclui procedimentos administrativos posteriores (emenda 01). A classificação por fechamento é apresentada como análise exploratória, por corresponder ao critério divulgado pelo TSE.

## 3 Dados e métodos

### 3.1 Fontes

Foram usados os arquivos públicos "Arquivos transmitidos para totalização" do 2º turno de 2026 (28 arquivos, 27 unidades da Federação e exterior, 124 GB) e do 2º turno de 2024 (20 unidades da Federação com 2º turno municipal, 51 municípios), obtidos no portal de dados abertos do TSE (BRASIL, 2026b). Para cada arquivo, a URL, a data de gravação e o SHA-256 estão em `resultados/manifesto_arqurna_2T2026.tsv` e `resultados/manifesto_arqurna_2T2024.tsv`. Os arquivos brutos não foram redistribuídos.

### 3.2 Extração

De cada seção foram extraídos, da imagem do boletim de urna (BU), o local de votação, o comparecimento e os votos para presidente e governador; e, do log da urna, o primeiro e o último voto computado, o encerramento confirmado, a geração do BU e um histograma de votos por hora. A linha do log que registra o título de eleitor do responsável pelo encerramento não foi copiada. Em Palmas (2024), os votos extraídos da imagem do BU coincidiram com o arquivo oficial de votação por seção em 629 de 629 seções.

### 3.3 Horário de Brasília

O relógio da urna registra a hora local, enquanto a votação segue o horário de Brasília. A conversão foi feita por município, a partir da hora de abertura mais frequente (8h de Brasília). Exemplo: no Acre, as urnas abriram às 6h locais.

### 3.4 Verificações de coerência

Foram excluídas as seções em que o número de votos no log difere do comparecimento do BU (padrão compatível com substituição de urna), em que fechamento e encerramento confirmado divergem em mais de 2 segundos, ou em que a ordem dos eventos é incompatível. Em 2026, 497.735 das 499.178 seções passaram nas verificações.

### 3.5 Estimador

Modelo linear ponderado pelos votos válidos, com efeito fixo de local de votação e erro-padrão agrupado por local: a diferença é estimada apenas entre seções do mesmo local, o que neutraliza a composição territorial do eleitorado.

## 4 Resultados

### 4.1 Validação contra os números oficiais

| Verificação | Dados extraídos | Número oficial | Diferença |
|---|---:|---:|---:|
| Votos de Lula (13) nos BUs | 64.255.787 | 64.256.232 | -445 |
| Votos de Flávio (22) nos BUs | 59.825.688 | 59.826.041 | -353 |
| Votos registrados após 17h | 34.330 | 34.393 | -63 (0,18%) |
| Seções com geração do BU após 19h | 6.858 | 6.766 (encerramento após 19h) | +92 |

A diferença de 798 votos nos totais (0,0006%) ainda não foi explicada; pode corresponder a seções ausentes dos arquivos transmitidos. As contagens de seções por horário dependem do evento usado como "encerramento", que o TSE não especifica.

### 4.2 O que ocorreu depois das 17h e das 19h

| Evento (horário de Brasília) | Após 17h | Após 17h10 | Após 18h | Após 19h |
|---|---:|---:|---:|---:|
| Último voto, 2T 2026 | 29.609 (5,9%) | 2.961 | 1.667 | 11 |
| Fechamento da urna, 2T 2026 | 497.897 (100%) | 13.356 | 7.086 | 6.336 |
| Último voto, 2T municipal 2024 | 10.546 (10,8%) | 16 | 0 | 0 |

Das 6.336 seções que fecharam após 19h, o último voto ocorreu, em mediana, às 16h59 (percentil 90: 18h29). Essas seções permaneceram abertas, em sua maioria, sem receber eleitores. Foram registrados 11 votos após 19h em todo o país. As seções que fecharam após 19h concentram-se no Rio de Janeiro (2.799), em São Paulo (1.567), na Bahia (933), em Pernambuco (657) e na Paraíba (272).

Comparado ao 2º turno municipal de 2024, o 2º turno de 2026 teve proporção menor de seções com fila após 17h (5,9% contra 10,8%); com a prorrogação, porém, 1.667 seções ainda votaram após 18h, o que não ocorreu em 2024.

### 4.3 Placebo: 2º turno municipal de 2024

Sem prorrogação, as seções com fila após 17h não diferiram das demais do mesmo local: -0,07 p.p. (IC 95%: -0,16 a +0,01; 5.242 locais). Não houve seção com último voto após 17h10 em número suficiente para os cortes principais.

### 4.4 Contrastes pré-registrados no 2º turno de 2026

| Contraste | Estimativa (p.p.) | IC 95% | p | p (Holm) | Seções tratadas |
|---|---:|---|---:|---:|---:|
| Primário: último voto após 19h | +0,81 | -1,67 a +3,29 | 0,52 | 0,89 | 11 |
| Secundário: último voto após 17h10 | -0,08 | -0,27 a +0,12 | 0,44 | 0,89 | 2.923 |
| Calibração: último voto após 17h00 | -0,05 | -0,11 a -0,002 | 0,04 | não se aplica | 29.287 |

Nenhum contraste confirmatório rejeitou a hipótese nula. O contraste primário é estimável, mas tem poder muito baixo, porque apenas 11 seções votaram após 19h. O contraste de calibração tem sinal e magnitude semelhantes aos do placebo de 2024 (-0,07 p.p.), o que indica um efeito estrutural pequeno das seções com fila, presente sem prorrogação, e não um efeito associado à extensão.

### 4.5 Contrastes exploratórios

| Contraste | Estimativa (p.p.) | IC 95% | Seções tratadas |
|---|---:|---|---:|
| Fechamento após 19h x fechamento até 17h10 | -0,04 | -0,26 a +0,19 | 6.304 |
| Fechamento após 17h10 x fechamento até 17h05 | +0,01 | -0,11 a +0,14 | 13.225 |
| Governador, último voto após 17h00 | -0,08 | -0,25 a +0,10 | 2.512 |

O contraste com fechamento após 19h corresponde ao critério divulgado pelo TSE e abrange todos os votos das seções que permaneceram abertas até 19h. Não houve diferença.

### 4.6 Por que a comparação bruta engana

Nas seções que fecharam após 19h, o candidato 13 obteve 55,2% dos votos válidos; nas demais, 51,7%. A diferença bruta, de 3,5 p.p., desaparece na comparação dentro do local de votação (-0,04 p.p.). Ela decorre da localização dessas seções, concentradas em regiões metropolitanas de RJ, SP, BA e PE, e não do horário de encerramento.

### 4.7 Materialidade

| Coorte | Votos válidos | Fração mínima a transferir para inverter a margem |
|---|---:|---:|
| Último voto após 19h | 3.273 | 677 vezes o total da coorte (impossível) |
| Último voto após 17h10 | 842.888 | 2,63 vezes (impossível) |
| Fechamento após 19h | 1.789.091 | 1,24 vez (impossível) |
| Último voto após 17h00 | 7.767.196 | 28,5% |

Nem a transferência integral dos votos das seções que permaneceram abertas até 19h alteraria o resultado. Uma alteração dessa ordem nas seções com fila (28,5%) seria incompatível com as diferenças observadas, da ordem de 0,05 p.p.

### 4.8 Estudo 03: hipótese do mesário (piloto no Tocantins)

No Tocantins, nenhuma hipótese da família pré-registrada foi sustentada (q = 1,0 em todos os testes). O excesso de habilitações sem biometria no fim do dia foi menor em 2026 do que em 2022, nenhuma seção apresentou duas ou mais rajadas de habilitações e a última habilitação do 2º turno de 2026 ocorreu às 17h11. O resultado vale para inserções a partir de cerca de 10 habilitações sem biometria por seção. Fora do Tocantins, o Estudo 03 passou a exploratório.

## 5 Discussão e limitações

1. Os horários provêm do relógio da urna. Um relógio incorreto, ou um software que registrasse horários falsos, produziria registros coerentes entre si e passaria em todas as verificações internas.
2. O desenho compara seções tardias com seções do mesmo local. Um comprometimento uniforme do software, que afetasse todas as urnas igualmente, não seria detectado por esse contraste.
3. A conciliação entre BU e totalização foi feita no agregado nacional (diferença de 798 votos) e não por seção contra cópias independentes do BU.
4. O contraste primário (após 19h) tem poder muito baixo, porque o fenômeno quase não ocorreu: 11 seções.
5. Estimativas dentro do local reduzem, mas não eliminam, o confundimento.
6. O pré-registro foi redigido após o conhecimento dos agregados nacionais; o caráter prospectivo limita-se aos microdados por seção.

## 6 Conclusões preliminares

1. Os dados públicos de urna reproduzem os totais oficiais e as contagens divulgadas pelo TSE.
2. A prorrogação até 19h quase não gerou votação: 6.336 seções permaneceram abertas, mas apenas 11 votos foram registrados após 19h.
3. Em nenhum contraste, pré-registrado ou exploratório, as seções de encerramento tardio diferiram, na composição integral de seus votos, das seções do mesmo local.
4. A diferença bruta de 3,5 p.p. nas seções abertas até 19h é explicada pela geografia.
5. Nenhuma alteração restrita às seções de encerramento tardio poderia ter invertido o resultado.
6. Essas conclusões não demonstram a ausência de qualquer adulteração. Elas afastam, com os dados públicos e sob a hipótese de relógio correto, a hipótese de que a prorrogação tenha sido usada para alterar os votos das seções envolvidas.

## 7 Próximos passos

1. Revisão independente (red team) deste relatório e do código.
2. Explicar a diferença de 798 votos entre a soma dos BUs e os totais oficiais.
3. Enviar o pedido de acesso à informação sobre o horário de recebimento dos BUs e sobre as atas, para validar o relógio da urna por fonte externa.
4. Conciliar BU por seção com cópias independentes (BU impresso ou QR Code coletado por fiscais).
5. Execução nacional exploratória do Estudo 03 nas UFs com votação após 17h49.

## Referências

BRASIL. Tribunal Superior Eleitoral. **Eleições 2026**: mais de 34 mil votos foram registrados após as 17h no 2º turno. Brasília, DF: TSE, 2026a. Disponível em: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno. Acesso em: 29 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Portal de Dados Abertos do TSE**: resultados 2026 e arquivos transmitidos para totalização. Brasília, DF: TSE, 2026b. Disponível em: https://dadosabertos.tse.jus.br. Acesso em: 29 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Esclarecimento sobre prorrogação da votação**. Brasília, DF: TSE, 2026c. Disponível em: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/esclarecimento-sobre-prorrogacao-da-votacao. Acesso em: 29 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Resolução nº 23.751, de 26 de fevereiro de 2026**. Brasília, DF: TSE, 2026d. Disponível em: https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-751-de-26-de-fevereiro-de-2026. Acesso em: 29 out. 2026.

BRASIL. Tribunal Superior Eleitoral. **Portal de Dados Abertos do TSE**: resultados 2024 e arquivos transmitidos para totalização. Brasília, DF: TSE, 2024. Disponível em: https://dadosabertos.tse.jus.br/dataset/resultados-2024. Acesso em: 29 out. 2026.
