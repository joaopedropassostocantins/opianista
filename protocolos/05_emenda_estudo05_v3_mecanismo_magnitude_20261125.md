# EMENDA 05 — ESTUDO 05: MECANISMO, MAGNITUDE E FAMÍLIAS DE FATOR EXTERNO

Emenda ao pré-registro 03 e à emenda 04 do Estudo 05, que permanecem inalterados nos itens não tratados aqui. Esta emenda é registrada antes de qualquer contagem de colisão. No momento do registro, o censo do 2º turno de 2026 estava em andamento e nenhum arquivo de colisões existia em disco. O código congelado está em `estudos/05_colisao_titulo_mesario/registro/HASHES_CODIGO_v3.txt`.

## 1 ESCOPO

Inalterado em relação à emenda 04:
- contagem só no 2º turno de 2026 (25/10/2026), em censo;
- linhas de 04/10 descartadas pela data;
- casos do 1º turno apenas como referência descritiva;
- Porto Seguro (BA)–Casa Nova (BA) marcado como alvo nominal;
- comparação com o 2º turno de 2022.

2018 continua indisponível. As URLs testadas, os códigos HTTP e a data e hora de cada verificação estão em `estudos/05_colisao_titulo_mesario/registro/verificacao_2018.md` (verificação de 2026-11-25, 02:10 UTC):

| URL | Resposta |
|---|---|
| pacotes `eleicoes2018/arqurnatot/*_2t_AC.zip`, `*_2t_SP.zip`, `*_1t_AC.zip` | HTTP 404 |
| diretório `eleicoes2018/arqurnatot/` | HTTP 403 |
| diretório `eleicoes2018/logsurna/` | HTTP 404 |
| portal de resultados, `ele2018/arquivo-urna/` | HTTP 404 |
| catálogo de dados abertos | 0 recursos de log de 2018 |

Um vigia diário verifica a republicação até a diplomação, prevista para 12/12/2026. Se os pacotes forem republicados, eles são incorporados com o mesmo pipeline (`download_historico.py quadro 2018` e `censo.py 2018 2`).

## 2 RECONCILIAÇÃO DO DENOMINADOR

O catálogo do 2º turno tem 517.179 seções:
- 499.248 principais, que são os 499.248 citados para o 1º turno;
- 17.931 agregadas, sem urna nem arquivo próprio (aux.json com HTTP 404; 7.066 de 7.066 conferidas até o registro);
- 41 das principais sem data de totalização no catálogo, com linha própria como candidatas a "não instalada";
- o exterior (ZZ, 2.715 seções) com linha própria;
- nenhum log de seção de apuração (logSA) na amostra de 58 aux.json.

N = registros de presença de mesário nas seções principais com log lido, filtrados pela data do turno e pela fase Oficial. A tabela final de reconciliação sai em `registro/reconciliacao_N_2t2026.md` ao fim do censo.

## 3 FASE 0 (ATUALIZADA)

As strings estão documentadas em `registro/fase0_2t_vocabulario.md` com exemplo de linha, arquivo e posição, e com os títulos mascarados:
- registro de presença;
- digitação do título (`Pedido de leitura da biometria do mesário <T>`);
- "não é eleitor da seção";
- "já registrado";
- título inválido;
- biometria coincidente e não coincidente;
- habilitação de eleitor;
- partida do sistema (`Início das operações do logd`);
- zerésima;
- voto computado;
- urna pronta;
- contingência.

A partida normal da manhã não é reinício: 28 de 30 urnas tiveram uma única partida no dia. A ordem do dia é zerésima, registro de mesários, urna pronta.

## 4 CLASSIFICAÇÃO DE BLOQUEIOS (PRECEDÊNCIA CONGELADA)

1. `bloqueio_pos_reinicio`: partida posterior à primeira do dia, até 30 min antes do bloqueio, sem voto no meio.
2. `erro_digitacao_para_outro_mesario_da_secao`: há na seção um título registrado a um erro de distância do título bloqueado. É a única classe que alimenta a validação cruzada.
3. `redigitacao_imediata`: mesmo título, mesma urna, até 10 min, sem voto no meio.
4. `redigitacao_ciclo_posterior`: o restante, inclusive o re-registro da mesa num ciclo posterior.

A evidência de vizinho prevalece sobre o tempo. A regra temporal pura fica na coluna paralela `classe_regra_temporal`, sem alimentar a validação.

A janela de 30 min é parâmetro de sensibilidade, rodado também com 15 e 60 min. Na amostra cacheada antes do registro, a classe 2 não se moveu (4 casos nas três janelas). O teste de estabilidade é reportado no censo completo.

**Não há teto para a classe 4.** Ela fica fora da razão e é descrita como resíduo, com distribuição por momento. O padrão "bloqueio antes do primeiro voto do dia, de 15 a 60 min após o registro, sem vizinho" sai como linha própria (`padrao_pre_primeiro_voto_15_60min`). Na amostra, 93% da classe 4 é re-registro, num ciclo "durante a votação", de títulos registrados no ciclo "antes".

## 5 p1 E D

- p1 por caminho (UF, corpo, DV, transposição, omissão e outros), medido por quase-duplicados, com taxa por seção e por UF. Contagens auxiliares com viés declarado, como na emenda 04.
- Leave-one-out nos dois sentidos:
  - D é medido sem os títulos em colisão e sem os títulos usados como quase-duplicados em p1;
  - p1 é medido sem os pares que contêm título em colisão.
- D por UF e por zona.
- A etapa de parâmetros tem acesso ao censo completo. As exclusões do LOO (números de títulos, registros e pares) são gravadas em `parametros_nulo.json` e publicadas com o hash desse arquivo.

## 6 MODELO NULO E SENSIBILIDADE

O modelo é o da emenda 04 (Vias 1, 2 e 3), com sensibilidade em:
- p1 × 0,5 e × 2;
- D × 0,5 e × 1,5;
- janela de reinício de 15, 30 e 60 min.

## 7 HORÁRIOS DO REGISTRO

O histograma de 15 em 15 minutos separa o primeiro registro da mesa dos posteriores (`horarios_registro.csv`).

Se mais de 5% dos registros ocorrerem após as 9h, as faixas de intervalo são estratificadas por período, e o nulo é rodado por estrato (`tabela_faixas_por_periodo.csv`). Os períodos são manhã (antes das 12h), tarde (12h a 17h) e após as 17h, e o período do par é o do registro mais tardio.

## 8 FAIXA A (MENOS DE 1 KM): VEREDITO PRÓPRIO, PROVA CASO A CASO

Cada caso da faixa A é "não explicado" até prova em contrário. A prova pode ser de dois tipos:

- **Explicado por digitação:** há quase-duplicado do título em uma das pontas.
- **Explicado por substituição:** duas condições juntas.
  1. Na ponta de destino (o registro mais tardio do par), o registro ocorreu num ciclo "durante a votação", ou a mesa de destino abriu com menos de 3 mesários no ciclo "antes".
  2. O intervalo é compatível com deslocamento a pé: delta ≥ max(60 s, distância em metros / 1,4 m/s).

A proporção de "não explicado" na faixa A é reportada com IC exato. Ela é achado próprio e não se dilui em B e C.

## 9 CRUZAMENTO COM O MOVIMENTO DE VOTOS (COMPLEMENTAR)

Dados: `votos.py`, com o boletim de urna web do 1º e do 2º turno de 2026.
- **Desfecho:** delta = margem no 2º turno − margem no 1º, com margem = (votos A − votos B) / comparecimento para os dois candidatos do 2º turno presidencial. As variações de cada candidato também são reportadas.
- **Controle:** as demais seções do mesmo local de votação, sem colisão.
- **Outlier:** |z| > 3 em relação às vizinhas, com no mínimo 3 vizinhas.
- **Leitura congelada:** o cruzamento não confirma digitação nem prova manipulação. Diz apenas se as seções com colisão se comportam como as vizinhas. Ele não vê alteração que atinja os dois turnos por igual, nem alteração só no 2º turno que não deixe rastro relativo ao 1º.
- **Saída:** `votos_outlier.csv`, que também grava urna efetivada e códigos de carga e de flashcard do 2º turno de cada seção envolvida.

## 10 TESTE DE CASO E FAMÍLIAS

Campos por colisão (`colisoes_caso.csv`):
- UF, zona, seção, horários, delta, distância e faixa;
- velocidade exigida para uma mesma pessoa estar nas duas pontas;
- biometria (resumo do censo e log bruto) e mensagem de digitação, em cada ponta;
- modelo e versão da urna nas duas pontas;
- quase-duplicado e distância de edição mínima a outro título da seção;
- lacuna superior a 300 s no log imediatamente antes do registro;
- verificação de assinatura do dia (conferida ou divergente);
- outros títulos compartilhados entre as duas seções;
- mesma carga ou flashcard;
- voto atípico;
- prova da faixa A;
- famílias compatíveis, famílias eliminadas e família mais estreita compatível.

Famílias, da mais estreita para a mais ampla. Marca-se a primeira compatível; se nenhuma for compatível, o caso fica "não classificado". Nunca se usa a F6 por default.

| Família | Eliminada quando |
|---|---|
| F0 erro de digitação | não há quase-duplicado em nenhuma ponta |
| F1 nulo mal especificado | a classe 2 está dentro do previsto e há excesso agregado (todos os casos) |
| F2 procedimento não documentado | a velocidade exigida passa de 120 km/h |
| F3 erro sistemático de software | há mensagem de digitação nas duas pontas, ou modelo/versão diferem |
| F4 carga ou mídia compartilhada | nenhum outro título compartilhado e carga/flashcard diferentes |
| F5 digitação intencional | há quase-duplicado |
| F6 registro fictício | não há nenhum sinal positivo: falta de mensagem de digitação numa ponta, assinatura divergente, lacuna > 300 s ou voto atípico |

Regras validadas em `tests/teste_familias.py` (12 de 12). Por exemplo, um caso a 800 km em 22 s, sem quase-duplicado, com digitação nas duas pontas e sem carga comum, tem F2, F3 e F4 eliminadas e F5 como a mais estreita compatível. O mesmo caso com quase-duplicado fica em F0.

## 11 ESTATÍSTICA

- Razão O/E com IC exato, por faixa e no total.
- Dispersão e concentração por seção, por local de votação e por UF.
- Teste individual por UF só onde o esperado passa de 3. As demais UFs são agregadas em estratos de eleitorado: G ≥ 10 milhões, M de 4 a 10 milhões, P < 4 milhões.
- Previsão do mecanismo: correlação de Spearman entre D por UF e colisões por registro.
- Mesmo pipeline no 2º turno de 2022.

## 12 REGRA DE DECISÃO (substitui a seção 10 da emenda 04)

São dois vereditos, implementados em `simulacao.py` e `teste_caso.py`.

**Veredito de mecanismo**, por faixa:

| Situação | Veredito |
|---|---|
| Classe 2 dentro do previsto e colisões dentro do IC | o acidente explica o volume |
| Classe 2 dentro do previsto e colisões acima do limite superior | o mecanismo existe, mas não chega: excesso |
| Classe 2 fora do previsto | o modelo de digitação está rejeitado e não pode ser usado para dizer "é acidente" |

"Dentro do previsto" significa dentro da faixa formada pelos intervalos de 95% dos cenários p1 × 0,5, central, D × 1,5 e p1 × 2.

**Veredito de magnitude**, sempre emitido:
- razão entre o observado e o limite superior do nulo, por faixa;
- com o modelo rejeitado, essa razão é um piso;
- famílias por caso e no agregado.

**Regras adicionais:**
- A faixa A tem veredito próprio (seção 8).
- Concentração tem achado próprio, que não é absorvido pelo veredito de volume. Ela é declarada se as seções envolvidas forem menos de 5% e o máximo por seção tiver P_sim < 0,05; ou se o mesmo valer para os locais de votação; ou se o qui-quadrado por UF tiver p < 0,05.
- A ausência de excesso abre o relatório.
- Se a validação reprovar, o relatório não se cala: emite magnitude e famílias.

## 13 CONGELAMENTO (ORDEM EXATA)

1. **Código:** hash em `HASHES_CODIGO_v3.txt`, no commit desta emenda.
2. **Censo:** termina.
3. **Parâmetros:** `python src/simulacao.py 2026 --somente-parametros` (com LOO) gera `parametros_nulo.json`.
4. **Commit dos parâmetros:** o SHA-256 desse arquivo vai para `registro/parametros_2t2026.sha256`, em commit próprio. O protocolo registra que a etapa de parâmetros teve acesso ao censo completo e lista as exclusões do LOO.
5. **Teste completo:** só então roda o `simulacao.py` completo, que escreve `colisoes.csv` e `bloqueios.csv`. O código recusa escrever colisões sem esse arquivo de hash (trava). Seguem o cache das seções com colisão, o `votos.py`, o `teste_caso.py` e a pseudonimização.

O cache dos brutos das seções com bloqueio e quase-duplicado pode ser montado antes da etapa 4. O das seções com colisão, só depois.
