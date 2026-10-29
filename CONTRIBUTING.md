# Como contribuir

Obrigado pelo interesse. Este projeto so tem valor se qualquer pessoa, de
qualquer posicao politica, puder reproduzir e contestar cada resultado. As
regras abaixo existem para proteger isso.

## 1 Antes de comecar

1. Leia o README do estudo em que pretende trabalhar e o protocolo
   correspondente em `protocolos/`.
2. Abra uma issue usando um dos modelos antes de um pull request grande.

## 2 Tipos de contribuicao

| Tipo | Onde |
|------|------|
| Codigo (coleta, parser, analise) | Pull request no estudo correspondente |
| Reproducao independente | Issue "Relato de reproducao" |
| Proposta de hipotese ou teste | Issue "Proposta de hipotese" (vira emenda se aprovada) |
| Erro em dado, fonte ou codigo | Issue "Erro em dado ou codigo" |
| Explicacao alternativa para uma anomalia | Issue "Proposta de hipotese", marcada como red team |

## 3 Regras para pull requests

1. Scripts completos em `.py`, Python 3.11+, seed fixa, sem emojis, aspas
   ASCII retas, validados com `ast.parse`.
2. Dependencias novas em `requirements.txt`.
3. Nenhum dado bruto no Git (logs, BU, RDV, parquet). Registre URL, data de
   acesso e SHA-256 no manifesto do estudo.
4. Nenhum dado pessoal. Se um arquivo trouxer titulo, nome, CPF ou
   identificacao de mesario, pseudonimize na ingestao.
5. Nao edite arquivos de `protocolos/` ja registrados. Mudanca de
   especificacao exige emenda nova, aprovada antes de abrir os dados afetados.
6. Testes que relacionem anomalia e resultado devem rodar para os dois
   candidatos.
7. Resultados vao com tamanho de efeito, intervalo e poder de deteccao, nunca
   so com p-valor.

## 4 O que nao aceitamos

- Afirmacoes de fraude ou de lisura nao sustentadas pelo protocolo.
- Exposicao de pessoas: mesarios, eleitores, servidores ou candidatos.
- Dados obtidos contornando bloqueios de acesso ou sem base legal.
- Material de campanha ou propaganda de qualquer candidato ou partido.
- Ataques pessoais a colaboradores ou a autores de criticas.

## 5 Discordancia

Discordar de um resultado e bem-vindo: abra uma issue com o teste, o codigo
ou o dado que sustenta a discordancia. Criticas metodologicas recebem resposta
publica, e as procedentes entram no relatorio, inclusive quando contrariam
conclusoes anteriores.

## 6 Conduta

Ver [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
