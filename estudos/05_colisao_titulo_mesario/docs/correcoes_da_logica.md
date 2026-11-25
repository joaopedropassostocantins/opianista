# CORREÇÕES E MELHORIAS DA LÓGICA DO PROTOCOLO SOLICITADO

Este documento registra, item por item, onde o protocolo encomendado para o Estudo 05 foi seguido, corrigido ou complementado, sempre com a evidência empírica que motivou a mudança. As medições vêm da Fase 0 (30 seções de 5 UFs) e do piloto (2.000 seções do 1º turno de 2026, sorteadas com a semente 20261004), sem cálculo de colisões.

## 1 MENSAGEM DE BIOMETRIA NÃO COINCIDENTE NÃO É RASTRO DE ERRO DE DIGITAÇÃO

Proposta original: contar as mensagens de biometria que não coincidem com nenhum mesário cadastrado como numerador de p1.

O que o log mostra (sequências de mensagens por tentativa de registro, 3.000 logs do 1º turno de 2026):

| Sequência | n |
|---|---|
| Pedido de biometria > `não é eleitor da seção` > registrado | 14.094 |
| Pedido > `Realizada a conferência` > `é eleitor da seção` > registrado | 5.482 |
| `Digitado título inválido para o registro de mesário` | 4.282 |
| Pedido > `Digital capturada não corresponde` > `é eleitor da seção` > registrado | 1.984 |
| Pedido sem desfecho no mesmo ciclo | 1.446 |
| Pedido > `é eleitor da seção` > registrado (sem conferência) | 241 |

Conclusões:

1. A urna só confere a digital quando o título digitado pertence a eleitor da própria seção. Numa colisão entre seções, o número errado é, por definição, título de mesário de outra seção e, em regra, não é eleitor da seção em que foi digitado. A mensagem de não coincidência não pode existir na ponta em que o erro ocorreu.
2. A mensagem `Digital capturada não corresponde` ocorre em 26% das conferências, com scores baixos (0 a 17), e o registro prossegue. Ela mede principalmente falha de leitura da digital, não título errado.
3. As mensagens de não coincidência no momento da habilitação de eleitor (`Biometria coletada não é do mesário <T>`) pertencem a outro processo, em que o mesário autentica a liberação de um eleitor, e também não medem erro de digitação no registro.

Correção adotada: o rastro direto de "digitou um título que não é o dele e foi aceito" é o quase-duplicado na mesma seção. Cada mesário é registrado em regra duas vezes (antes e após a votação). Quando uma das digitações passa no dígito verificador com um erro, ficam registrados, na mesma seção, dois títulos a uma única operação de erro de distância. Esse par é observável, contável e classificável por tipo e posição.

## 2 TAXA DE APROVAÇÃO POR POSIÇÃO: O PREFIXO DE UF NÃO APROVA ~27%

Proposta original: substituição no prefixo de UF com aprovação de ~27%; corpo e DV com ~1%.

Medição (enumeração exaustiva de todos os vizinhos de cada título registrado no piloto, aplicando o algoritmo público do DV):

| Tipo de erro | Aprovação no DV (p2) |
|---|---|
| Substituição no corpo sequencial (dígitos 1 a 8) | 1,88% |
| Substituição no prefixo de UF (dígitos 9 e 10) | 0,65% |
| Substituição no dígito verificador (dígitos 11 e 12) | 0,00% |
| Transposição adjacente | 1,13% |
| Transposição com salto | 1,28% |
| Erro gêmeo (aa → bb) | 10,5% |

O prefixo de UF entra no cálculo do segundo DV, com peso 7 ou 8 módulo 11; uma substituição nele altera o resto e só passa nas colisões de resto 0/10. A cifra de ~27% corresponderia a aceitar qualquer prefixo entre 01 e 28 sem recalcular o DV, o que não é o algoritmo. A substituição isolada no DV nunca passa, porque o DV correto é único. A omissão de dígito não é representável: o campo exige 12 dígitos e o número rejeitado não é gravado.

## 3 p1 MEDIDO, NÃO SUPOSTO, E A DIVERGÊNCIA COM AS TENTATIVAS INVÁLIDAS

As tentativas rejeitadas (`Digitado título inválido para o registro de mesário`) somam 15,2% das tentativas no piloto. Se todas fossem erros de um dígito num número de 12 dígitos, os títulos válidos errados seriam 15,2% × p2 ≈ 0,2% dos registros, ou cerca de 38 no piloto. Foram observados 2 quase-duplicados. A maior parte das rejeições não é erro de um dígito, e provavelmente corresponde a entrada incompleta ou confirmação prematura. O protocolo adota o quase-duplicado como medida central e mantém as tentativas inválidas como cenário de limite superior na análise de sensibilidade.

## 4 REGRA DE VALIDAÇÃO DETERMINADA EMPIRICAMENTE

- Nenhum título registrado falha no DV (0 em 14.948 registros do piloto).
- 70% dos títulos registrados vêm marcados `não é eleitor da seção` e são aceitos, logo não há consulta à lista da seção.
- A conferência biométrica é informativa: o registro prossegue com `não corresponde`.
- O número rejeitado não é gravado, de modo que a regra não pode ser auditada pelo lado negativo. A conclusão é a de validação estrutural, compatível com DV/UF.

## 5 SEPARAÇÃO ENTRE MESÁRIO E ELEITOR

O log grava o título em claro apenas no ciclo de registro de mesário. Na habilitação de eleitor, grava somente o tipo de identificador (`Identificador digitado pelo mesário foi: (Título de eleitor)`), sem o número. O confundidor "título digitado para liberar eleitor confundido com título de mesário" fica eliminado por construção.

## 6 TESTE DE CASO REFORMULADO

O critério "colisão sem mensagem de mismatch nas duas pontas é a que merece atenção" classificaria quase toda colisão como suspeita, porque a mensagem quase nunca pode existir (item 1). Classificação adotada, em ordem:

1. excluída por mesma urna ou linha idêntica (contingência ou restart);
2. erro de digitação evidenciado: em uma das pontas há título registrado a um erro de distância do número colidido;
3. mesmo prédio (<1 km), sem anomalia;
4. dono conferido por biometria em uma ponta (eleitor da seção com conferência coincidente);
5. resíduo sem explicação no log, que é o único grupo que o mecanismo não cobre.

## 7 ESCALA: CENSO

O protocolo revisado está correto ao exigir censo. Sob amostragem aleatória de fração f, as colisões esperadas escalam com f², porque as duas pontas precisam ser sorteadas. Com f = 10%, o nulo calibrado cai para menos de 0,1 evento. A primeira versão, que usava amostra, foi descartada sem cálculo de colisões (`registro/obsoleto/` no repositório de origem).

## 8 PODER

Mesmo com censo, o poder para detectar razão 2 (α = 0,05, unilateral) fica em torno de 69% sob a calibração central. O mínimo de 80% não é atingível, o que é declarado na primeira linha do relatório.

## 9 LINHAS DE BASE HISTÓRICAS

- 2022: disponível nos pacotes por UF do CDN do TSE, com as mesmas strings de mesário de 2026. O log do 2º turno de 2022 carrega também as linhas do 1º turno, então o filtro pela data do turno é obrigatório.
- 2018: pacotes não publicados no CDN (HTTP 404), e o portal de resultados não mantém mais `ele2018`. Não executável; 2024 (municipal) pode servir como substituta declarada.

## 10 DESIGNAÇÃO LEGÍTIMA PARA DUAS SEÇÕES

A base pública de convocação de mesários (`convocacao_mesarios_<ano>.zip`) é agregada por zona, sem título nem seção. O cruzamento individual pedido no protocolo não é possível com dados públicos; permanece como ressalva quantificada pelo número de resíduos.

## 11 DENOMINADOR M E A FRAÇÃO q

O protocolo estima q ≈ 1,6% com ~2,5 milhões de mesários. O valor usado é medido: títulos únicos efetivamente registrados no censo, divididos pelo eleitorado da base de locais de votação (158.745.463 em 2026). A Via 2 dispensa M, porque sorteia alvos apenas no multiconjunto de títulos registrados.
