# Protocolo de pré-registro — Etapa 0

**Versão:** 1.0 — rascunho para aprovação humana explícita  
**Data de redação:** 28/10/2026  
**Unidade de análise planejada:** seção eleitoral e, quando aplicável, evento individual de habilitação.  
**Status:** pré-registro ainda não aprovado; nenhum dado de análise foi aberto nesta Etapa 0.

## 1. Pergunta de pesquisa

Em todas as Unidades da Federação (UFs), durante as janelas finais de votação de 25/10/2026, há evidência estatística de uma “assinatura de pianista”, operacionalizada por uma combinação pré-especificada de (i) aumento na taxa de habilitação sem biometria e (ii) rajadas temporais de habilitações incompatíveis com o padrão temporal de referência, em magnitude que exceda o limiar de efeito mínimo fixado e permaneça após controles e correção por falsos descobrimentos?

A análise não pretende provar fraude, autoria, intenção ou causalidade. Um resultado positivo será tratado como sinal estatístico compatível com a hipótese operacional, sujeito a explicações alternativas, validação documental e investigação institucional.

## 2. Escopo e parâmetros fixados

- **ESCOPO_UF:** todas as UFs.
- **AMOSTRA:** censo das unidades elegíveis disponíveis; não haverá amostragem probabilística.
- **COMPARADORES:** 1T 2026; 2T 2022; e 2T 2018 somente se os logs necessários estiverem disponíveis e forem comparáveis.
- **ALFA:** 0,05, com controle de FDR Benjamini–Hochberg em **q = 0,05**.
- **EFEITO_MINIMO:** 5 pontos percentuais na taxa de habilitação sem biometria e **2 rajadas por seção**.
- **JANELA_FINAL:** 16h00–17h00 e 17h00–19h00, analisadas separadamente.
- **SEED:** 20261025.
- **Unidade temporal:** horário de Brasília, salvo documentação oficial de conversão necessária para a base analisada.

A extensão excepcional do recebimento de votos até 19h00 de Brasília em locais cujas urnas ainda não haviam sido fechadas foi documentada pelo STF e pelo TSE; urnas já fechadas deveriam seguir os procedimentos de computação e totalização (STF, 2026a; STF, 2026b; TSE, 2026a). O TSE registrou 34.393 votos após 17h no território nacional, mas advertiu-se que registros após 17h não identificam, isoladamente, se o eleitor foi beneficiado pela prorrogação ou já estava na fila às 17h (TSE, 2026b; TRE-DF, 2026). Esses fatos motivam a separação das duas janelas, mas não constituem evidência da hipótese.

## 3. Definições operacionais

### 3.1 Habilitação sem biometria

Será classificada como **habilitação sem biometria** a habilitação cujo registro de dados identifique o fluxo previsto para pessoa sem biometria coletada ou o fluxo de biometria não reconhecida, conforme a codificação efetivamente disponível nos logs e no dicionário de dados. A Resolução TSE nº 23.759/2026 distingue a pessoa sem biometria coletada, habilitada mediante digitação do ano de nascimento, da biometria não reconhecida após tentativas de leitura; no segundo fluxo, prevê conferência do ano de nascimento, assinatura e leitura da digital da mesária ou do mesário (TSE, 2026c). O Manual do Mesário descreve até quatro tentativas de leitura e os fluxos de assinatura/ano de nascimento (Justiça Eleitoral, 2026a).

Se os dados não distinguirem essas duas situações, será usada apenas a categoria agregada documentada pelo campo; a limitação será reportada e não será feita reclassificação por suposição. Não se atribuirá automaticamente a leitura da digital do mesário a todo eleitor sem biometria cadastrada, pois essa exigência não está expressa da mesma forma no art. 20 e no art. 21 da resolução.

Para seção `s` e janela `w`, definimos:

\[
r_{s,w}^{NB}=\frac{N_{s,w}^{NB}}{N_{s,w}^{H}},
\]

onde `N^{NB}` é o número de habilitações sem biometria observadas e `N^{H}` é o número total de habilitações observadas. Se o denominador ou a classificação não estiver disponível, a taxa será marcada como não estimável, não imputada.

### 3.2 Tempo entre habilitações e limiar `dt`

Para cada seção, os eventos serão ordenados pelo timestamp disponível. O intervalo entre habilitações consecutivas será `dt_i = t_i − t_{i−1}`. O limiar `dt*` será o **percentil 1 empírico dos `dt` entre habilitações biométricas ocorridas entre 09h00 e 15h00 do 1T 2026**, calculado antes de abrir ou inspecionar os dados do 2T 2026. O método de quantil, tratamento de empates, timestamps inválidos e fuso serão registrados no log de análise antes da abertura do 2T 2026.

O limiar será estimado somente com eventos biométricos válidos, não com a janela final nem com os resultados-alvo. Se não houver logs comparáveis, timestamp suficiente ou número mínimo documentado de eventos para estimar o percentil, o limiar ficará pendente e a análise confirmatória correspondente não será executada.

### 3.3 Rajada

Uma **rajada** é uma sequência contígua de pelo menos dois intervalos consecutivos `dt_i ≤ dt*` dentro da mesma seção e janela, sem inserir eventos ausentes ou reordenar timestamps. A contagem de rajadas usará uma regra determinística de não sobreposição: uma nova rajada começa após o fim da anterior e somente após um intervalo `dt_i > dt*`, salvo especificação técnica previamente registrada para empates. A regra final de empates e a implementação deverão ser congeladas antes do acesso ao 2T 2026.

A condição de efeito mínimo para a dimensão temporal é **pelo menos 2 rajadas por seção** na janela analisada. A quantidade de rajadas é uma medida descritiva e também um critério de sinalização; sua significância será testada conforme as hipóteses abaixo.

### 3.4 Assinatura de pianista

A assinatura de pianista é uma hipótese operacional, não um fato estabelecido: concentração temporal de habilitações em rajadas muito rápidas, especialmente quando acompanhada por elevação da taxa de habilitação sem biometria, em uma janela final, relativamente ao padrão biométrico de referência e aos comparadores disponíveis. A classificação de uma seção como sinalizada exigirá que os critérios previamente definidos sejam aplicados sem olhar para resultados, candidatos ou UFs favorecidas.

## 4. Hipóteses

As hipóteses serão avaliadas em cada janela final separadamente, por UF e no agregado nacional quando a unidade e a comparabilidade permitirem. A direção alternativa é pré-especificada.

### H0a/H1a — taxa de habilitação sem biometria

- **H0a:** a diferença na taxa de habilitação sem biometria entre a janela final do 2T 2026 e o comparador temporal apropriado é nula ou não excede o efeito mínimo de 5 pontos percentuais, após os controles especificados.
- **H1a:** a taxa no 2T 2026 excede a do comparador em pelo menos 5 pontos percentuais, de forma estatisticamente compatível com `p ≤ 0,05` e `q ≤ 0,05` após FDR.

### H0b/H1b — rajadas temporais

- **H0b:** a quantidade de rajadas definida por `dt*` não apresenta excesso sistemático no 2T 2026 em relação ao padrão de referência/comparador, ou não atinge pelo menos 2 rajadas por seção.
- **H1b:** há excesso de rajadas compatível com a hipótese temporal, com pelo menos 2 rajadas por seção na unidade sinalizada, segundo o teste e a regra de exposição previamente congelados.

### H0c/H1c — assinatura conjunta

- **H0c:** não há associação conjunta entre elevação de pelo menos 5 pontos percentuais na taxa sem biometria e ocorrência de pelo menos 2 rajadas por seção; qualquer associação observada é compatível com variação aleatória, composição, horário, fluxo, contingência ou outras explicações controladas.
- **H1c:** a mesma unidade, na mesma janela pré-especificada, satisfaz conjuntamente o limiar de taxa sem biometria e o limiar de rajadas, com evidência estatística após FDR e persistência nas análises de robustez.

Nenhuma hipótese será interpretada como evidência de fraude sem biometria ou de manipulação. A lei de Benford não será usada como teste confirmatório: literatura verificada alerta que conformidade ou desvio não oferece desempenho forense confiável quando usada isoladamente (Deckert; Myagkov; Ordeshook, 2011).

## 5. Variáveis e fontes de dados

### 5.1 Variáveis primárias

- identificador pseudonimizado de UF, município, zona e seção;
- turno, data, janela e timestamp de cada habilitação;
- modalidade de habilitação (biométrica, sem biometria, não reconhecida ou código equivalente documentado);
- indicador de validade, duplicidade, ordenação e completude do timestamp;
- total de habilitações por seção e janela;
- número e taxa de habilitações sem biometria;
- `dt` entre habilitações e número de rajadas;
- candidato/cargo, somente quando necessário para a análise de simetria e se o arquivo o disponibilizar de modo legítimo.

### 5.2 Covariáveis e controles potenciais

Serão considerados, se disponíveis e documentados: UF, fuso/horário local, turno, seção, tamanho do eleitorado, total de habilitações, comparecimento, status de fechamento, urna de contingência/substituição, qualidade/completude do log, situação de totalização, fila/atendimento e composição observável do eleitorado. O conjunto Eleitorado–2026 fornece perfis e eleitorado por seção; Comparecimento e Abstenção–2026 fornece indicadores agregados, mas não equivale, por si só, a registro técnico de ocorrências (TSE, 2026d; TSE, 2026e).

### 5.3 Disponibilidade ainda não confirmada

Nesta etapa não foram baixados nem validados campo a campo os ZIP/CSV ou logs. O TSE publica conjuntos de Resultados, BU, arquivos transmitidos contendo BU/log/RDV/VOTA em situação “Totalizado” e logs Gedai, mas a disponibilidade integral, comparabilidade, cobertura de todos os eventos de habilitação e campos necessários para 2T 2026, 1T 2026, 2T 2022 e 2T 2018 ainda precisam ser verificadas (TSE, 2026f; TSE, 2026g; TSE, 2026h; TSE, 2026i). Portanto, nenhuma estimativa ou resultado é apresentado neste protocolo.

## 6. Regras de exclusão e sinalização

Serão excluídos da estimativa primária, com contagem e motivo registrados: eventos sem identificador de seção; timestamps ausentes, impossíveis, duplicados ou fora do turno; registros cuja ordem temporal não possa ser determinada; eventos sem classificação de habilitação; registros não totalizados quando a análise exigir totalização; e unidades sem denominador válido.

Serão sinalizados, não automaticamente excluídos: seções com baixa completude; mudanças de fuso; fechamento antes/depois do horário; presença de contingência ou substituição; múltiplos reinícios/logs; discrepância entre logs e BU; e seções com volume extremo. A análise principal não imputará eventos nem converterá ausência de registro em zero.

A substituição de urna não será inferida de um número agregado ou de fonte secundária quando não houver registro de seção. O total final de 1.551 urnas substituídas em 499.248 foi informado pelo TSE, mas a decomposição por modalidade não foi confirmada diretamente em fonte primária; portanto, não será usada como variável individual sem validação (TSE, 2026j).

## 7. Plano de análise estatística

1. Congelar versão do protocolo, dicionário de dados, regras de limpeza, regra de rajada, quantil e código de análise antes da abertura do 2T 2026.
2. Validar hashes, cobertura por UF/turno, duplicidades, timestamps, fuso, status de totalização e correspondência entre identificadores.
3. Estimar `dt*` exclusivamente no conjunto biométrico de 09h–15h do 1T 2026, antes de abrir o 2T 2026.
4. Construir as janelas 16h–17h e 17h–19h separadamente. A janela 17h–19h será interpretada à luz da ordem excepcional: somente locais ainda abertos poderiam prosseguir; registros após 17h não serão automaticamente atribuídos à prorrogação (STF, 2026b; TSE, 2026a; TRE-DF, 2026).
5. Calcular, por seção e UF, taxa sem biometria, diferenças em pontos percentuais, número de rajadas e indicador conjunto.
6. Comparar 2T 2026 com 1T 2026; repetir com 2T 2022 e 2T 2018 somente quando os logs forem acessíveis e comparáveis. Não haverá comparação forçada entre esquemas incompatíveis.
7. Usar modelos apropriados ao desfecho e à unidade, com efeitos/fatores de UF e seção quando identificáveis, exposição/denominador explícito e erros-padrão robustos ou método de reamostragem documentado. A especificação exata será congelada após inspeção apenas da estrutura/metadados, sem consultar desfechos do 2T 2026.
8. Testar H0a, H0b e H0c nas famílias previamente definidas; aplicar Benjamini–Hochberg com `q=0,05` e reportar estimativa, intervalo de confiança, p-valor, q-valor, número de unidades e exclusões.
9. Relatar resultados por UF e agregado, sem selecionar apenas UFs ou candidatos com sinais positivos.

A análise confirmatória principal é a que usa as duas janelas fixadas, o `dt*` calibrado como acima, os comparadores disponíveis e as regras de exclusão congeladas. Qualquer redefinição posterior será rotulada como análise exploratória e não substituirá a principal.

## 8. Simetria entre candidatos

A mesma definição de exposição, unidade, janela, denominador, `dt*`, teste, controle FDR, exclusão e critério de sinalização será aplicada a todos os candidatos elegíveis do mesmo cargo. Não haverá escolha de candidato baseada no resultado. Serão reportados todos os candidatos com dados válidos ou, se a anonimização impedir a publicação nominal, códigos consistentes e a regra de mapeamento preservada sob acesso autorizado. Diferenças de exposição, votos válidos, volume ou disponibilidade serão ajustadas/descritas, não tratadas como equivalência automática.

## 9. Controles de confundimento e explicações alternativas

Serão avaliados: variação normal de fluxo ao longo do dia; filas e eleitores presentes às 17h; fusos e horários locais; composição e tamanho da seção; disponibilidade/ausência de biometria; falha de reconhecimento; contingência/substituição; reinício ou perda de log; fechamento efetivo; qualidade e situação de totalização; diferenças de tecnologia e documentação entre eleições; e alteração normativa/operacional. A resolução vigente prevê tentativas de reconhecimento e fluxos distintos para ausência e não reconhecimento de biometria (TSE, 2026c; TSE, 2026k).

Nenhum controle será usado para “explicar” o sinal por conveniência após ver o resultado. Variáveis não disponíveis serão declaradas como limitações. A ordem excepcional das 17h não será convertida em tratamento uniforme de todas as seções, pois a aplicação ficou restrita às urnas ainda abertas (STF, 2026b).

## 10. Robustez

Serão planejadas, se os dados permitirem: (a) repetição por UF, região e tamanho de seção; (b) modelos com e sem controles; (c) exclusão de seções com baixa completude e análise de sensibilidade incluindo-as como sinalizadas; (d) limiares temporais alternativos apenas como exploratórios; (e) comparação com diferentes regras de não sobreposição de rajadas; (f) placebo em 09h–15h; (g) comparação entre candidatos e cargos sob a mesma regra; (h) análise restrita a registros com status e hash verificáveis; e (i) comparação com 2T 2022/2018 apenas se a comparabilidade for demonstrada.

Não será usado Benford como confirmação. A literatura sobre irregularidades eleitorais reconhece utilidade de métodos estatísticos específicos, mas também limita inferências e alerta contra testes isolados; resultados agregados não identificam mecanismo ou intenção (Klimek et al., 2012; Rozenas, 2017; Deckert; Myagkov; Ordeshook, 2011).

## 11. Poder e precisão

Como a amostra é um censo, não haverá cálculo de tamanho amostral para seleção. Isso não garante poder: o poder efetivo dependerá do número de seções com logs válidos, prevalência do desfecho, correlação intrasseção, completude e magnitude real. Antes da análise confirmatória, será produzido um diagnóstico de precisão/poder baseado exclusivamente em metadados e parâmetros observáveis, com simulações usando **SEED = 20261025**, sem ajustar hipóteses aos resultados do 2T 2026. Se o diagnóstico mostrar precisão insuficiente, o resultado será “inconclusivo” ou exploratório, não convertido em evidência positiva.

## 12. Privacidade, LGPD e segurança

Serão utilizados apenas dados necessários à finalidade científica/analítica, preferencialmente agregados por seção e janelas. Não serão publicados nome, título, CPF, biometria, imagem, assinatura, identificador individual ou qualquer dado diretamente identificável. Identificadores serão pseudonimizados; chaves, se existirem, ficarão separadas, com acesso restrito, registro de acesso, criptografia em repouso/trânsito e retenção mínima necessária. A divulgação respeitará a LGPD e as regras de acesso/licença do TSE. O conjunto de logs do 2T 2026 foi descrito no portal como “Nenhuma Licença Fornecida”, o que requer verificação antes de redistribuição ou uso derivado (TSE, 2026h).

A pesquisa não tentará reidentificar eleitores nem inferir atributos sensíveis. Qualquer incidente será documentado e interromperá o processamento até avaliação responsável.

## 13. Critérios de parada

A coleta/análise confirmatória será interrompida se: (i) faltar base essencial ou dicionário que permita identificar a unidade e o tempo; (ii) os logs não forem comparáveis; (iii) houver risco de reidentificação; (iv) hashes/arquivos estiverem corrompidos ou inconsistentes sem resolução; (v) a aprovação humana for revogada; ou (vi) a execução exigir alteração de parâmetro fixado. Não haverá parada antecipada por encontrar sinal positivo. Resultados parciais não serão divulgados como conclusão.

## 14. Confirmatório versus exploratório

**Confirmatório:** hipóteses H0a/H1a, H0b/H1b e H0c/H1c; todas as UFs; censo elegível; duas janelas fixadas; comparadores autorizados; `dt*` definido pelo percentil 1 biométrico de 09h–15h do 1T 2026 antes de abrir o 2T 2026; efeito mínimo fixado; alfa/FDR fixados; simetria entre candidatos; regras de exclusão congeladas.

**Exploratório:** limiares alternativos; outras janelas; outros agrupamentos; visualizações; associações não previstas; decomposição de causas; uso de bases não comparáveis; e qualquer análise criada após inspeção dos resultados. Esses resultados serão claramente rotulados, sem p-valor confirmatório ou linguagem causal.

## 15. Decisões pendentes antes da execução

Ainda precisam de decisão humana explícita: aprovação deste protocolo; confirmação do cargo/candidatos e do nível de divulgação; confirmação do dicionário/códigos de habilitação; disponibilidade e licença dos logs; regra final para empates e eventos simultâneos; especificação estatística final após inspeção de metadados; e autorização de acesso aos dados. Nenhum desses pontos será preenchido por suposição.

## Referências (ABNT simplificado)

BRASIL. Supremo Tribunal Federal. **Liminar urgente na Rcl 101.673**. 25 out. 2026. Disponível em: <https://noticias-stf-wp-prd.s3.sa-east-1.amazonaws.com/wp-content/uploads/wpallimport/uploads/2026/10/25183103/liminar-urgente.pdf>. Acesso em: 28 out. 2026.

BRASIL. Supremo Tribunal Federal. **Esclarecimento da decisão na Rcl 101.673**. 25 out. 2026. Disponível em: <https://noticias-stf-wp-prd.s3.sa-east-1.amazonaws.com/wp-content/uploads/wpallimport/uploads/2026/10/25183217/esclarecimento.pdf>. Acesso em: 28 out. 2026.

DECKERT, Joseph; MYAGKOV, Mikhail; ORDESHOOK, Peter C. Benford’s Law and the detection of election fraud. *Political Analysis*, v. 19, n. 3, p. 245–268, 2011. DOI: 10.1093/pan/mpr014. Disponível em: <https://www.cambridge.org/core/journals/political-analysis/article/benfords-law-and-the-detection-of-election-fraud/3B1D64E822371C461AF3C61CE91AAF6D>.

JUSTIÇA ELEITORAL. **Manual do Mesário**. 2026. Disponível em: <https://www.justicaeleitoral.jus.br/eleicoes/mesario/assets/arquivos/manual_do_mesario.pdf>.

KLIMEK, Peter et al. Statistical detection of systematic election irregularities. *Proceedings of the National Academy of Sciences*, v. 109, n. 41, p. 16469–16473, 2012. DOI: 10.1073/pnas.1210722109. Disponível em: <https://www.pnas.org/doi/10.1073/pnas.1210722109>.

ROZENAS, Arturas. Detecting election fraud from irregularities in vote-share distributions. *Political Analysis*, v. 25, n. 1, p. 41–56, 2017. DOI: 10.1017/pan.2016.9. Disponível em: <https://www.cambridge.org/core/journals/political-analysis/article/detecting-election-fraud-from-irregularities-in-voteshare-distributions/1C48196DDCECC891F913CE0CEE948F3E>.

TRIBUNAL REGIONAL ELEITORAL DO DISTRITO FEDERAL. **TRE-DF informa quantidade de votos computados após as 17 horas no segundo turno**. 2026. Disponível em: <https://www.tre-df.jus.br/comunicacao/noticias/2026/Outubro/tredf-informa-quantidade-de-votos-computados-apos-as-17-horas-no-segundo-turno>.

TRIBUNAL SUPERIOR ELEITORAL. **Resolução nº 23.759, de 26 de fevereiro de 2026**. Disponível em: <https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-759-de-26-de-fevereiro-de-2026>.

TRIBUNAL SUPERIOR ELEITORAL. **Esclarecimento sobre prorrogação da votação**. 2026. Disponível em: <https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/esclarecimento-sobre-prorrogacao-da-votacao>.

TRIBUNAL SUPERIOR ELEITORAL. **Eleições 2026: mais de 34 mil votos foram registrados após as 17h no 2º turno**. 2026. Disponível em: <https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno>.

TRIBUNAL SUPERIOR ELEITORAL. **Portal de Dados Abertos: Resultados–2026**. 2026. Disponível em: <https://dadosabertos.tse.jus.br/dataset/resultados-2026>.

TRIBUNAL SUPERIOR ELEITORAL. **Portal de Dados Abertos: Resultados 2026 — Boletim de Urna**. 2026. Disponível em: <https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna>.

TRIBUNAL SUPERIOR ELEITORAL. **Portal de Dados Abertos: arquivos transmitidos para totalização**. 2026. Disponível em: <https://dadosabertos.tse.jus.br/dataset/resultados-2026-arquivos-transmitidos-para-totalizacao>.

TRIBUNAL SUPERIOR ELEITORAL. **Portal de Dados Abertos: logs Gedai do 1º e 2º turnos**. 2026. Disponível em: <https://dadosabertos.tse.jus.br/dataset/resultados-2026-logs-do-sistema-de-preparacao-das-urnas-eletronicas-gedai-1-turno> e <https://dadosabertos.tse.jus.br/dataset/resultados-2026-logs-do-sistema-de-preparacao-das-urnas-eletronicas-gedai-2-turno>.

TRIBUNAL SUPERIOR ELEITORAL. **Portal de Dados Abertos: Eleitorado–2026**. 2026. Disponível em: <https://dadosabertos.tse.jus.br/dataset/eleitorado-2026>.

TRIBUNAL SUPERIOR ELEITORAL. **Portal de Dados Abertos: Comparecimento e Abstenção–2026**. 2026. Disponível em: <https://dadosabertos.tse.jus.br/dataset/comparecimento-e-abstencao-2026>.

TRIBUNAL SUPERIOR ELEITORAL. **Balanço do 2º turno das eleições 2026**. 2026. Disponível em: <https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/presidente-do-tse-anuncia-reeleicao-de-lula-e-faz-balanco-do-2o-turno-das-eleicoes-2026>.

