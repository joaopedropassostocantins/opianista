# opianista

Analisando o Brasil: pesquisa aberta, pre-registrada e reprodutivel sobre os
registros publicos de urna das Eleicoes 2026, com foco no 2o turno de
25/10/2026.

O projeto detecta e quantifica ANOMALIAS em dados publicos do TSE e testa
explicacoes alternativas. Nao parte da premissa de fraude nem da premissa de
ausencia de fraude. Todo teste que relacione anomalia a resultado eleitoral e
executado de forma simetrica para os dois candidatos, e resultados nulos sao
relatados com o mesmo destaque que resultados positivos.

## Estudos

| Estudo | Pergunta | Situacao |
|--------|----------|----------|
| [01 Prorrogacao (DiD)](estudos/01_prorrogacao_did/) | Votos apos 17h e prorrogacao alteraram a votacao por secao? | Pre-registrado; aguardando dados do 2T por secao |
| [02 Transferencia de votos](estudos/02_transferencia_votos/) | A captacao entre turnos foi atipica frente a 2022? | Exploratorio; codigo a publicar |
| [03 Mesario pianista](estudos/03_pianista/) | Ha assinaturas de insercao de votos pela mesa nos logs? | Piloto TO concluido: hipoteses nao sustentadas; execucao nacional pendente |
| [04 Auditabilidade](estudos/04_auditabilidade/) | Que tamanho de adulteracao o sistema consegue detectar? | Proposta de artigo |
| [05 Urnas de encerramento tardio](estudos/05_simulacao_temporal/) | Qual o perfil de TODOS os votos nas urnas que encerraram tardiamente? O relogio e verificavel? | Exploratorio; coortes e testes sinteticos |

Painel de coordenacao: [PLANEJAMENTO.md](PLANEJAMENTO.md).

## Estrutura

```
protocolos/     pre-registros e emendas (imutaveis), com hashes
estudos/        um diretorio por estudo
didatico/       material de aula, separado da pesquisa
site/           site editorial independente (Vite + TypeScript)
.github/        modelos de issue e de pull request
data/           dados brutos (fora do Git)
```

## Site editorial

A aplicacao em [site/](site/) e independente de `estudos/` e `protocolos/`: apresenta a tese do Arquiteto-Fiscal, acompanha o status dos estudos e encaminha os leitores aos documentos canonicos. Nao e resultado pericial. Foi implementada a partir do texto-base preservado; o codigo-fonte original do ChatGPT Sites nao foi exportado.

Para desenvolver: `cd site && npm ci && npm run dev`. Para validar: `npm run typecheck && npm test && npm run build`. A publicacao nao e automatica.

## Como participar

Leia o [CONTRIBUTING.md](CONTRIBUTING.md). As frentes mais uteis agora:

1. Parser de logs de urna (`.logjez`) validado no 2o turno de 2022.
2. Catalogo das mensagens de evento do log, com revisao humana.
3. Reproducao independente: rodar o mesmo codigo e comparar resultados.
4. Red team: propor explicacoes alternativas para qualquer anomalia.

## Regras do projeto

1. Pre-registro antes dos dados. Mudancas de especificacao entram como emenda
   em `protocolos/`, nunca por edicao de arquivo ja registrado.
2. Nada de dado, URL, mensagem de log ou resultado presumido.
3. Dados brutos nao entram no Git. Fontes e hashes ficam registrados em cada
   estudo.
4. Nenhum mesario, eleitor ou servidor e identificado. Dados pessoais sao
   pseudonimizados na ingestao (LGPD).
5. Filmagens e dados de telecomunicacoes estao fora do escopo; constam apenas
   como recomendacao de diligencia a autoridade competente, mediante ordem
   judicial.
6. Codigo em Python 3.11+, seeds fixas, scripts completos, sem emojis.

## Aviso

Este repositorio e um projeto de pesquisa independente. Anomalia estatistica
nao e prova de crime. Nenhuma analise aqui deve ser divulgada como conclusao
sem o protocolo, o codigo, o poder de deteccao e as explicacoes alternativas
que a acompanham.

## Licenca

Codigo: MIT ([LICENSE](LICENSE)). Textos, protocolos e relatorios: CC BY 4.0.
