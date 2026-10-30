# Pré-registro Estudo 05 — coortes de seções com encerramento tardio, BU integral e confiabilidade do horário

**Versão:** 1.0 — congelamento proposto em 29/10/2026, antes da abertura de microdados de seção do segundo turno de 2026 por este estudo.
**Status:** texto pré-especificado para revisão e aprovação humana de GATE E05-0. Não declara autorização para abrir a base-alvo.
**Decisão vinculante:** D4 em PLANEJAMENTO.md: **nenhum BU, log, horário, tabela de totalização ou microdado de seção do 2T2026 será aberto para este ou outro estudo antes do GATE 1.6 do Estudo 03**.
**Exposição prévia incontornável:** já são conhecidos os resultados **nacionais** do 2T2026 (64.256.232 e 59.826.041 votos, margem 4.430.191), a divulgação de 34.393 votos depois das 17h e as contagens **agregadas de seções** por horário (>17h, >17h10, >19h). Isso significa que este documento **não foi redigido em cegamento absoluto**; o registro será considerado prospectivo apenas para os **microdados por seção ainda bloqueados**. Reconhecer também os dados de amostra de 2,1% mencionados no planejamento, cujo conteúdo e alcance ainda não foram reconstruídos; não declarar ausência de exposição completa até auditar isso. Se o proponente já visualizou tabelas por seção do 2T2026, listar a exposição antes de aprovar o GATE.

## 1. Pergunta e estimando

A unidade observacional é a **seção eleitoral**; exposição é o encerramento tardio confirmado do processo de **votação**, não o horário de um voto nem a hora da transmissão. Para cada seção exposta, incluir **todos os votos do BU para presidente**, sem filtrar votos por timestamp. Se a única hora disponível for emissão do BU ou finalização técnica, ela não classifica a seção como "votação tardia" no teste principal.

**Hipótese nula H0 (comparação interna ao local):** dentro de um mesmo local de votação, a diferença média da participação do candidato A nos votos válidos entre seções comprovadamente tardias e contemporâneas não tardias é zero após o ajuste pré-especificado. É teste de **associação**, não demonstração de causalidade ou fraude.

**Alternativa bilateral H1:** a diferença média ajustada é diferente de zero. Sem direção pré-fixada, sem seleção de localidades por sinal ou significância. **A = candidato 13 (Lula), B = candidato 22 (Flávio)** no 2T2026; o contraste é bilateral e simétrico, com interpretação de sinais espelhada para ambos.

**Alvo primário:** seções cujo **encerramento da votação** está comprovado externamente após **19h00**, comparadas com seções do mesmo local comprovadamente encerradas antes ou às 17h00 (grupo de controle estrito) e elegíveis ao mesmo tratamento operativo, quando identificável. A definição estrita é deliberada: ela pode eliminar grande parte da amostra. Se não houver sobreposição suficiente, o teste primário será classificado **não estimável**, sem substituição oportunista do critério. Seções encerradas entre 17h00 e 19h00 não são controle estrito.

**Secundário, com teste separado:** encerramento de votação externamente confirmado após **17h10**, contra seções comprovadamente encerradas até 17h00 no mesmo local. O corte 17h10 é limiar de pesquisa, não uma regra legal. Outros cortes (18h, 19h com horário técnico, emissão do BU) só exploratórios. **Não** confundir 6.766 seções com "encerramento técnico após 19h" com eleitores votando até 19h.

## 2. Classificação cega, confirmação externa e indeterminado

Campo obrigatório por seção: tipo de relógio e evento, qualidade da fonte, fuso, precisão, hora do último voto quando documentada, hora de encerramento da votação, início e fim da geração do BU, impressão e transmissão/recebimento quando observáveis. Nenhuma variável ausente será substituída por valor zero.

- **Confirmado externo (classe E):** registro contemporâneo independente do software sob exame e idôneo para documentar **fim da votação**, verificável com identificação da seção e hora. A assinatura do mesário, isoladamente, pode ser dependente da hipótese de conluio operacional e requer avaliação de proveniência; horários provenientes exclusivamente do BU, do log ou da totalização **não são fonte externa**.
- **Interno apenas (classe I):** horário presente em log/BU/resultado, sem fonte independente. Pode integrar análise **descritiva exploratória**, nunca H0 principal.
- **Conflito (classe C):** fontes discordam em mais de 1 minuto ou atravessam o limiar; classificar **indeterminado** para H0; apresentar discrepância e seu sinal, sem imputação.
- **Ausente/ambíguo (classe U):** sem confirmação independente da hora de encerramento da votação; classificar **indeterminado** para H0, não "fechado antes de 17h" e não "fora da eleição".
- **Contingência:** substituição da urna, agregação de seções, horário de relatório confundido com último voto: classe indeterminada até reconciliar identidade e sequência; listar exclusões por motivo.

**Se não existir evidência externa suficiente para qualquer grupo, relatar H0 = NÃO TESTÁVEL.** Não alterar regra para produzir p-valor.

## 3. Pareamento, controles e exclusões

Chave da seção: ano, turno, UF, município, zona, número da seção, cargo e correspondência entre seção agregadora/agregada. Chave de **local de votação** deve ser obtida de cadastro oficial de locais, não presumida pela zona nem pelo município. Excluir do estimador principal locais sem ID confiável, com menos de uma seção de cada classe, ou sem concatenação verificável entre BU e local. Publicar tabelas de perdas antes de estimar.

Covariáveis pré-especificadas: eleitores aptos, comparecimento/aptos, modelo da urna, agregação, contingência/substituição, número de seções no local; **possíveis variáveis pós-tratamento**, como comparecimento ou contingência, serão informadas também em análise sem ajuste para evitar viés de pós-tratamento. Para a análise primária, ajuste somente aptos, modelo de urna, tamanho do local e identificadores pré-pleito verificáveis. Turnout e contingência entram como sensibilidade, não como requisito para estimar.

O encerramento tardio não é aleatório. Diferença de perfil político em seções próximas, horários auto-relatados e falhas de classificação podem gerar artefatos. Para a cadência de filas, paradigma histórico prioritário: **segundos turnos municipais**, sem eleger eleições presidenciais anteriores como controle histórico de fila.

## 4. Estimador e inferência

Desfecho da seção: \(y_s=v_{13,s}/(v_{13,s}+v_{22,s})\), considerando **todos os votos válidos presidenciais** da seção; excluir do modelo de participação apenas se o denominador for zero (registrar quantas, nunca converter para 0%). Desfechos adicionais separados: comparecimento/aptos, votos brancos/comparecimento e nulos/comparecimento.

Modelo linear de probabilidade agregada por seção, ponderado pelo número de votos válidos: \(y_s=\alpha_{local(s)}+\beta T_s+\gamma X_s+\epsilon_s\). Efeitos fixos do **local**; covariáveis de pré-pleito; erro-padrão robusto agrupado pelo local (mínimo de 30 locais com ambas as classes). Relatar IC 95%, p-valor bilateral, tamanho efetivo por grupo, dispersões e pesos. Se menos de 30 locais válidos: não reportar p confirmatório, usar estimativa descritiva e intervalo por bootstrap de locais apenas como exploração. Teste bilateral 5% para único contraste primário (>19h); secundário >17h10 com ajuste Holm sobre o conjunto primário+secundário quando ambos estimáveis, ou declarar secundário exclusivamente exploratório após o primário não estimável. Por simplicidade conservadora, usar **Holm 5% para os dois contrastes quando ambos estimáveis**; não selecionar testes pelo resultado.

Plano de poder: simular diferenças de 0,5; 1; 2; 5 pontos percentuais, por amostragem de locais com a heterogeneidade estimada dos placebos, antes de examinar microdados 2T2026. Fixar a seed 20261029 e 2000 reamostragens. A ausência de poder adequado deve ser destacada antes do GATE de abertura.

## 5. Materialidade e limites

Margem nacional **confirmada em fonte oficial**: \(M=64.256.232-59.826.041=4.430.191\) votos. Válidos nacionais \(124.082.273\). Para cada coorte, \(V_c=\sum_s(v_{13,s}+v_{22,s})\) = **todos os votos válidos de todas as seções de encerramento tardio classificadas**. Definir:

- **Transferência bilateral hipotética:** fração mínima \(q_{transfer}=(M+1)/(2V_c)\); número inteiro necessário \(N_{transfer}=\lfloor M/2\rfloor+1=2.215.096\). Restringir a votos originalmente atribuídos ao candidato cuja margem seria reduzida; portanto, além de \(V_c\), verificar a disponibilidade do candidato nessa coorte. Somente parte dos votos totais da coorte pode ser transferida nesse sentido.
- **Alteração unilateral hipotética:** \(N_{unilateral}=M+1=4.430.192\), se cada alteração tiver impacto líquido máximo de 1 na margem.
- **Cenário restrito à coorte:** se \(V_c < N_{transfer}\), uma reversão por transferência de voto **exclusivamente nessa coorte** é aritmeticamente impossível; esta é condição necessária, não suficiente. Não usar médias aproximadas quando os microdados forem liberados.
- Relatar ambos os limites e a porcentagem do eleitorado total; anomalia estatística e materialidade eleitoral são perguntas distintas.

Não atribuir efeitos aos grupos sem teste observacional capaz de identificá-los. A aritmética não fornece mecanismo para adulterar sistemas.

## 6. Placebos e pré-validação liberados

**2T municipal 2024:** preferencialmente disputas para prefeito em que haja exatamente dois candidatos, e coortes com relógio externo verificável. Desfecho = participação do vencedor **municipal** nos válidos da própria eleição; o desfecho não é diretamente comparável a Lula/Flávio. Todos os votos da seção entram. Se a confirmação externa não existir, o teste temporal é **não estimável** e apenas a validação do parser/qualidade é permitida. Reconhecer municípios selecionados e saliência distinta.

**1T2026:** somente recursos comprovadamente restritos ao primeiro turno e isolados fisicamente do 2T. Se arquivos combinarem turnos ou tiverem metadados ambíguos, **não abrir**. Desfecho técnico para testes de consistência do parser = participação de 13 entre votos 13 e 22; outros candidatos são contabilizados separadamente e nunca classificados como branco/nulo. Se o relógio externo não existir, validar parsing e reconciliação, sem teste de efeito.

Para ambos: filtros explícitos ano, turno, cargo, UF; manifesto do recurso com nome, URL, turno, campo de seção, SHA-256, licença e data. Testar em arquivo sintético e em controles negativos primeiro. Nenhum 2T2026 pode ser solicitado ou baixado pelo pipeline antes do desbloqueio D4.

O módulo comum de logs para os itens **1.4 (catálogo) e 1.5 (dt*)** do Estudo 03 só passa à condição de *validado* depois de confirmar granularidade, timestamp, modalidade de habilitação e amostra de registros efetivos do 1T2026; não inventar campos ou conversores de \`.logjez\`.

## 7. Regra de congelamento, critérios de interrupção e reporte

Antes de iniciar microdados 2T2026: (1) registro de versão e SHA-256 deste documento; (2) revisão de exposição prévia, inclusive a amostra de 2,1%; (3) teste da qualidade de relógio externo; (4) diagnóstico de poder em placebos; (5) aprovação **expressa** do proponente do Estudo 05; (6) aprovação do GATE 1.6 do Estudo 03. Em falta de qualquer item, **parar**.

Critérios de não testabilidade: fonte externa ausente, local de votação indisponível, ausência de sobreposição no local, erro grave de reconciliação ou menos de 30 locais elegíveis. Relatar nulos, positivos, não estimáveis e efeitos sem materialidade com mesmo destaque. Nenhuma atribuição individual de conduta. Ajuste posterior deste protocolo somente em **emenda datada e vinculada**, nunca modificando este arquivo após commit.

## 8. Fontes e rastreio

- TSE, 25/10/2026: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/presidente-do-tse-anuncia-reeleicao-de-lula-e-faz-balanco-do-2o-turno-das-eleicoes-2026
- TSE, 28/10/2026: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/como-a-totalizacao-dos-votos-evoluiu-ferramenta-do-tse-permite-acompanhar-o-processo
- TSE, dados oficiais: https://dadosabertos.tse.jus.br/dataset/resultados-2024 e https://dadosabertos.tse.jus.br/dataset/resultados-2026
- Histórico de bloqueios, exposição e decisões: PLANEJAMENTO.md; estudos/05_simulacao_temporal/REVISAO_METODOLOGICA_20261029.md.
