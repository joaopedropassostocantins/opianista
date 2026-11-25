# Inventario de evidencias - situacao em 2026-11-25

Classificacao inicial segundo `AGENTS.md`. Todos os campos factuais estao
pendentes de conferencia em fonte primaria (`verificado = false` nos
manifestos). Nenhum item tem, ate esta data, hash e carimbo de terceiro.

| Item | Camada | Teto real | Motivo | Manifesto |
|------|--------|-----------|--------|-----------|
| DataUrnas-BR | L2 | B | Verificacoes contra `.vsc`, catalogo SHA256SUMS; commits de out/2026 anteriores ao pleito; G4 falha | `artefatos/B/dataurnas-br/` |
| var-ue | L2 | B | Verifica assinatura MSE UE2009-UE2022; suporte a `.vsc` de 2026; G4 falha | `artefatos/B/var-ue/` |
| Totalizacao Paralela (CMInd) + Arvor | L2 | B (com ressalva) | Fonte externa ao TSE (QR do BU impresso), cobertura de dezenas de secoes | `artefatos/B/totalizacao-paralela-cmind/` |
| Cluster "votos apos as 17h" (4+ repositorios) | L2 | B fraco | Ferramenta reproduzivel, tese estatistica; G4 falha | a abrir |
| Brunazo, relatorio do PL, peritos | L3 | C/D | Reciclagem 2018/2022 sem binario novo | a abrir |
| "Urna votando sozinha por 2 h" (video) | L3 | D | Video sem log | a abrir |

## Conclusao provisoria

Nenhum item atual e classe A. O `.vsc` assina apenas arquivos de resultado; o
log registra o nome de cada pacote verificado e "SUCESSO", nao o hash. Nenhum
arquivo publico liga o programa executado na urna a lista lacrada; a ligacao
so existe por amostragem em cerimonia, com relatorio nao publicado. Enquanto
isso nao mudar, o teto do ecossistema e B. (Afirmacao a confirmar com amostra
de logs `.logjez` do 2o turno de 2026.)

## Caminho para A

1. Pedido LAI ao TSE: relatorios das cerimonias de verificacao por amostragem
   e especificacao do algoritmo de assinatura de software.
2. Reproduzir o build de um modulo a partir do codigo-fonte de fiscalizacao
   (`SOURCE_DATE_EPOCH`, `diffoscope`) e comparar com o hash da lista oficial.
3. Reproduziu: A, com data provada por TSA/Rekor.
4. Nao reproduziu: divergencia quantificada e documentada (classe B com
   achado registrado).

## Referencias das tecnicas

- RFC 3161 e limite do genTime: https://thehopiumlab.com/whiteboard/what-does-an-rfc-3161-timestamp-prove
- Rekor v2 dependente de TSA externa: https://www.stephane-robert.info/en/docs/devsecops/supply-chain/sigstore/
- Build deterministico: https://nhimg.org/reproducible-builds-guide
- diffoscope: https://diffoscope.org/
