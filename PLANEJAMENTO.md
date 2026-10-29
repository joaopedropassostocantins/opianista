# Planejamento do projeto

Atualizado em 29/10/2026. Este arquivo e o painel de coordenacao: o que esta
feito, o que vem a seguir, quem decide e o que bloqueia. Nao e protocolo e pode
ser editado livremente.

## 1 Situacao geral

| Estudo | Situacao | Proximo marco |
|--------|----------|---------------|
| 01 Prorrogacao (DiD) | Pre-registrado (00); coleta bloqueada em 26/10 por falta de dados do 2T | Validar pipeline no 2T 2022 |
| 02 Transferencia de votos | Exploratorio, sem codigo no repositorio | Publicar script Monte Carlo |
| 03 Mesario pianista | GATE 0 aprovado (v1.1); Etapa 1 iniciada | Corrigir coleta.py e rodar descoberta |
| 04 Auditabilidade | Proposta de artigo | Receber fichamento de Aranha et al. |

Fato novo relevante para o Estudo 01: o TSE informou 34.393 votos registrados
apos 17h no pais, contra margem de 4.430.191 votos. O teste de alteracao de
resultado pelos votos tardios fica limitado por esse numero; o estudo segue util
para documentar isonomia e para calibrar o parser compartilhado.

## 2 Estudo 03 - sequencia de trabalho ate a abertura do 2T 2026

Nada do 2o turno de 2026 e aberto antes do item 1.6.

| No | Tarefa | Responsavel | Depende de | Situacao |
|----|--------|-------------|------------|----------|
| 1.1 | Corrigir coleta.py (secao 3.1) | Claude ou colaborador | - | Pendente |
| 1.2 | Rodar coleta em modo descoberta (sem download) e revisar fontes.md | Colaborador | 1.1 | Pendente |
| 1.3 | Confirmar nos metadados e em amostra de logs do 1T 2026 que existem modalidade de habilitacao, timestamp e secao | Colaborador + revisao humana | 1.2 | Pendente |
| 1.4 | Catalogo de mensagens do log (Etapa 2 antecipada, so 1T 2026 e 2T 2022) | Claude | 1.3 | Pendente |
| 1.5 | Calcular dt* no 1T 2026 e rodar diagnostico de poder com insercoes simuladas | Claude | 1.4 | Pendente |
| 1.6 | Emenda com dt*, poder e lista de municipios com denuncia de transporte; aprovacao | Proponente | 1.5 | Pendente |
| 1.7 | Download e abertura do 2T 2026 | Colaborador | 1.6 | Bloqueado |

O parser das tarefas 1.4 e 1.5 serve tambem ao Estudo 01 (calibracao de sigma_d
e placebo S5 no 2T 2022).

## 3 Revisao das contribuicoes recebidas

### 3.1 coleta.py (commit a3fb63b, direto no main)

Boa base: usa a API oficial, registra URLs e SHA-256, comeca em modo descoberta.
Problemas a corrigir antes de qualquer `--download`:

1. **Abre o 2T 2026 cedo demais.** `--download` baixa todos os periodos, inclusive
   o 2T 2026, antes do dt* e do diagnostico de poder exigidos pelo protocolo
   v1.1. Precisa de trava: 2T 2026 so com opcao explicita e referencia a emenda
   aprovada (item 1.6).
2. **O filtro de UF nao e aplicado no download.** A UF so anota o registro; um
   piloto em TO baixaria arquivos do pais inteiro.
3. **Periodo pode sair trocado.** 1T e 2T de 2026 usam os mesmos termos de busca
   e os conjuntos sao deduplicados pelo primeiro periodo em que aparecem; um
   recurso do 1T pode ser rotulado e salvo como 2T, e vice-versa. O periodo
   deve vir do nome ou dos metadados do recurso.
4. **Dados brutos dentro do repositorio.** O diretorio padrao fica em
   `estudos/.../01_coleta/dados_brutos`, fora do padrao `data/` do .gitignore;
   arquivos .csv baixados poderiam ser commitados. Mudar o padrao para `data/`
   e incluir `dados_brutos/` no .gitignore.
5. Menor: `zipfile` importado e nao usado; falta teste com resposta simulada da
   API.

### 3.2 PR #2 - branch `handoff-cadencia-site-20261029`

Contribuicao produzida em outra ferramenta, com dois blocos:

- **Submodulo de cadencia:** proporcao de votos entre 16h e 17h, pareando secoes
  do 2T presidencial de 2026 com o 2T municipal de 2024 (prefeito), e proibindo
  qualquer eleicao presidencial anterior como referencia. Codigo testado so com
  dados sinteticos.
- **Material didatico:** reconstrucao estatica do site "O Paradoxo do
  Arquiteto-Fiscal" e seu texto-base.

O proprio relatorio de transferencia recomenda nao fundir esse protocolo com o
pre-registro e trata-lo como submodulo exploratorio. Concordo, com dois
acrescimos:

1. A "proibicao de eleicao presidencial anterior" contradiz o protocolo v1.1 ja
   aprovado, que usa o 2T 2022 como placebo. As duas coisas podem coexistir
   apenas se o submodulo for declarado exploratorio e o v1.1 permanecer
   intocado.
2. O controle municipal de 2024 tem limitacoes fortes: 51 municipios grandes,
   cargo e saliencia diferentes, e a hipotese ja foi formulada apos ver dados de
   2026. Serve como descricao comparativa, nao como teste confirmatorio.

O material do site e independente e pode entrar em `didatico/` apos revisao de
linguagem e referencias.

## 4 Decisoes pendentes do proponente

| No | Decisao | Opcoes |
|----|---------|--------|
| D1 | Destino do modulo de cadencia (PR #2) | (a) PR como submodulo exploratorio em `estudos/03_pianista/contribuicoes/`; (b) estudo separado (05); (c) nao incorporar |
| D2 | Site Arquiteto-Fiscal (PR #2; HTML autocontido, sem recursos externos) | (a) so link para o original; (b) HTML no repositorio sem publicacao; (c) publicar via GitHub Pages |
| D3 | Fluxo de trabalho no main | Exigir pull request para alteracoes no main (recomendado: ja houve dois commits diretos) |
| D4 | Abertura de dados do 2T 2026 para o Estudo 05 (classificacao por horario usa os mesmos dados-alvo do Estudo 03) | (a) bloquear ate o item 1.6 (recomendado); (b) abrir so BU e totalizacao, por emenda; (c) abrir tudo, rebaixando o Estudo 03 a exploratorio no 2T 2026. Ver `estudos/05_simulacao_temporal/REVISAO_METODOLOGICA_20261029.md` |

## 5 Pendencias de documentos

| Item | Por que importa | Situacao |
|------|-----------------|----------|
| `protocolos/00_preregistro.md` original | Sem ele, o hash registrado nao pode ser conferido | Pendente |
| Codigo e dados da amostra de 2,1% | Necessario para analisar com e sem a amostra exposta | Pendente |
| Fichamento de Aranha et al. (DOCX) | Base do Estudo 04 | Pendente |
| Tres PDFs de anotacoes | `didatico/` | Pendente |
| Artefatos listados no relatorio de transferencia (votos invalidos 2010-2026, emenda 02 ABNT) | Possivel estudo novo; exigem protocolo proprio | Avaliar |

## 6 Riscos

| Risco | Mitigacao |
|-------|-----------|
| Abrir dados do 2T 2026 antes das emendas | Trava na coleta (3.1, item 1) e PR obrigatorio |
| Multiplos protocolos concorrentes para a mesma hipotese | Um so confirmatorio (v1.1); demais rotulados exploratorios |
| Logs sem campo de modalidade de habilitacao | Item 1.3 antes de qualquer outro trabalho; se ausente, H1a e H1b nao sao executaveis |
| Licenca dos logs do 2T 2026 nao declarada | Nao redistribuir dados; publicar so agregados e codigo |
| Leitura publica de resultados parciais como conclusao | Aviso no README; relatorios so apos red team |

## 7 Prioridade maxima - Estudo 05 (urnas de encerramento tardio, BU integral, relogio e insider)

**Reorientacao de 29/10/2026:** a unidade de analise e a **secao/urna que encerrou tarde**; analisar **TODOS os votos** de cada BU dessa coorte, sem limitar a votos registrados depois das 17h. O horario registrado na propria urna e uma observacao interna com confiabilidade a validar, nao uma fonte independente. A pergunta "e se o relogio puder ser alterado?" torna obrigatoria a triangulacao por observacoes externas e testes de sensibilidade; nenhuma alteracao intencional foi demonstrada. O simulador de votos apos 17h e apenas educativo, subordinado ao novo painel de coortes.

Dados publicados TSE (28/10/2026): 497.333 secoes encerradas depois de 17h; 24.268 apos 17h10; **6.766 apos 19h**. Estes numeros contam secoes, nao votos, e podem abranger procedimentos de encerramento apos o ultimo voto. Consultar [plano revisado](estudos/05_simulacao_temporal/COORTES_HORARIO_NAO_CONFIAVEL.md). Metodo historico principal para cadencia: **segundos turnos municipais**, nunca turnos presidenciais como paradigma de fila.


**Novo estudo exploratorio:** [simulacao temporal](estudos/05_simulacao_temporal/README.md) e [analise de origem e totalizacao](estudos/05_simulacao_temporal/ANALISE_INSIDER_BU_TOTALIZACAO.md).

Perguntas tecnicas prioritarias, em ordem:

1. Habilitacao do eleitor: condicoes de abertura de sessoes e controles de horario.
2. Terminal do mesario: intervencoes do operador e estados de autorizacao.
3. Contabilizacao: votos nominais, brancos, nulos, sessoes incompletas e RDV.
4. Geracao do BU: origem dos totais e fixacao do resultado local.
5. Logs e persistencia: quais eventos ficam observaveis e quais nao.

**Duas hipoteses separadas:** (A) origem comprometida antes da emissao do BU, que nao e refutada por coerencia entre registros do mesmo subsistema; (B) diferenca de totalizacao central comparada aos BUs locais preservados independentemente, verificavel por recontagem por secao. Suspensao da recepcao e da totalizacao ate 19h nao prova vulnerabilidade e nao pode ser confundida com recebimento tardio normal.

**Entrega existente no PR #3:** painel didatico com fixtures totalmente sinteticas, sem execucao de urna real; testes automatizados e links ao codigo reconstruido de desenvolvimento do simulador VOTA. Revisao humana obrigatoria antes de confundir hipoteses, anomalias e prova.

**Proximos gates:** (i) validar fontes e horario de cada registro; (ii) obter BUs e logs oficiais com hashes; (iii) identificar copias preservadas fora do canal central; (iv) verificar compatibilidade da reconstrucao web com a versao de producao autorizada; (v) preregistrar testes confirmatorios antes dos dados-alvo. Sem alteracao de pre-registros anteriores.
