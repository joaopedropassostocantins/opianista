# Estudo 05 — simulação temporal dos eventos, logs e relatórios (17h–19h)

**Status:** exploratório; criado em 29/10/2026. Este novo estudo não modifica pré-registros aprovados dos Estudos 01 ou 03.

## Pergunta

Em uma eleição cujo encerramento regular é previsto às 17h no horário de Brasília, mas na qual podem ocorrer filas ou uma extensão excepcional até 19h, como verificar a coerência entre estado, horário, eventos de voto, geração do BU, logs e relatórios? Uma discrepância observável perto de uma fronteira horária justificaria inspeção dos componentes de relógio?

**O segundo turno de 25/10/2026 teve decisão excepcional de extensão até 19h**, segundo comunicação oficial do TRE-DF. Isso não demonstra, por si só, que subsistemas perderam proteção ou que votos foram inseridos indevidamente.

### Referências normativas

- [Resolução TSE nº 23.759/2026, art. 29](https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-759-de-26-de-fevereiro-de-2026): encerramento às 17h, salvo fila já presente; controle por senhas.
- [TRE-DF, 27/10/2026](https://www.tre-df.jus.br/comunicacao/noticias/2026/Outubro/tredf-informa-quantidade-de-votos-computados-apos-as-17-horas-no-segundo-turno-das-eleicoes): reconhece extensão até 19h, diferenciando essa prorrogação da fila regular.
- [TSE: após o encerramento](https://www.tse.jus.br/comunicacao/noticias/2026/Setembro/faltam-7-dias-veja-qual-e-o-caminho-do-voto-depois-de-encerrada-a-votacao): elaboração do BU, mídia de resultado, transmissão, verificação e totalização.

## Base técnica e limites

A referência pública [urna-vota-decompiled](https://github.com/igoroalonge/urna-vota-decompiled), de Igor Alonge, é uma **reconstrução** do WebAssembly do simulador de votação, identificada pelo autor como versão 10.23.0.1 de DESENVOLVIMENTO. Não é o código-fonte original, não compila como o sistema de produção e **não é o executável das urnas lacradas de 2026**.

Foram examinados no repositório público:
1. Componentes de checagem de horário da thread do operador: src/uenux2/src/app/vota/operador/comum/cinformacaothreadoperador.cpp;
2. Estado associado a indicação de término de horário: src/uenux2/src/app/vota/operador/outrasopcoes/chorariovotacaoterminou.u34.cpp;
3. Geração do boletim: src/uenux2/src/app/vota/eleitor/fimvotacao/cgerabu.h;
4. Log de início e término de relatórios: src/uenux2/src/app/comum/log/ieventoslog.u35.cpp;
5. Segundo a própria documentação do projeto, a thread do operador **não executa na experiência web normal**.

**Não há demonstração aqui de uma vulnerabilidade do VOTA, nem comprovação de funcionamento distinto após 17h ou 19h no sistema lacrado.** A implementação do site é uma máquina de estados sintética, independente do WASM. Não usa hardware da urna nem gera arquivos oficiais/assinaturas.

## Hipóteses exploratórias (sem estatuto de pré-registro)

- **H0:** horários, transições e registros permanecem coerentes com fila e extensão legalmente autorizadas.
- **H1:** incoerência verificada perto de 17h/19h pode justificar revisão específica do componente de horário.
- **H2:** diferenças verificáveis entre dados públicos do BU, RDV, log e assinatura devem ser investigadas após controlar diferenças esperadas de gravação e contingência.
- **H3:** fusos e relógios, se interpretados incorretamente, produzem alertas falsos e podem afetar comparação com cronologia do encerramento.
- **H4:** geração, impressão ou transmissão após 19h **não implica** voto após 19h.
- **H5:** o contraste com fontes fora do domínio de software pode aumentar a capacidade de verificação de afirmações sobre o evento real.

## Produto implementado

O site apresenta um laboratório interativo que percorre 16:55–19:15 e mostra:
- Cenário regular sem fila; continuação dos eleitores que já estavam na fila; extensão excepcional assumida válida; e extensão com lacuna de log **artificialmente criada no modelo**; e injeção fictícia de evento posterior ao encerramento.
- Estado temporal, eventos da seção, linhas de log fictícias e totais de BU fictício.
- Alarmes de consistência do próprio modelo, detecção de eventos posteriores ao BU sem alterar retroativamente seu conteúdo e marcadores ainda não avaliados quando seria necessária evidência real.
- Testes unitários que demonstram a detecção da lacuna artificial, sem atribuí-la ao software eleitoral.

Arquivos: site/src/lib/temporal-simulator.ts; site/src/components/TemporalSimulator.ts; site/tests/temporal.test.mjs.

**A correspondência 1 evento de voto para 1 linha de log foi inventada como contrato do modelo. Não pode ser presumida nos logs reais sem validação técnica.** Os totais fictícios de A/B/BRANCO/NULO não são dados do TSE.

## Plano de verificação futura (somente fontes públicas e ambiente autorizado)

1. Registrar versão/hash e limitações da reconstrução; distinguir símbolos observados de nomes inferidos.
2. Fixar hipóteses, critérios de exclusão e regras de detecção antes da abertura dos dados-alvo do estudo.
3. Obter documentos oficiais públicos com trilhas de origem, hashes e documentação da versão/modelo.
4. Mapear quais eventos efetivamente constam em log, RDV e BU e quais dependem de ata ou observação externa.
5. Normalizar o horário real da seção para Brasília, separando hora do voto, encerramento, impressão, geração e recepção no totalizador.
6. Testar falsos positivos com filas, falhas de gravação, contingência e controle negativo.
7. Para análise de cadência, manter o 2º turno **municipal** como paradigma principal, sem usar turnos presidenciais históricos como paradigma de cadência; eventuais controles técnicos por formato são outra questão.
8. Realizar qualquer ensaio do binário lacrado apenas mediante autorização em ambiente institucional apropriado.

**Regra editorial:** não tratar um alerta sintético como resultado empírico; resultados nulos e explicações alternativas devem ser publicados com o mesmo destaque que sinais positivos.
