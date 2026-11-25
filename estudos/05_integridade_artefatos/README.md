# Estudo 05 - Integridade dos artefatos publicos do TSE (pleito 2026)

## Perguntas

1. Primaria (F2): existe hash de sistema divergente entre UFs no mesmo pleito,
   ou entre a lista publicada hoje e a publicada antes do pleito?
2. Secundaria (F3): existe artefato de assinatura que nao fecha (certificado,
   cadeia, QR, BU, RDV, aux.json)?
3. Terciaria (F4, so com orcamento aprovado): existe anomalia de log compativel
   com injecao?

Nao-objetivo: concluir se houve fraude. Teto estrutural de classe: B
(ver `CONCILIACAO.md`, C12).

## Arquivos

| Arquivo | Funcao |
|---------|--------|
| `PLANO.md` | Plano de execucao, versao 0, como recebido |
| `CONCILIACAO.md` | Ajustes C01-C14 frente ao contrato de evidencia e aos Estudos 03 e 04; decisoes D1-D4 |
| `DECISOES.md` | Registro append-only de decisoes |
| `src/`, `fixtures/`, `out/`, `keys/` | Codigo, amostras de teste, saidas e chave publica do coletor |

Dados brutos ficam em `data/estudo05/`, fora do Git.

## Status

| Fase | Situacao |
|------|----------|
| F0 Bootstrap | Parcial: selftest F2 verde; buildinfo e minisign pendentes |
| F1 Congelamento de L1 | Gate reprovado em 25/11: CDN do TSE recusa o IP de nuvem (403). Fallback D3 na maquina do proponente |
| Pre-registro | Registrado (entrada 07, 2026-11-25) |
| F2-F5 | Nao iniciadas |
