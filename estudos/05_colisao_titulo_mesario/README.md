# Estudo 05 - Colisao de titulo no registro de presenca de mesario

## Escopo vigente

Emenda 05 (`protocolos/05_emenda_estudo05_v3_mecanismo_magnitude_20261125.md`): dois vereditos (mecanismo e
magnitude), familias de fator externo F0-F6 por caso, faixa A com prova caso a caso, cruzamento com o
movimento de votos e trava que impede escrever colisoes antes do commit dos parametros.

### Emenda 04

Emenda 04 (`protocolos/04_emenda_estudo05_2t_20261125.md`): somente o 2o turno de 2026 (25/10/2026), censo
de todas as secoes, com comparacao no 2o turno de 2022. 2018 indisponivel no TSE. Alvo nominal:
Porto Seguro (BA) - Casa Nova (BA).

## Pergunta

O mesmo numero de titulo aparece no registro de presenca de mesario em duas
secoes diferentes, no mesmo turno, mais do que um modelo de erro de digitacao
explica? Se aparece, o excesso esta no volume ou na concentracao?

O estudo entrega observado, esperado, razao, intervalo de confianca e veredito
pela regra pre-registrada. Nao conclui fraude nem lisura; conclui excesso
estatistico, ou ausencia dele.

## Protocolo

`protocolos/03_preregistro_estudo05_colisao_titulo_20261125.md` (registrado em
`protocolos/REGISTRO.md`). Correcoes feitas ao protocolo encomendado, com a
evidencia de cada uma: `docs/correcoes_da_logica.md`.

## Mecanismo nulo

1. O mesario digita errado.
2. O numero errado passa na validacao estrutural da urna (DV/UF), que nao
   consulta lista.
3. O numero coincide com o titulo de outro mesario registrado em outra secao.

O rastro medido do erro aceito e o quase-duplicado na mesma secao: dois titulos
registrados na mesma secao a um unico erro de distancia.

## Estrutura

```
src/parsing.py               leitura do log (.jez 2026 / .logjez 2022) e extracao dos registros de mesario
src/censo.py                 coleta censitaria retomavel, com SHA-256 de cada arquivo original
src/densidade.py             caminhos de erro, p1 por caminho (quase-duplicados), densidade local D
src/simulacao.py             colisoes, bloqueios, teste de caso, nulo (vias 1, 2 e 3), validacao, veredito
src/fase0.py                 Fase 0 do 2o turno (vocabulario com exemplo de linha e posicao)
src/cache_brutos.py          cache seletivo dos logs originais (bloqueios, quase-dup, colisoes), com SHA-256
src/teste_caso.py            teste de caso de cada colisao, prova da faixa A e familias F0-F6
src/votos.py                 cruzamento com o movimento de votos (outlier dentro do local de votacao)
src/pseudonimizar.py         saidas publicaveis (titulo -> HMAC; chave fora do Git)
src/geo.py                   coordenadas e eleitorado por secao
src/download_historico.py    quadro de secoes de 2022/2024 a partir dos pacotes por UF
src/download.py, amostragem.py, extrair.py, erros.py, poder.py, zip_remoto.py   Fase 0 e piloto
tests/teste_sintetico.py     colisoes plantadas; deve imprimir 4 OK
registro/                    Fase 0, piloto, poder, hashes do codigo congelado, manifesto
docs/correcoes_da_logica.md  o que mudou em relacao ao protocolo encomendado e por que
docs/probabilidade_por_uf.md probabilidade por UF de o erro virar colisao (exploratorio, parametros medidos)
resultados/                  saidas pseudonimizadas e relatorio (apos o censo)
```

## Reproducao

```bash
pip install -r estudos/05_colisao_titulo_mesario/requirements.txt
cd estudos/05_colisao_titulo_mesario
python src/download.py catalogo
# auxiliares em data/raw/aux/: eleitorado_local_votacao_2026.zip e _2022.zip (dadosabertos.tse.jus.br)
python src/geo.py 2026 && python src/geo.py 2022
python src/download_historico.py quadro 2022
for s in 0 1 2 3 4 5; do python src/censo.py 2026 2 $s 6 & done; wait   # idem: python src/censo.py 2022 2 ...
python tests/teste_sintetico.py
python src/cache_brutos.py 2026 2 bloqueios ; python src/simulacao.py 2026 --somente-parametros
python src/cache_brutos.py 2026 2 quase_dup
sha256sum data/outputs/2026_t2/parametros_nulo.json > registro/parametros_2t2026.sha256   # commit proprio
python src/simulacao.py 2026 ; python src/cache_brutos.py 2026 2 colisoes
python src/votos.py 2026 ; python src/teste_caso.py 2026
python tests/teste_familias.py        # deve imprimir 12 OK
python src/pseudonimizar.py data/outputs/2026_t2 resultados/2026_t2
```

Tudo o que e baixado ou gerado com titulo em claro fica em `data/` e
`outputs/`, fora do Git.

## Status

| Etapa | Situacao |
|-------|----------|
| Fase 0 (vocabulario, regra de validacao) | Concluida |
| Piloto de parametros (2.000 secoes, sem colisoes) | Concluido |
| Pre-registro e congelamento do codigo | Concluido (2026-11-25) |
| Censo 2026 1T e 2T (100% das secoes; 2T aprovado pelo proponente em 25/11/2026, decisao D4) | Em execucao |
| Censo 2022 1T e 2T (linha de base) | Em execucao |
| 2018 | Nao executavel: pacotes nao publicados pelo TSE |
| Simulacao, teste de caso e relatorio | Pendente do censo |
