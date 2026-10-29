# Pipeline de placebos e catálogo de eventos — Estudo 05 / integração Estudo 03

**Estado em 29/10/2026:** infraestrutura e testes **offline sintéticos** concluídos; **nenhum CSV ou log real do 2T2026 aberto**; execução em arquivos oficiais de 2024 e 1T2026 depende de obter um recurso isolado com licença, hash e esquema verificados. Este texto não é resultado empírico.

## Fontes identificadas e elegibilidade

1. **2024, 2º turno, prefeito:** portal oficial https://dadosabertos.tse.jus.br/dataset/resultados-2024 ; recursos de votação por seção e arquivos de urna: https://dadosabertos.tse.jus.br/dataset/resultados-2024-arquivos-transmitidos-para-totalizacao. Muitos conjuntos por UF abrangem mais de um turno; selecionar e confirmar o conteúdo antes de processar, pelo campo \`NR_TURNO\`. O período 2T2024 é o **placebo municipal**; suas regiões e candidaturas não correspondem a 2026.
2. **2026, SOMENTE 1º turno:** https://dadosabertos.tse.jus.br/dataset/resultados-2026 . O próprio portal informa atualização ao fim de cada turno; **não confiar no nome genérico “resultados 2026” como declaração de isolamento**. Só é permitido usar cópia cuja origem e versão comprovem que contém exclusivamente 1T2026. Recursos que reúnam 1T+2T2026 não podem ser abertos agora por causa da decisão D4.
3. **Resultados oficiais nacionais (agregados):** margem verificada em [VALIDACAO_MARGEM_20261029.md](VALIDACAO_MARGEM_20261029.md); esses números são conhecidos, não servem como ocultação da exposição anterior.

## Módulos implementados

- \`pipeline_placebo.py\`: lê somente CSV/ZIP **local e isolado** com manifesto JSON contendo período, \`isolated=true\`, URL de origem HTTPS, ID de recurso, licença e hash SHA-256. Rejeita \`2T2026\` e períodos desconhecidos, recurso sem hash, arquivos que misturem 2026 com qualquer outro turno (no período 2T2024, as linhas do 1T2024 do mesmo recurso são ignoradas e contadas em `skipped_other_turn_rows`), schema inesperado e descompasso de hash. Processa registros em streaming; agrega **todos os votos por seção** para o cargo apropriado (prefeito 2024, presidente 2026) e preserva votos de outros candidatos no 1T2026. Não tenta estimar horário sem confirmação externa e ID de local. Não faz downloads.
- \`../03_pianista/etapas/02_parser/contrato_eventos.py\`: contrato para eventos já normalizados, catálogo por tipo e cálculo do percentil 1 de intervalos biométricos no J0 do 1T2026, no sentido definido no pré-registro v1.1 do Estudo 03. **Não é decodificador de \`.logjez\`**. É necessário identificar e validar códigos/mensagens reais e fuso antes dos itens 1.4/1.5; jamais deduzir que um evento foi biométrico sem documentação.
- O \`coleta.py\` legado do Estudo 03 passa a recusar \`--download\` quando a busca contém 1T ou 2T de 2026, devido ao risco de recurso de período misto. Descoberta de **metadados** continua permitida, sem arquivos-alvo. O diretório padrão de brutos foi deslocado para \`data/coleta_03\`.

## Exemplo de manifesto **FICTÍCIO**

\`\`\`json
{
  "period": "2T2024",
  "isolated": true,
  "origin_url": "https://cdn.tse.jus.br/URL-OFICIAL-DO-RECURSO-ISOLADO",
  "resource_id": "ID-REAL-DO-RECURSO-VALIDADO",
  "license": "LICENCA-CONFERIDA",
  "sha256": "SHA256-REAL-DE-64-HEXADECIMAIS"
}
\`\`\`

Não substituir a URL por um endereço inventado em coleta real. Preencher o manifesto **somente depois de verificar o recurso oficial**, calcular \`sha256sum\` do arquivo local e revisar o conteúdo do 1º turno, quando aplicável.

## Execução do parser local

\`\`\`sh
python -m unittest discover -s estudos/05_simulacao_temporal -p 'test_*.py' -v
python -m unittest discover -s estudos/03_pianista/etapas/02_parser -p 'test_*.py' -v

python estudos/05_simulacao_temporal/pipeline_placebo.py \
  --period 2T2024 \
  --csv data/2024/2T/recurso-isolado.csv \
  --manifest data/2024/2T/manifest.json \
  --out data/saida/placebo-2024.json
\`\`\`

Para \`1T2026\`, trocar o período e paths **somente se o arquivo for comprovadamente exclusivo do 1T**. O parser bloqueia \`2T2026\` mesmo se o operador passar esse período explicitamente.

## Quais tarefas podem ser consideradas concluídas?

| Tarefa | Situação |
|---|---|
| Determinar fontes oficiais e regras de isolamento | Feito em documentação; escolha de recurso específico por UF ainda não certificada |
| Parser de votação por seção (CSV com contrato) | Implementado e **testado somente com dados sintéticos** |
| Baixar/processar dados reais de 2T2024 | **Não executado** |
| Baixar/processar dados reais exclusivamente de 1T2026 | **Não executado** |
| Interpretar/decodificar \`.logjez\` oficial | **Não implementado**; é necessário verificar esquema da versão |
| Gerar catálogo de eventos (item 1.4) | Implementado como contrato para eventos normalizados; **sem catálogo empírico** |
| Estimar dt* (item 1.5) | Implementação do cálculo, com mínimo de 100.000 intervalos; **dt* não estimado** |
| Teste confirmatório Estudo 05 em microdados 2T2026 | **Bloqueado** por D4 / GATE 1.6 / E05-0 |

## Cuidados

Sem identificação de local de votação e comprovação externa do **fim da votação** não existe contraste de efeito fixo no mesmo local: os pares devem ser marcados como **não estimáveis**, não substituídos por comparação nacional. Não usar horário de geração de BU ou recepção como indicador de eleitor ainda votando. Não tratar uma diferença estatística como fraude.

O TSE pode oferecer dados por seção em CSV e artefatos por seção em ZIP com esquemas distintos; o parser CSV **não** faz engenharia reversa de BU, RDV ou log. Sua atribuição é normalizar dados tabulares. O dicionário de mensagens de log precisa de seu próprio adaptador validado e revisão humana antes do estudo confirmatório.

## Atualizacao de status (29/10/2026)

Este documento descreve o estado inicial, anterior ao relatorio [RESULTADO_PLACEBO_2T2024_TO_20261029.md](RESULTADO_PLACEBO_2T2024_TO_20261029.md), que informa execucao real de Palmas. Declaracoes anteriores de 'nenhuma execucao real' estao **superadas para Palmas**, mas nao equivalem a reproducao externa nem a analise nacional. Ver [auditoria](../../auditoria/AUDITORIA_TRANSVERSAL_20261029.md).
