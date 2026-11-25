# EMENDA 06 — ESTUDO 05: A PORTA, O PAINEL LOCAL E O RÓTULO ENTRE ACIDENTE E INTENÇÃO

Emenda às emendas 04 e 05 do Estudo 05, que permanecem inalteradas nos itens não tratados aqui. O escopo é o mesmo: 2º turno de 2026, 25/10/2026.

Esta emenda é publicada e commitada antes do cálculo de parâmetros. Quando isso acontece, não existe arquivo de colisões em disco, e a trava do `simulacao.py` impede escrevê-lo sem o commit dos parâmetros. Os hashes do código estão em `estudos/05_colisao_titulo_mesario/registro/HASHES_CODIGO_v4.txt`.

## 1 AVISO OBRIGATÓRIO NA PRIMEIRA PÁGINA DO RELATÓRIO

A primeira página do relatório deve trazer o texto: "Não ter repetição de número de título não inocenta as demais seções do país. A busca por seções atípicas sem colisão é a pergunta do Estudo 03 (mesário pianista), com protocolo próprio."

## 2 O QUE ESTAVA ERRADO NA EMENDA 05 E COMO FICA

1. **F5 por ausência de quase-duplicado.** Sem título pretendido conhecido, F0 e F5 permanecem compatíveis, e o rótulo do caso passa a ser "não classificado entre F0 e F5".
   - F0 só cai quando o título pretendido é conhecido e a distância de edição até o número gravado é grande. O único título pretendido observável é o quase-duplicado, a segunda digitação correta, que está a distância 1. Logo F0 não cai por ausência de quase-duplicado.
   - Cada caso recebe a razão de verossimilhança contra o acidente, 1/(1 − d), em que d é a probabilidade de o erro ficar visível, medida nos parâmetros: cerca de 0,81, ou seja, cerca de 5 para 1.
2. **Separação F0/F5, agregada.** Teste binomial unilateral da fração de colisões com quase-duplicado contra d.
   - Fração muito abaixo de d (p < 0,05): o conjunto não tem a forma do erro de digitação.
   - Se o total de colisões couber no intervalo do nulo, F5 não é necessária.
   - Se passar do intervalo, o excesso pede outra família, e o caso individual não herda F5 por isso.
3. **Faixa A.** O quase-duplicado não tira o caso de "não explicado". O estado é `substituicao_compativel` (critérios da emenda 05, seção 8) ou `nao_explicado`. O campo `indicio_de_digitacao` registra se há quase-duplicado.
4. **F3.** Mensagem de digitação nas duas pontas elimina F3 e só F3. A regra de modelo ou versão diferentes entre as pontas continua.
5. **F4.** O flashcard deixa de contar. Medição no Acre, 2º turno, 2.270 seções:

   | Campo | Valores distintos | Seções que compartilham |
   |---|---|---|
   | Número da urna efetivada | 2.270 | 0 |
   | Código de carga 1 | 2.270 | 0 |
   | Código de carga 2 | 2.267 | 6 |
   | Flashcard | 88 | 2.270, em grupos de até 34 |

   O flashcard é compartilhado por desenho. O código de carga 1 e a urna efetivada são únicos por urna. F4 é compatível se o código de carga 1 ou a urna efetivada coincidirem entre as pontas, ou se 2 ou mais outros títulos se repetirem juntos.
6. **F6.** Compatível só com sinal positivo:
   - uma ponta sem mensagem de digitação e sem leitura de biometria;
   - assinatura divergente;
   - lacuna superior a 300 s antes do registro;
   - seção G1 no painel local.

   Nunca por default.
7. **Biometria da mesma pessoa nas duas pontas.** Não é observável, porque a urna só compara com o cadastro da própria seção. A regra não é aplicada.

## 3 A PORTA

A definição larga ("não é eleitor da seção" ou biometria não coincidente) cobre 74,7% das presenças de mesário. No censo parcial do 2º turno de 2026 (1.047.140 presenças), 38,9% das seções têm 100% das presenças nessa condição. Isso descreve a prática de designar mesários de outras seções e não é critério.

A porta larga entra só como descrição. No painel entra a **porta estreita**: fração dos mesários que são eleitores da seção e cuja biometria não coincidiu. Ela é comparada com as vizinhas e com a taxa do 2º turno de 2022 na mesma UF e no mesmo modelo de urna. Sozinha não classifica seção; junto com outra anomalia, pesa (seção 4).

## 4 PAINEL LOCAL (`src/painel.py`)

Obrigatório em toda seção com colisão. Nenhuma é dispensada pelo veredito nacional.

**Universo:** todas as seções dos municípios com colisão. Os logs vêm do cache seletivo, critério `painel`, que só pode ser montado depois do commit dos parâmetros. Não há reprocessamento nacional.

**Vizinhas:** demais seções do mesmo local de votação, sem colisão. Se o local tiver menos de 5 seções, a mesma zona e o mesmo modelo de urna, sem colisão.

**Métricas:**
1. variação da abstenção, do 1º para o 2º turno (boletim de urna);
2. taxa de habilitação sem biometria;
3. taxa de habilitação autorizada por mesário;
4. taxa de "não é eleitor da seção";
5. movimento de cada finalista;
6. taxa de liberação manual;
7. rajada: votos nos 15 min após o registro contestado, contra as janelas de 15 min da própria seção (só nas seções com colisão).

Strings usadas pelas métricas 2, 3 e 6, verificadas na Fase 0: `Eleitor foi habilitado`, `Tipo de habilitação do eleitor [biométrica]`, `Mesário <T> habilitou o eleitor`, `Solicitação de dado pessoal do eleitor para habilitação manual`, `O voto do eleitor foi computado`.

**Outlier:** |z| > 3. O z é robusto: (x − mediana das vizinhas) / max(1,4826 × MAD, piso). Para taxas, o piso é binomial, sqrt(p0(1 − p0)/n). Para variações, é o desvio-padrão das vizinhas.

**Seção anômala:**
- Para o teste conjunto: 2 ou mais outliers entre as métricas 1 a 6, ou 1 outlier e a porta estreita também outlier. A métrica 7 fica fora, porque não existe em seção sem colisão.
- Para o veredito de local: a métrica 7 também conta.

## 5 TESTE CONJUNTO

Proporção de seções com colisão que são anômalas, contra permutação dos rótulos de colisão dentro de município × modelo de urna. São 10.000 réplicas, com semente 20261025. A taxa esperada é a das seções sem colisão nos mesmos estratos.

| Total de colisões | Proporção anômala | Leitura |
|---|---|---|
| Dentro do intervalo | Dentro da permutação | O acidente ainda chega |
| Dentro do intervalo | Acima da permutação (p < 0,05) | O volume não salva os locais |
| Acima do intervalo | — | Excesso de volume; o painel diz se o excesso está nos locais anômalos |

## 6 VARREDURA SEM COLISÃO (G3)

Fica fora deste estudo. Ela exigiria reler cerca de 990 mil logs (2026 e 2022) e é a pergunta reservada pelo Estudo 03, que tem protocolo próprio. Fazer aqui criaria dois protocolos para a mesma suspeita, que é o risco já listado no `PLANEJAMENTO.md`. O relatório usa só G1 (colisão e anômala) e G2 (colisão e normal), e traz o aviso da seção 1.

## 7 VEREDITOS

| Veredito | Regra |
|---|---|
| Nacional, de volume | Observado contra o intervalo do nulo de colisões. Não absolve seção. |
| De mecanismo | Continua condicionado à classe 2 (emenda 05). |
| De local | Para toda seção com colisão. G1: "acidente não chega neste local", com a lista do que ficou compatível. G2: "compatível com acidente, desde que o total nacional caiba no intervalo". Sem família por default. |
| De magnitude | A razão observado/limite superior continua e é apresentada ao lado da razão do teste conjunto. As duas não se substituem. |

## 8 N E EXTERIOR

O commit de parâmetros usa o N reconciliado: registros nas seções principais com log, não os 517.179 do catálogo.
- Seções de apuração: nenhuma encontrada.
- Não instaladas: 41, com linha própria.
- Exterior: fica no numerador e no denominador, com linha própria. Tirá-lo só de um dos dois entortaria a razão.

## 9 ORDEM DE EXECUÇÃO (substitui a seção 13 da emenda 05)

1. Censo concluído.
2. `simulacao.py --somente-parametros`, que inclui d e o N reconciliado.
3. Commit do hash de `parametros_nulo.json`, com esta emenda já no hash do código.
4. `simulacao.py` completo.
5. Cache dos critérios `colisoes` e `painel`.
6. `votos.py`.
7. `painel.py`.
8. `teste_caso.py`.
9. Pseudonimização.
10. Relatório.
