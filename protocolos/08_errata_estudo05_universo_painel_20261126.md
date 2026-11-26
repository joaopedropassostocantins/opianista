# ERRATA E06-1 — ESTUDO 05: UNIVERSO DO PAINEL LOCAL

Errata à emenda 06 (seção 4, "Universo"). Registrada em 26/11/2026, depois da geração do arquivo de colisões e da leitura de seus totais agregados. Esta errata é posterior a essa leitura e diz respeito só ao acesso aos dados; ela não altera nenhuma regra de decisão, métrica, limiar ou veredito.

## O que a emenda 06 dizia

O painel local cobriria todas as seções dos municípios em que houve colisão.

## Por que não é executável

Os 917 municípios com colisão têm 282.996 seções com log (57% do país). Baixar esses logs custaria cerca de 28 GB de disco e quase duas horas de download. Restringindo às zonas com colisão, ainda seriam 227.637 seções.

## O que passa a valer

Universo do painel = (a) todas as seções dos locais de votação em que há colisão, mais (b) para os locais com menos de 5 seções, todas as seções da mesma zona. São 78.574 seções (2.786 locais, 572 deles com menos de 5 seções). Isso cobre exatamente as vizinhas que a regra da emenda 06 manda usar (mesmo local ou, com menos de 5 seções, mesma zona e mesmo modelo de urna).

Consequência para o teste conjunto: a permutação dos rótulos de colisão continua dentro de município × modelo de urna, mas só entre as seções do universo acima. As seções fora do universo não entram no controle. O universo é escolhido a partir das colisões, o que o torna mais próximo das seções com colisão do que uma amostra aleatória do município; a taxa de anomalia das controles é, portanto, estimada em seções vizinhas e não no município inteiro. A leitura do teste conjunto fica restrita a essa comparação local.

Código: `src/cache_brutos.py`, critério `painel`. Os demais arquivos do código congelado não mudam.
