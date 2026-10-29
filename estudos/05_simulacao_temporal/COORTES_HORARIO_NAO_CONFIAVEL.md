# Estudo 05 — coortes de urnas com encerramento tardio e hipótese de horário não confiável

**Revisão de escopo: 29/10/2026. Exploratório.** Não alterar o pré-registro dos Estudos 01 e 03. Este documento substitui a interpretação de que o foco deste módulo são apenas os votos lançados depois das 17h.

## Problema correto

**Unidade = urna/seção. Desfecho = todos os votos da urna/seção selecionada.**

A exposição é uma característica da **seção**: estar com votação ou procedimentos de encerramento ainda em curso além de determinado horário, não a hora em que um voto específico foi registrado. Exemplo: 280 votos em seção que encerrou às 19h08 = **280 votos** examinados, mesmo que nenhum novo voto seja comprovado depois das 17h.

O argumento de "mesário pianista" não implica que alguém teria de inserir fisicamente votos até as 19h. É essencial separar:
- **Hipótese operacional:** uso indevido da habilitação comum por operador; exige examinar pré-condições, controles, caderno/ata e vestígios. Não supor liberdade operacional irrestrita.
- **Hipótese de comprometimento de origem:** software anterior à apuração/BU hipoteticamente produz registros e contagens incorretas. Um registro coerente não refuta, por si só, o comprometimento na sua própria fonte.
- **Hipótese de cronologia não confiável:** carimbos gerados na mesma origem podem não ser fonte independente de quando ocorreu um evento. Alteração deliberada do relógio ou dos carimbos **não foi demonstrada** nas urnas reais e não deve ser presumida.
- **Hipótese de totalização:** o BU local original permanece íntegro, mas totalização central apresenta distribuição diferente. Confrontar BUs externos por seção.

## Dado oficial que obriga a corrigir o método

O TSE informou sobre o 2º turno de 25/10/2026:

| Critério de encerramento registrado | Número de seções |
|---|---:|
| Depois de 17h | **497.333** |
| Depois de 17h10 | **24.268** |
| Depois de 19h | **6.766** |

Fonte: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno

Esses números são **quantidades de seções**, não votos. O TSE esclarece que encerrar o funcionamento da seção abrange procedimentos após o último voto. Portanto, não são medidas diretas de funcionamento da sessão de votação até esses horários. A classe >17h inclui praticamente todas as seções do levantamento; é um **mau indicador isolado** do efeito da decisão de extensão. O corte 17h10 é apenas critério operacional de pesquisa e **não um padrão legal**; o grupo >19h ainda precisa ser depurado por estado e motivo do encerramento.

A decisão judicial de extensão só preservou em funcionamento as seções que **não haviam encerrado a votação às 17h**, conforme nota TSE 25/10/2026: https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/esclarecimento-sobre-prorrogacao-da-votacao. Não equiparar "encerrou relatórios após 19h" com "ficou recebendo votos até 19h".

## Variáveis e definição de coortes

Para cada seção identificada por município, zona, seção, turno e modelo, reunir:

1. **Todos os votos no BU:** A, B, branco, nulo, comparecimento, aptos, abstenção. Preservar identificação de seção agregada/contingência e número de cargos.
2. **Horário atribuído ao último voto e ao encerramento:** medir separadamente, com nível de confiança explícito.
3. **Horários da geração do BU, impressão, retirada de mídia, transmissão e recepção:** não substituir o horário de encerramento da votação pelo da totalização.
4. **Proveniência do horário:** próprio relógio da urna, log, ata assinada, registro externo verificável; anotar se as fontes dependem do mesmo relógio ou mesma pessoa.
5. **Contexto:** modalidade de fechamento, fila antes das 17h, contingências, modelo da urna, eleitorado, seção agregada, município, zona, escola, perfil local e eventuais ajustes autorizados.

**Coortes a serem examinadas:** >17h10, >18h e >19h; adicionalmente “ainda aberta às 17h no momento da determinação” apenas quando comprovado por fonte própria. Cada grupo é avaliado com todos os votos das seções selecionadas.

Definição provisória:

`S_t = {s : instante confirmado de encerramento(s) > t}`.

`V_t = Σ_{s ∈ S_t} comparecimento(s)`.

`P_{A,t} = [Σ_{s ∈ S_t} votos_A(s)] / [Σ_{s ∈ S_t}(votos_A(s)+votos_B(s))]`.

O denominador usa os votos **válidos para o cargo presidencial** no segundo turno; brancos e nulos permanecem nas métricas próprias, nunca são confundidos com votos válidos. Não imputar votos de seções cuja hora ou pertencimento ao grupo não foi confirmado, nem tratar ausência de confirmação como prova de fechamento antecipado.

## Hipóteses de relógio e integridade — sem pressupor capacidade de alterar horário

**H0:** diferenças entre seções com encerramento tardio e grupos comparáveis são explicadas por seleção de locais, atrasos administrativos, filas, contingências, tamanho do eleitorado, comportamento regional e variação estatística.

**H1:** a composição integral das seções com encerramento tardio apresenta diferença estável, não explicada pelas covariáveis observadas ou por efeitos de composição. **Uma associação NÃO prova adulteração nem identifica o mecanismo.**

**H2:** classificações baseadas exclusivamente no relógio/log da urna são sensíveis a erro, desalinhamento ou comprometimento hipotético de horário. A hipótese de alteração intencional exige evidência específica; o modelo não a assume.

**H3:** os registros de mesmo domínio permanecem coerentes apesar de um erro hipotético na origem. Uma prova externa independente pode revelar discrepâncias se existir, não sendo possível reconstituir a intenção secreta de cada eleitor a posteriori.

**H4:** divergências BU local preservado × BU publicado × resultado consolidado são auditáveis por seção com mapeamento correto.

## Regra legal de ajuste do relógio

O **art. 114 da Resolução TSE nº 23.751/2026** prevê que, após a preparação, eventual ajuste de horário/calendário interno da urna deve ser feito por **sistema específico do TSE**, por técnica(o) autorizada(o) pela juíza ou pelo juiz eleitoral, com notificação dos legitimados e **ata contendo identificação das urnas e horário**. Fonte: https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-751-de-26-de-fevereiro-de-2026

Isso prova a existência de um procedimento regulado, **não** uma capacidade irrestrita de mesários ou vulnerabilidade ativa durante a votação. Solicitar para pesquisa apenas documentação sobre eventuais ajustes e fontes de tempo, sem alteração de equipamento.

## Desenho inferencial

1. **Construir a base por seção, com 100% dos votos e não somente votos após 17h.** Identificar e deduplicar seções agregadas.
2. Confirmar grupos pelo **horário de encerramento da votação**; comparar com horário de fechamento técnico da urna e emissão do BU. A classificação por um log é **observada, não necessariamente verificada externamente**.
3. Selecionar grupos de comparação no mesmo município/zona/local e tamanho de eleitorado quando possível; não utilizar somente média nacional. Controlar comparecimento, composição geográfica, modelo, contingências e possíveis efeitos de seleção.
4. **Referência histórica da dinâmica de filas e encerramento:** segundos turnos **municipais**, sem usar eleições presidenciais anteriores como paradigma de cadência. Comparação com turnos presidenciais para checagem de compatibilidade de arquivos é auxiliar, não controle confirmatório.
5. Não usar causalidade ou “efeito de extensão” com alocação não aleatória sem estratégia explícita de identificação. Calcular intervalos de confiança e checagem de múltiplas hipóteses com unidade de cluster apropriada.
6. **Análise de sensibilidade ao relógio:** classificar pelo log, por confirmação externa quando disponível e por limites inferiores/superiores para seções sem referência; relatar proporção não verificável e divergência de classificação.
7. Investigar também o que a seção **não registrou** e comparar consistência entre suas saídas; tratar ausência de evento como evidência apenas se o contrato documental da versão real afirmar que o evento deveria ter sido gravado.
8. Comparar o BU local, quando custodiado externamente, ao BU publicado e ao resultado atribuído à seção; analisar a totalização separadamente do VOTA.
9. Manter resultados nulos, inconclusivos e positivos com exposição igual. Nenhuma inferência sobre o voto de indivíduos.

## Alteração do laboratório do site

O novo painel **“Coortes de encerramento tardio”** tem dez seções inventadas (F-01 a F-10), com votos integrais A/B/brancos/nulos, tempos de fechamento internos e, para algumas, uma referência de relógio externo *também fictícia*. Uma seção tem **discordância artificial entre dois horários**. O usuário pode alternar limiares >17h10 ou >19h e fontes de classificação, observando como o conjunto selecionado e o total de votos analisados mudam.

Isso não simula adulteração do relógio de uma urna real e não prova que a discordância tenha ocorrido no pleito. **Somente demonstra a fragilidade de classificar um grupo por uma variável cujo processo de medição é parte da hipótese que se deseja testar.**

## Evidências ainda necessárias

Dados oficiais do segundo turno de 2026 por seção; detalhamento de tipo/hora de encerramento; relógio e documento de auditoria independente; atlas de modelo e configuração; atas de ajuste de horário conforme art. 114, se houver; cópias independentes e autenticadas de BUs; explicações de seções agregadas/contingência. Sem essas fontes, estimar comportamento geral de 6.766 seções com dados ilustrativos seria inválido.
