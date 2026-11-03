# O Paradoxo do Arquiteto-Fiscal: da analogia do percurso à teoria da prova digital

Oct 26, 2026 · @Jp

## Tese central

O software não verifica o mundo; verifica representações do mundo que ele próprio foi programado para aceitar. O log, portanto, não é testemunho do fato. É testemunho do sistema sobre si mesmo.

A analogia de partida: um software é, grosso modo, um algoritmo lógico que encadeia ações para atingir um objetivo, como o deslocamento de casa até a faculdade. Cada ponto de controle do percurso (semáforo, cruzamento, carro ligado, tanque abastecido) gera um aviso de etapa concluída, e esse aviso, criptografado, é o log. Quem constrói o sistema sabe que basta emitir os avisos para que o programa considere o percurso cumprido, ainda que ele não tenha sido percorrido.

## 1 As quatro camadas do percurso

A fraude mora nas fronteiras entre quatro camadas que o algoritmo do percurso mistura.

| Camada | No percurso | No sistema | Quem controla |
| --- | --- | --- | --- |
| E — Evento | O carro passou pelo semáforo X | O fato no mundo físico | Ninguém (é a realidade) |
| S — Sensor | Algo detecta a passagem | Coleta de dados (GPS, clique, leitor) | O arquiteto escolhe o quê e como |
| R — Registro | "Etapa 3 concluída" | O log | O arquiteto define formato, momento e chave |
| I — Interpretação | "Ele percorreu o trajeto" | Inferência do auditor, do perito, do juiz | Quem lê, limitado ao que o arquiteto permitiu ver |

A criptografia protege apenas a passagem de S para R e a integridade de R depois de gravado; nada diz sobre a passagem de E para S. Assinatura digital prova quem disse e que o dito não foi alterado; não prova que o dito é verdadeiro.

O "voo" do exemplo é a ruptura entre E e S: o evento não ocorreu, mas o sensor, ou a rotina que deveria consultá-lo, emitiu o sinal de etapa concluída.

## 2 Taxonomia do insider

A "quarta dimensão" se escalona em quatro níveis: cada um vê mais premissas do que o anterior e, portanto, frauda com menos vestígios.

| Nível | Quem é | O que faz | O que o detecta |
| --- | --- | --- | --- |
| 1 — Forjador externo | Não conhece a arquitetura | Replica avisos observados (ataque de replay) | Criptografia e carimbo de tempo |
| 2 — Insider operador | Conhece as premissas | Explora as lacunas entre os pontos de controle, como o motorista que sabe onde estão os radares | Pontos de controle adicionais ou aleatórios |
| 3 — Insider arquiteto | Define onde, quando e como os logs nascem | Produz registros tecnicamente autênticos e materialmente falsos | Apenas fontes fora do seu domínio |
| 4 — Arquiteto do arquiteto | Controla as ferramentas com que o sistema é feito | Insere premissas que o próprio arquiteto desconhece | Builds reproduzíveis, auditoria da cadeia de suprimentos |

No nível 3, a perícia tradicional falha, porque tudo o que ela verifica (hash, assinatura, metadados) está conforme.

O nível 4 tem fundamento clássico: Ken Thompson demonstrou, na palestra do Prêmio Turing de 1984 ("Reflections on Trusting Trust"), que um compilador pode ser modificado para inserir uma porta dos fundos em todo programa que compilar, inclusive em novas versões de si mesmo, sem rastro no código-fonte. O caso SolarWinds (2020) é a versão empírica disso.

Consequência lógica: a confiança não se elimina; ela só se desloca para um nível acima. Toda verificação pressupõe um verificador em que se confia sem verificar.

## 3 Núcleo teórico: autorreferência

Proposição: nenhum sistema pode certificar a correspondência entre os seus registros e a realidade utilizando exclusivamente os seus próprios registros.

É o *quis custodiet ipsos custodes* de Juvenal traduzido para arquitetura de software. Há um paralelo útil, como analogia e não como demonstração, com a incompletude de Gödel: um sistema suficientemente expressivo não prova a própria consistência a partir de seus axiomas. Aqui, os axiomas são as premissas definidas pelo arquiteto.

Daí o **princípio da independência do observador**: o valor de um registro como prova é proporcional ao grau em que ele foi produzido fora do domínio de controle de quem tem interesse no seu conteúdo.

## 4 Quanto vale um log

Contra o arquiteto, a razão de verossimilhança do log tende a 1: o registro é tecnicamente perfeito e epistemicamente inútil.

O peso probatório de um log L em relação à hipótese H (percorreu o trajeto) contra F (fraude) é:

```latex
RV = \frac{P(L \mid H)}{P(L \mid F)}
```

- Contra o forjador de nível 1, P(L | F) é baixíssima, RV é alta e o log pesa muito.
- Contra o arquiteto de nível 3, P(L | F) ≈ 1, porque ele produz o log válido quando quiser. Então RV ≈ 1 e o log não altera a probabilidade da hipótese.

Essa é a formulação precisa da supervalorização: o sistema de justiça trata o log como se RV fosse alta, sem perguntar quem tinha poder de produzi-lo.

O arquiteto é derrotado pelas fontes que não controla. Mesmo voando, ele deixa resíduos fora do próprio sistema: odômetro e consumo de combustível inalterados, estação rádio-base do celular, câmera de trânsito municipal, pedágio, o aluno que o viu chegar por outro lado. Com n fontes independentes, cada uma com probabilidade pᵢ de revelar a incongruência:

```latex
P(\text{detecção}) = 1 - \prod_{i=1}^{n} (1 - p_i)
```

O insider perfeito só vence se controlar todas as fontes, e o custo disso cresce de forma combinatória. É o princípio de Locard em versão digital: todo contato deixa vestígio, mas o arquiteto só controla os vestígios do próprio sistema. Dez logs do mesmo servidor valem, contra o arquiteto, o mesmo que um; a prova robusta converge de domínios ortogonais.

## 5 O insider perfeito existe: casos reais

A analogia deixa de ser hipótese diante de casos documentados.

| Caso | Ano | Nível | Mecanismo |
| --- | --- | --- | --- |
| Volkswagen (Dieselgate) | 2015 | 3 | O software detectava o teste de laboratório e só nessa condição emitia poluentes dentro da norma |
| Stuxnet | 2010 | 3 | Ao sabotar centrífugas iranianas, reproduzia aos operadores leituras normais gravadas antes |
| Horizon (Post Office, Reino Unido) | 1999–2015 | 3 | Agentes postais processados com base em divergências do sistema, sob presunção de correção do computador; a fornecedora podia alterar dados remotamente |
| SolarWinds | 2020 | 4 | Atualização legítima e assinada distribuiu código malicioso a milhares de clientes |
| Sistemas da Odebrecht | 2023 | 3 | STF declarou imprestáveis provas extraídas da contabilidade paralela por problemas de integridade e cadeia de custódia \[VERIFICAR: número da reclamação e alcance da decisão\] |

O Horizon é o caso-padrão de supervalorização do log no processo penal; o Dieselgate é o mais didático para abrir uma aula.

## 6 Aplicação aos crimes digitais e à prova penal

A teoria fornece uma régua para valorar a prova digital: o registro produzido no domínio de quem tem interesse no seu conteúdo não basta, sozinho, para provar fato decisivo.

1. **Cadeia de custódia (arts. 158-A a 158-F do CPP).** A lei protege o vestígio a partir da coleta. No meio digital há uma "pré-custódia": tudo o que ocorreu entre o evento e a geração do log, sob controle do arquiteto. A pergunta da defesa não é só "o arquivo foi preservado?", mas "quem definiu as regras que o produziram, e com que interesse?".
2. **Logs de provedores (Marco Civil, arts. 13 e 15).** O provedor é arquiteto, guardião e fornecedor do registro. Isso não invalida o registro, mas impede tratá-lo como autoevidente quando for o elemento decisivo.
3. **Prints e capturas de tela.** O STJ tem exigido demonstração de integridade para capturas de aplicativos de mensagem \[VERIFICAR: precedentes recentes da Quinta e Sexta Turmas\]. Quem tira o print é o arquiteto daquele registro.
4. **Contraditório técnico.** Se o log é a declaração do sistema, a defesa tem direito de interrogar o declarante: acesso a código-fonte, documentação de arquitetura e perito assistente (art. 159, §§ 3º a 5º, do CPP).
5. **Crimes do próprio arquiteto.** Inserção de dados falsos em sistema de informações (art. 313-A do CP), modificação não autorizada de sistema (art. 313-B) e fraudes internas em instituições financeiras são crimes de nível 3 por definição. A investigação que só lê os logs do sistema comprometido pede ao suspeito que confirme o próprio álibi.
6. **Agentes de IA.** Sistemas que relatam "tarefa concluída" sem concluí-la (*reward hacking*) são o insider automatizado: o agente aprende que o avaliador confere o aviso, não o percurso.

## 7 Logs sociais: extensão à análise da sociedade

Toda instituição moderna governa por registros, e por isso o paradoxo transcende o software. A Lei de Goodhart (quando a medida vira meta, deixa de ser boa medida) e a Lei de Campbell (quanto mais um indicador orienta decisões sociais, mais se corrompe) são o mesmo paradoxo em linguagem econômica.

| Domínio | O "aviso" | O percurso que pode ser voado |
| --- | --- | --- |
| Segurança pública | Autos lavrados, taxa de homicídios | Produtividade medida por autos produz autos; homicídio reclassificado como "morte a esclarecer" melhora a estatística sem salvar ninguém |
| Educação | Lista de presença, diploma | O registro de presença não comprova aprendizagem |
| Compliance e ESG | Política, treinamento, relatório, autoavaliação | Programa de integridade sem auditoria independente é aviso sem percurso |
| Estado | Indicador produzido pelo próprio órgão executor | RV ≈ 1; argumento empírico para observatórios independentes |

Em chave filosófica, é o simulacro de Baudrillard: o registro passa a preceder e substituir o fato. A sociedade do log não pergunta se o percurso aconteceu; pergunta se os avisos chegaram.

## 8 Contramedidas de arquitetura

Um sistema que o arquiteto não engana separa quem define, quem executa e quem registra.

1. **Segregação de funções** entre quem define as regras, quem executa e quem registra (a velha lição da auditoria contábil).
2. **Logs em domínio externo e somente-anexáveis** (*append-only*), como os registros públicos de transparência de certificados digitais: o arquiteto escreve, mas não apaga nem reescreve, e terceiros conferem.
3. **Builds reproduzíveis e auditoria de código por terceiros**, contra o nível 4.
4. **Redundância heterogênea**: sensores de naturezas diferentes, mantidos por partes com interesses opostos.
5. **Presunção processual invertida**: registro produzido no domínio de parte interessada não é, isoladamente, prova suficiente de fato decisivo.

## Síntese

> O log não é simplesmente o registro de que algo aconteceu. É a declaração de um sistema sobre si mesmo, cujo valor probatório é exatamente igual à independência de quem escreveu as regras que o produziram.

Versão de quadro: o sistema não sabe se você foi de carro ou voando. Ele só sabe que os avisos chegaram. E quem decidiu quais avisos bastavam foi você.

**Pontos a confirmar antes de levar à aula**

- [ ] Decisão do STF sobre os sistemas da Odebrecht (2023): número da reclamação e alcance
- [ ] Precedentes recentes do STJ sobre integridade de prints de aplicativos de mensagem