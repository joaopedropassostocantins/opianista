# Contribuicao ChatGPT — teste independente de cadencia temporal (28–29/10/2026)

Esta pasta contem **material para revisao tecnica**, nao resultados de um estudo concluido ou versao aprovada da Etapa 0.

## Conteudo
- `PROTOCOLO_CADENCIA_VOTACAO.md`: especificacao de comparacao temporal entre 2024 municipal e 2026 presidencial.
- `auditoria_temporal.py`: parser experimental de logs e testes pareados por secao/municipio.
- `requirements.txt`: dependencias minimas declaradas.

## Restricao do usuario (obrigatoria)
**Nenhum 2o turno presidencial anterior a 2026 pode compor o paradigma historico, sua calibracao ou os placebos primarios deste modulo.**

Referencia primaria: **2o turno municipal para prefeito em 2024**. 2016/2020 municipais somente mediante verificacao de disponibilidade e comparabilidade. Segundos turnos estaduais apenas como estudo secundario, pois coincidem em horario com a votacao presidencial.

## Situacao verificada
O arquivo Python compila e oferece a CLI `extrair`/`testar`. O material afirma ter passado por verificacao com dados sinteticos, mas os scripts ou registros dessa verificacao nao foram versionados nesta entrega. **Nao ha teste executado com logs oficiais completos; nao existem estimativas reais, valor-p ou conclusao sobre 2026.** A interpretacao de eventos `.logjez`, fuso, contingencias e reconciliacao com BU ainda exige revisao de arquivos reais.

## Integracao com a pesquisa pre-registrada
A branch principal ja possui `protocolos/00_prompt_preregistro_original_20261026.md`, Emenda 01 e uma Etapa 0 em revisao (PR #1). Esses protocolos incluem comparadores presidenciais que sao **incompativeis com a restricao acima para o estudo de cadencia historica**. Nao substitua, nao reescreva e nao incorpore essa especificacao como teste confirmatorio do preregistro ja existente. Submeta-a como proposta exploratoria ou nova emenda metodologica a deliberacao do coordenador, com exposicao previa aos dados e hash, antes de novos testes confirmatorios.

## Revisoes necessarias antes do uso empirico
1. Validar semantica e formato dos eventos dos logs em exemplos de todas as geracoes e urnas de contingencia.
2. Comparar contagens do log com BU em cada secao e documentar exclusoes.
3. Harmonizar fusos e horarios legais por municipio e ano; o script usa `--abertura-local` informado.
4. Testar pareamento de secoes alteradas/remanejadas e compatibilidade do numero de cargos.
5. Calcular poder e efeito minimo detectavel por municipio, com tamanho de efeito e IC, nao so valor-p.
6. Versionar testes sinteticos, amostras pequenas auditaveis e manifestos SHA-256.
7. Nenhum registro individual de eleitor/mesario deve ser publicado.
