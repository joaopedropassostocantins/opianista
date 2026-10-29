# Protocolo de auditoria temporal eleitoral — Hipótese de inserção indevida de votos pela mesa receptora
**Versão:** 1.0 — 28/10/2026  
**Status:** protocolo definido; fontes oficiais identificadas; software de extração e contraste implementado e testado com dados SINTÉTICOS. **Não há estimativas reais da diferença 2024×2026 nesta entrega.**

## 1. Pergunta e hipóteses
**Pergunta:** a cadência de votos registrados em seções do 2º turno presidencial de 2026 — com atenção especial ao período 16h–17h — é compatível com a distribuição temporal observada em segundos turnos **municipais e estaduais**, após harmonização de horas, cargos, locais e comparecimento?

- **H0 (teste principal):** a média municipal das diferenças pareadas da proporção de votos computados na última hora, **2026 presidente – 2024 prefeito**, é igual a zero.
- **H1 (bilateral):** a média municipal das diferenças pareadas é diferente de zero.
- **Predição direcional investigativa:** proporção maior entre 16h e 17h em 2026; eventual excesso nos últimos 30/15/5 minutos. A direção não substitui o teste bilateral pré-fixado.
- **Hipótese operacional específica:** o excesso, se existir, estaria concentrado em poucas seções, com cadência anômala e possivelmente formas excepcionais de habilitação. Essa assinatura **não equivale a atribuição de conduta ilícita**.

A ausência de rejeição de H0 não comprova equivalência. Para afirmar similaridade substantiva, executar análise de equivalência (TOST) com margem **±0,5 ponto percentual** — margem analítica inicial, a revisar em justificativa registrada **antes de examinar os dados reais**. A rejeição de H0 não identifica automaticamente mecanismo causal ou fraude.

## 2. Amostras — exclusões expressas
### Controle primário (independente da disputa presidencial)
- **2024, 2º turno municipal para prefeito** (27/10/2024): 51 municípios, um cargo, com 33.996.477 eleitores aptos anunciados pelo TSE. Selecionar apenas as seções desses municípios e exigir correspondência confiável UF + município TSE + zona + seção e conferência de local/agrupamento.
- **2020, 2º turno municipal para prefeito:** somente análise de sensibilidade. Alterações de comportamento pela pandemia e eventuais protocolos sanitários inviabilizam empilhamento ingênuo com 2024.
- **2016, 2º turno municipal para prefeito:** elegível somente se houver logs com horário individual, formato verificado e cobertura auditável.

### Controles estaduais secundários
- **2022, 2018 e 2014, 2º turno estadual para governador:** os registros podem informar cadência em eleições gerais. **Restrição crucial:** a mesma pessoa também votava para presidente, quando disputado o 2º turno nacional. Logo, a série estadual não é uma fonte independente da movimentação eleitoral presidencial. Os dados estaduais não entram no controle primário e não devem ser usados para alegar validação independente do comportamento presidencial.

### Alvo
- **2026, 2º turno presidencial (25/10/2026)**, dentro das seções elegíveis a comparação.
- **Controle primário com um único cargo em 2026:** excluir AC, AM, ES, RN, TO e DF, que tiveram 2º turno de governador em 2026. Esses lugares são analisados separadamente, pois o eleitor precisava votar em dois cargos.
- **Amostra principal restrita a municípios que também tiveram 2º turno para prefeito em 2024:** resultado dessa amostra **NÃO é automaticamente generalizável** ao Brasil, já que todos os municípios de 2024 eram grandes centros com eleição de prefeito em segundo turno. É necessária calibração de cobertura para extrapolação nacional, e pode não haver suporte para municípios rurais.

**Proibição:** nenhuma eleição presidencial anterior a 2026 é usada como amostra de referência, parâmetro do modelo, janela de calibração ou teste placebo principal.

## 3. Fontes originais e registros necessários
1. TSE — **Resultados 2024 – Arquivos transmitidos para totalização** (ZIPs por UF e turno): https://dadosabertos.tse.jus.br/dataset/resultados-2024-arquivos-transmitidos-para-totalizacao
2. TSE — **Resultados 2022 – Arquivos transmitidos para totalização**: https://dadosabertos.tse.jus.br/dataset/resultados-2022-arquivos-transmitidos-para-totalizacao
3. TSE — 2026, arquivos de urna, BU, RDV e logs: https://dadosabertos.tse.jus.br/dataset/ e https://resultados.tse.jus.br/
4. TSE — calendário e instrução sobre horários e habilitação: https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-759-de-26-de-fevereiro-de-2026?texto=compilado
5. TSE — eleitores 2024: https://www.tse.jus.br/comunicacao/noticias/2024/Outubro/faltam-10-dias-2o-turno-do-pleito-abrange-33-9-milhoes-de-eleitores-de-51-municipios
6. Revisão de literatura sobre operações de locais de votação e natureza não estacionária do fluxo: https://electionlab.mit.edu/sites/default/files/2023-10/in-person-voting_MEAES.pdf
7. Literatura de filas e distinção entre chegada, identificação e conclusão do voto: https://vote.caltech.edu/documents/152/Managing_Polling_Place_Resources.pdf

**Não utilizar GEDAI como log dos votos.** Extrair eventos **“O voto do eleitor foi computado”** exclusivamente do log da urna, filtrado pela data do segundo turno. Guardar checksums de pacotes oficiais e nota de extração. Eventos do 1º turno podem estar nos logs cumulativos do 2º; filtre por data. Incluir logs de contingência quando houver urnas substituídas; não inferir comparecimento de log incompleto.

## 4. Harmonização
- Os logs podem registrar hora local da urna; eleições históricas tiveram mudanças nas regras de fuso. Converter pelo município e ano para **minuto desde a abertura legal**; não comparar 16h do relógio local com 16h Brasília indevidamente.
- Comparar os primeiros 540 minutos (9 horas, 8h–17h Brasília nas eleições unificadas). Votos depois das 17h são analisados separadamente e não contaminam a métrica primária.
- Reconciliar cada urna: eventos totais de voto (incluindo após 17h) × comparecimento do BU; registrar falhas de reconciliação, seções agregadas, transferidas e urna substituída.
- Registrar denominador: número de votos efetivamente computados no intervalo 8h–17h. Não dividir por votos válidos para um candidato.
- Não tratar habilitação sem cadastro biométrico como sinônimo de liberação manual após falha da digital. Procedimentos legais mudaram em 2026.
- Excluir da inferência principal seções sem correspondente confiável em 2024, com 50 ou menos votos no período, logs de contingência não reconstruídos ou metadados incompletos. Mostrar cobertura e perfil das exclusões.

## 5. Estatística principal, estimadores e decisão
Para seção i em ano y:

`p_i,y = votos_i,y(16h–17h) / votos_i,y(8h–17h)`

Diferença na mesma seção:

`d_i = p_i,2026 - p_i,2024`.

Agregação primária: calcular a média de `d_i` por município e depois a média municipal, preservando o município como unidade de inferência. Apresentar IC95% por t de Student sobre médias municipais e por **bootstrap de municípios** (não por eleitor). Reportar n municípios, n seções pareadas, distância em pontos percentuais, p, IC95%, faixa de equivalência ±0,5 p.p., amplitude e heterogeneidade regional. Para a generalização a municípios com diferentes dimensões, realizar análise ponderada adicional, **não substituir** o desfecho pré-especificado por pesos escolhidos a posteriori.

- **α = 0,05 bilateral** para o contraste primário.
- **Materialidade:** o limiar investigativo inicial é 0,5 p.p., além da significância; deverá ser justificado antes da leitura dos valores reais.
- **Multicomparações:** BH-FDR 1% nas triagens por seção; testes auxiliares de janelas por Holm ou FDR separado.
- **Especificação alternativa:** binomial hierárquica/beta-binomial, intercepto por município e dispersão entre seções; análises de robustez por UF, porte, participação e local de votação.
- **Validação de tendência:** séries municipais adicionais 2020/2016 apenas com dados adequados; sem elas, diferenças 2024→2026 podem representar mudança legítima de mobilização.

## 6. Testes auxiliares e assinaturas investigativas
A. **Forma da curva:** 36 intervalos de 15 minutos, diferença por janela, distribuição de desvios ajustada por local e município.

B. **Agrupamento final:** 16h–16h15, 16h15–16h30, 16h30–16h45, 16h45–17h; identificar picos na última meia hora sem assumir que um aumento corresponde a voto fictício.

C. **Cadência intrasseção:** distribuição empírica dos intervalos entre votos computados (segundos), runs de votos rápidos e tempos entre início de identificação e computação. Calibrar o valor esperado a partir do **mesmo tipo de eleição** e do modelo da urna, não de um tempo mínimo inventado. Descartar casos em que o relógio, eventos duplicados ou a contingência invalidam o cálculo.

D. **Habilitação:** taxas de biometria reconhecida, habilitação por falha de reconhecimento, e eleitores sem biometria cadastrada **separadas**. Cruzar com alta taxa de votos na última hora, sempre por estrato e método de votação; conferir ata e relatório de eleitores não reconhecidos biometricamente.

E. **Comparecimento/abstenção:** agregar BU e cadastro de aptos (abstenção = 1 - comparecimento/aptos); verificar concentração de elevada votação tardia, baixo percentual de abstenção, uso excepcional de identificação. Evitar usar abstenção como preditor que absorva parte da própria hipótese: apresentá-la também como diagnóstico externo.

F. **Presença física independente:** verificar autorização e disponibilidade de contagens de entrada, câmeras de acessos públicos, registros de fluxo do prédio e atas. Qualquer dado de telecomunicações exige base legal e salvaguardas de privacidade; agregações por antena NÃO identificam com precisão presença na cabina, e a ausência de sinal não demonstra ausência do eleitor. Não relacionar pessoas a escolhas eleitorais, preservando sigilo do voto.

G. **Comparação espacial:** seções do mesmo local (escola), mesmo município, similares em tamanho e histórico; exigir padrões replicáveis e registrar explicações concorrentes (falhas, transporte, clima, remanejamentos e mobilização específica).

## 7. Critérios interpretativos
1. **p≥0,05:** sem evidência suficiente para rejeitar H0 naquele desenho; não afirmar equivalência.
2. **p<0,05, efeito <0,5pp:** significância estatística possivelmente trivial; não atribuir anomalia material.
3. **p<0,05, efeito ≥0,5pp e persistência na validação:** diferença temporal relevante, recomendando examinar causas externas legítimas e reconstrução operacional.
4. **Excesso extremo localizado com alta taxa de habilitação excepcional e registros externos incompatíveis:** caso prioritário para **auditoria**, jamais imputação automática de fraude a pessoas ou seções.
5. **Nenhum sinal em agregados:** não exclui automaticamente a possibilidade de episódios raros, mas enfraquece a hipótese de fenômeno amplo.

## 8. Status e uso do programa
**Concluído:** identificação e verificação da disponibilidade oficial dos arquivos de 2024 e 2022; recorte de referência; modelo de comparação por seção/município; extração experimental em Python; teste interno com registros sintéticos para verificar estrutura do cálculo. **Não concluído:** download e decodificação de ZIPs oficiais completos, conferência com BUs reais, estimativa de efeito/IC/p de 2024×2026 e análise de biometria efetiva. Os ZIPs oficiais podem ter múltiplos GB e não foram transferidos a este ambiente.

Exemplo com São Paulo (horário local = Brasília nesses pleitos):

```bash
pip install numpy pandas scipy statsmodels py7zr
python auditoria_temporal.py extrair --zip bu_imgbu_logjez_rdv_vscmr_2024_2t_SP.zip --ano 2024 --tipo prefeito --data 2024-10-27 --abertura-local 08:00 --saida prefeito_2024_SP.csv
python auditoria_temporal.py extrair --zip bu_imgbu_logjez_rdv_vscmr_2026_2t_SP.zip --ano 2026 --tipo presidente --data 2026-10-25 --abertura-local 08:00 --saida presidente_2026_SP.csv
python auditoria_temporal.py testar --referencias prefeito_2024_SP.csv --alvo presidente_2026_SP.csv --saida resultados
```

Para 2020 municipal: `--ano 2020 --tipo prefeito --data 2020-11-29` e no teste `--ano-referencia 2020` (somente sensibilidade). Para governadores de 2022: `--ano 2022 --tipo governador --data 2022-10-30`, teste com `--tipo-referencia governador --ano-referencia 2022 --secundario` e **não misturar** a conclusão ao controle municipal. Os dois grupos de 2026 serão segregados automaticamente. Para fuso distinto, ajustar `--abertura-local` para o horário efetivamente registrado no município e confirmar pelas mensagens de abertura/zerésima.

**Controle de qualidade antes de publicação:** auditoria manual de 20 logs reais por origem e 20 seções com maior anomalia; verificação de cadeia de integridade, biometria, correspondência local e confronto BU; relatório de perdas e de seleção amostral.