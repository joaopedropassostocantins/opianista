# EMENDA 07 — ESTUDO 05: CAMINHO DE OMISSÃO, DIVISÃO DOS QUASE-DUPLICADOS E LEAVE-ONE-OUT

Emenda às emendas 04, 05 e 06 do Estudo 05. Escopo inalterado: 2º turno de 2026, 25/10/2026, censo. Registrada em 26/11/2026, antes do cálculo oficial de parâmetros e de qualquer arquivo de colisões. Aprovada pelo proponente em 26/11/2026 ("Sim", em resposta à proposta registrada na conversa). Código congelado em `estudos/05_colisao_titulo_mesario/registro/HASHES_CODIGO_v5.txt`.

## 1 CORREÇÕES DE ERRO ENCONTRADO ANTES DO CÁLCULO OFICIAL

- **Horário.** A conversão para segundos dividia por 10⁹ e, com pandas 3 (datetime64 em microssegundos), encolhia todos os horários e intervalos 1.000 vezes. Corrigido e coberto por teste (intervalo de colisão plantada: 3.000 s, faixa 30 min–4 h). Não afetou nenhum arquivo de colisões, que ainda não existe.

## 2 CAMINHO DE OMISSÃO

O caminho "omissão" (um dígito apagado, com o número completado por um dígito no fim ou por um zero à esquerda) é caminho real de erro de digitação.

Evidência: num controle de mesmo local, a taxa de pares de omissão é 1.021 por milhão de pares dentro da mesma seção, contra 0,5 por milhão entre seções diferentes do mesmo local de votação (razão de cerca de 2.000). Substituição no corpo: 162 contra 7,3 (razão 22). Transposição: 25 contra 0,9 (razão 29). A variante dominante é o zero à esquerda (1.457 de 1.476 pares de omissão examinados em amostra).

O caminho entra com seu peso medido, sem trava. Os pesos e p1 por caminho são os da seção 5.

## 3 DIVISÃO DOS QUASE-DUPLICADOS

Para cada par de títulos distintos registrados na mesma seção a um único erro de distância:

- **erro aceito:** um dos dois títulos aparece uma única vez na seção, e os conjuntos de ciclos (antes, durante, após) em que cada título aparece são disjuntos. O número digitado errado foi registrado num ciclo e o correto no outro.
- **vizinho legítimo:** qualquer outro par. São mesários com títulos vizinhos registrados nos mesmos ciclos.

Medição no censo do 2º turno (amostra de 2 de 6 arquivos de registro): 1.239 pares, dos quais 1.169 erros aceitos (94,4%) e 70 vizinhos legítimos (5,6%).

Regras:
- p1 usa só erros aceitos.
- O indício de digitação no teste de caso usa só erros aceitos.
- Vizinhos legítimos saem de p1 e do indício, mas continuam em D.

## 4 LEAVE-ONE-OUT

- **D:** exclui os títulos em colisão e os dois membros de cada erro aceito. Não se sabe qual dos dois é o número errado, e o errado não é alvo legítimo. Os pares de vizinhos legítimos permanecem em D, o que restaura a previsão de bloqueios de classe 2 que a emenda 05 tinha zerado.
- **p1:** exclui pares de erro aceito em que algum título está em colisão.
- **d (visibilidade):** fração de ocorrências (título, seção) fora dos erros aceitos que foram registradas duas ou mais vezes.
- O modo `--sem-loo` mantém a filtragem por erro aceito e tira só a exclusão por colisão.

## 5 PARÂMETROS OFICIAIS

Cálculo com 10.000 réplicas, semente 20261025, N reconciliado (499.178 seções com log, 3.799.442 registros de presença antes da exclusão de relógios inconsistentes; o N exato fica em `parametros_nulo.json`). Os valores do ensaio sobre dados parciais não valem: o ensaio usou a regra antes desta emenda.

Antes do cálculo oficial, o cache dos brutos das seções com bloqueio e de quase-duplicados é verificado: cada arquivo conferido contra o SHA-256 do censo (74.796 arquivos, 0 divergentes).

## 6 ORDEM DE CONGELAMENTO (substitui a da emenda 06 no que se refere ao hash)

1. Esta emenda e `HASHES_CODIGO_v5.txt` commitados. Nenhum arquivo de colisões existe em disco.
2. `simulacao.py 2026 --somente-parametros` gera `parametros_nulo.json`.
3. Commit do SHA-256 de `parametros_nulo.json` em `registro/parametros_2t2026.sha256`.
4. Só depois: cache dos critérios `colisoes` e `painel`, `simulacao.py` completo, `votos.py`, `painel.py`, `teste_caso.py`, pseudonimização e relatório.

A coleta de 2022 segue pausada para liberar memória durante o cálculo oficial e retoma depois, como linha de base.

## 7 O QUE NÃO MUDA

Regra de decisão, dois vereditos (mecanismo condicionado à classe 2, magnitude sempre), rótulo "não classificado entre F0 e F5" sem quase-duplicado, painel local obrigatório, G3 fora deste estudo (Estudo 03), exterior no numerador e no denominador.
