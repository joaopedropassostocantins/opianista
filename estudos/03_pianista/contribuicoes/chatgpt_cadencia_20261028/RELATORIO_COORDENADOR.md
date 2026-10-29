# Relatorio tecnico de transferencia ao coordenador — opianista

**Data:** 29/10/2026 (UTC)  
**Origem:** trabalho em ChatGPT/Work, consolidado para revisao humana  
**Repositorio-alvo:** `joaopedropassostocantins/opianista`  
**Status:** entrega de codigo exploratorio, protocolo metodologico nao aprovado, material didatico e registro de pendencias. **Nao executar merge como estudo confirmatorio antes da deliberacao do GATE 0.**

## 1. Resumo executivo

Esta contribuicao traz duas frentes distintas:

**A. Estudo 03 — cadencia temporal e hipotese dos "mesarios pianistas".**
Foi desenhado um teste da distribuicao de votos por horario, com foco em 16h–17h e nos intervalos menores, comparando **segundos turnos municipais para prefeito** com o **segundo turno presidencial de 2026**. O programa experimental em Python extrai eventos temporais de logs e calcula contrastes pareados na mesma secao. O estudo **ainda nao foi executado em microdados oficiais completos**; nao ha coeficientes, IC ou valores-p reais calculados por esta entrega.

**B. Site O Paradoxo do Arquiteto-Fiscal.**
O site foi localizado no acervo ChatGPT Sites (link na secao 5); seu texto-base de 26/10/2026 foi preservado, e uma versao estatica navegavel em HTML/CSS foi produzida em `didatico/sites/`. Como o codigo-fonte nativo do ChatGPT Sites nao esta exportavel neste ambiente, a versao HTML e **uma reconstrucao funcional, e nao replica tecnica ou visual exata**. Publicacao GitHub Pages nao foi ativada.

A proposta separa pesquisa empírica, formulacao metodologica e divulgacao didatica, como exige o README atual.

## 2. Materiais desta entrega integrados na branch de revisao

| Caminho relativo | Funcao | Estado |
|---|---|---|
| `estudos/03_pianista/contribuicoes/chatgpt_cadencia_20261028/PROTOCOLO_CADENCIA_VOTACAO.md` | hipoteses, amostras e decisao estatistica | para parecer do coordenador; nao aprovado |
| `estudos/03_pianista/contribuicoes/chatgpt_cadencia_20261028/auditoria_temporal.py` | extracao exploratoria de logs, percentuais por quarto de hora, teste pareado e triagem | compila e responde ao --help; parser e inferencia ainda dependem de validacao real |
| `estudos/03_pianista/contribuicoes/chatgpt_cadencia_20261028/requirements.txt` | dependencias Python | declarado |
| `estudos/03_pianista/contribuicoes/chatgpt_cadencia_20261028/README.md` | instrucao, restricao dos comparadores e riscos | disponivel |
| `didatico/sites/arquiteto_fiscal_evidencia/conteudo_base_20261026.md` | texto teorico de origem | preservado |
| `didatico/sites/arquiteto_fiscal_evidencia/index.html` | pagina autonoma de divulgacao | implementada, nao publicada via GitHub |
| `didatico/sites/arquiteto_fiscal_evidencia/README.md` | proveniencia, limite de fidelidade, preview | disponivel |
| `.../RELATORIO_COORDENADOR.md` | presente relatorio de transferencia | disponivel |

**Todos esses arquivos estao apenas na branch de revisao; a branch `main` nao foi modificada por esta contribuicao.**

## 3. Delimitacao substantiva: paradigma historico exigido pelo proponente

**Regra obrigatoria para este modulo:** nao usar *nenhuma* eleicao presidencial anterior a 2026 na amostra de referencia, no processo de calibracao ou como paradigma das medias por horario.

- **Controle principal:** 2o turno **municipal** de 2024, para prefeito, um cargo. Unidades: municipio, zona, secao, identificador oficial harmonizado.
- **Sensibilidade:** segundos turnos municipais de 2016 e 2020 somente com logs elegiveis. 2020 necessita controle adicional pelos efeitos da pandemia.
- **Controle estadual secundario:** segundos turnos de governador de 2014, 2018 e 2022, **nao independentes** do fluxo da eleicao presidencial nos mesmos dias. Nao substituir o controle municipal por esses dados.
- **Alvo:** segundo turno presidencial de 2026; separar as UFs onde houve segundo turno simultaneo para governador (numero de cargos distinto), bem como fusos e cronologia de encerramento.

A inferencia nacional a partir de municipios que tiveram segundo turno municipal em 2024 e limitada por selecao amostral. As cidades sao grandes e nao representam automaticamente zonas rurais e localidades sem segundo turno municipal.

### 3.1 Hipoteses e medida

Para secao `s` e eleicao `y`:

`p_s,y = votos computados entre 16h–17h / votos computados entre 8h–17h`

`delta_s = p_s,2026 - p_s,2024`

**H0:** media das diferencas municipais pareadas igual a zero.  
**H1:** media das diferencas municipais pareadas diferente de zero, teste bilateral, alfa 0,05.

Teste t com municipio como unidade inferencial e bootstrap por municipio, reportando efeito em pontos percentuais e IC95%. A margem de equivalencia ±0,5 pp e o limiar de materialidade 0,5 pp **sao propostos, nao validados**. Diferencas estatisticamente significativas nao identificam, por si, insercao ficticia de votos.

Hipoteses auxiliares: padrao nos intervalos de 15 minutos, sequencias de votos com intervalo reduzido, modalidades de habilitacao, comparecimento/abstencao, heterogeneidade por municipio e seções vizinhas. A presenca real de eleitores exige fontes independentes e legalmente obtidas.

## 4. Compatibilidade com o repositorio existente e o GATE 0

Foram inspecionados: `README.md`, `CONTRIBUTING.md`, `protocolos/00_prompt_preregistro_original_20261026.md`, `protocolos/01_emenda_20261028_pianista.md`, `protocolos/REGISTRO.md`, `estudos/03_pianista/README.md`, `estudos/03_pianista/fundamentacao_metodologica.md` e o PR **#1**, ainda aberto, com proposta da Etapa 0 v1.1.

**Incompatibilidade para resolver:** o protocolo ja versionado e o PR #1 admitem segundos turnos presidenciais anteriores como controles/placebos, enquanto a diretriz expressa desta frente proibe sua utilizacao **como paradigma historico de cadencia**. Nao e correto reescrever retroativamente o preregistro ou chamar de confirmatoria uma hipotese amadurecida apos observacao de dados de 2026.

**Recomendacao ao coordenador:** manter o estudo original e seu hash intocados; definir esta abordagem como **submodulo independente de cadencia municipal (exploratorio)**, ou submeter nova emenda prospectiva com status explicitamente pos-exposicao, antes de incorporacao confirmatoria. Isso permite coexistencia de estudos de objetos diferentes sem confundir conjuntos de controle.

**Outra pendencia ja registrada no projeto:** `protocolos/REGISTRO.md` informa que o arquivo historico `00_preregistro.md` (hash registrado) nao esta presente no repositorio. A contribuicao nao o reconstruiu nem alterou o registro. Verificar antes de declarar cadeia de preregistro completa.

### 4.1 Lacunas de engenharia que impedem interpretacao empirica

1. **Formato dos logs:** o parser depende de padroes de mensagens textuais; validar catalogo de eventos por geracao de urna e firmware, inclusive contingencia, antes de aceitar campos de modalidade.
2. **Conciliacao:** verificar para cada secao o total de votos no log contra comparecimento/BU; o script prepara contagens mas **nao implementa ainda um gate de conciliacao BU externo**.
3. **Fusos/horarios:** `--abertura-local` exige especificacao manual; nao ha mapeamento automatico e auditado de fuso por municipio/ano.
4. **Pareamento:** a chave UF+municipio+zona+secao pode mudar com remanejamentos; exigir checagem cadastral historica e rastrear perdas.
5. **Contingencias:** logs multiplos ou urna substituida exigem reconciliacao documental; a exclusao e temporaria e deve ser quantificada.
6. **Teste de inferencia:** documentar potencia estatistica, erros agrupados, possivel viés de selecao e robustez em cidades pouco representativas.
7. **Triagem local:** qualquer flag por secao e exploratoria; controlar falsos positivos, auditar dados subjacentes e preservar anonimato.
8. **Reprodutibilidade:** incluir fixtures sintéticas, testes automatizados, manifesto de dados com URL, data, hashes SHA-256 e comandos de execucao por UF.
9. **Privacidade:** proibida identificacao publica de eleitores, mesarios e servidores. Imagens e telecomunicacoes sao exclusivamente recomendacoes de diligencias legais por autoridade competente; nao integrar coleta privada.

O teste `python -m py_compile` e a CLI `--help` foram executados sem falhas no ambiente de trabalho. Nao equivale a validacao da exatidao do parser.

## 5. Site: proveniencia, materiais e integracao

**Titulo:** O Paradoxo do Arquiteto-Fiscal.  
**Site original:** https://arquiteto-fiscal-evidencia.hazyzebra6.chatgpt.site  
**Categoria:** material didatico/ensaio teorico sobre limites de logs, arquitetura de confianca, auditabilidade e fontes independentes.

O texto-base apresenta quatro camadas (evento/sensor/registro/interpretacao), taxonomia de tipos de insider, analogias historicas como Dieselgate e casos de sistemas, relacao com prova penal e propostas de verificacao independente. O texto aponta expressamente referencias a confirmar. **Essas analogias nao sao evidencia empirica de manipulacao eleitoral no Brasil.**

**Arquivos versionados:**
- `didatico/sites/arquiteto_fiscal_evidencia/conteudo_base_20261026.md`
- `didatico/sites/arquiteto_fiscal_evidencia/index.html` (HTML/CSS auto-contido, reconstruido a partir do Markdown)
- `didatico/sites/arquiteto_fiscal_evidencia/README.md`

**Avisos obrigatorios:** (i) origem ChatGPT Sites; (ii) nao foi obtido export do codigo original; (iii) a reconstrucao nao garante fidelidade visual nem funcional do site de origem; (iv) teses epistemologicas nao devem ser anunciadas como prova de fraude em 2026; (v) revisar fatos, jurisprudencia e citacoes antes de divulgacao editorial.

**Decisao pendente do coordenador:** manter apenas o link para o site original, disponibilizar preview do HTML em GitHub Pages por workflow, ou hospedar o HTML em outro dominio. Nenhuma publicacao automatica foi acionada.

## 6. Inventario de trabalhos anteriores relacionados, NAO incluidos nesta branch

Outros artefatos foram gerados em sessoes anteriores e permanecem fora deste PR, sujeitos a nova curadoria e validacao antes de migracao:

| Artefato | Conteudo | Estado/restricao |
|---|---|---|
| `votos_por_minuto.csv`, `votos_por_minuto.png` | acumulados por horario de encerramento de secoes, 17h00–17h30 | **nao** representam votos individuais emitidos em cada minuto; nao servem ao teste de cadencia |
| `comparacao_secoes_1730.png` | percentuais agregados em secoes encerradas antes/depois de 17h30 | descritivo, confuso com composicao geografica; nao atribui voto ao horario |
| `votos_invalidos_2010_2026_auditoria.csv`, `analise_votos_invalidos_2010_2026.py` | serie nacional de brancos/nulos | estudo distinto; exige validacao dos dados e protocolo proprio |
| `relatorio_emenda02_abnt.docx` | proposta de testes por secao para votos invalidos | sem microdados por secao, ainda nao executado |
| `2º turno de 2026_ prorrogacao sem indicio de fraude e teste falseavel da hipotese.pdf` | resumo de contexto, prorrogacao e testes propostos | pesquisa secundária; nao usar como substituto de dados oficiais |
| `O Paradoxo do Arquiteto-Fiscal.md` | texto-base do site | **incluido** na pasta editorial, com nome de origem normalizado |

**Nota:** valores de amostras parciais ou resultantes de estudos anteriores nao podem ser promovidos a conclusoes confirmatorias desta contribuicao.

## 7. Proposta de decisao (por prioridade)

**P0 — antes de merge como metodo cientifico:** resolver conflito dos paradigmas historicos e status pos-exposicao de 2026; obter parecer GATE 0; preservar os pre-registros e seus hashes.

**P1 — antes de rodar dados reais:** avaliar parser com logs oficiais reais, aderencia dos intervalos a eventos, correspondencia a BU, perfil das exclusoes e conveniencia dos estimadores por municipio; definir dicionario de dados.

**P1 — para o site:** revisar linguagem e referencias de casos, aprovar a versao estatica como espelho editorial com aviso de reconstrução, e escolher hospedagem. Nao associar o site a resultados empiricos.

**P2 — para reprodutibilidade:** pipeline com manifestos e checksums, CI para sintaxe e testes sintéticos, especificacao de licencas e revisao de acessibilidade do HTML.

**Decisao sugerida:** aceitar os arquivos como *contribuicao em revisao*; nao fundir os protocolos; pedir ao coordenador aprovar separadamente: (1) uso do submodulo empirico exploratorio; (2) publicacao da reconstrução do site.

## 8. Declaracao de limites

Este relatorio documenta **o que foi produzido, onde foi colocado e o que nao esta demonstrado**. Nenhum teste definitivo da hipotese de insercao de votos por integrantes da mesa foi realizado nesta entrega; nao existe identificacao de autores, evidencia de voto ficticio nem inferencia causal da eleicao 2026. O conteudo do site e material de discussao e formacao, nao acusacao.
