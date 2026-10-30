# Parecer critico revisado - Projeto O Pianista (recebido em 30/10/2026)

Texto do proponente, arquivado para continuidade. As respostas ponto a ponto estao em
`RESPOSTA_PARECER_20261030.md`. Observacao de arquivo: o texto recebido tem um trecho
truncado na secao 8 ("quem deixou de se abster ou"), mantido como chegou.

## Objeto e limitacao

Revisao cientifica, estatistica, computacional e metodologica do relatorio preliminar
de 29/10/2026, incorporando as hipoteses sobre mesarios, biometria, cadencia de
votacao, abstencao, votos invalidos, transferencias eleitorais, vulnerabilidades de
software, ameacas internas e auditabilidade. Material: relatorio, codigo da analise
nacional, JSON de resultados, manifestos, documentos dos Estudos 02, 03 e 05,
protocolos e auditoria transversal do PR #6, confrontados com a publicacao do TSE
atualizada em 29/10. Nao constitui segunda execucao independente dos 124 GB.

## 1 Parecer geral

O relatorio nao deve ser aprovado como auditoria abrangente da eleicao presidencial
de 2026. E uma investigacao estatistica delimitada sobre encerramento tardio e
composicao dos votos. Problemas estruturais: (1) incompletude - sem execucao nacional
de cadencia por minuto, biometria, abstencao, brancos e nulos e deteccao abrangente
de anomalias; (2) identificabilidade - usa registros da urna para avaliar hipoteses
que incluem o comprometimento desses registros; (3) inferencia excessiva;
(4) reprodutibilidade incompleta - divergencias nao reconciliadas, exclusoes
relevantes; (5) escopo de seguranca insuficiente - insider e cadeia de suprimentos
apenas conceituais. Resultado nulo sobre encerramento tardio nao e resultado nulo de
auditoria de integridade.

## 2 Onze secoes nao equivalem a onze votos

TSE (29/10): votos apos 17h 34.393; 17h-18h 32.399; 18h-19h 1.981; apos 19h 13;
secoes encerradas apos 19h 6.766; votos apos 17h nas secoes encerradas apos 19h 4.773.
O JSON registra 11 secoes com ultimo voto apos 19h. Correcao: distinguir 11 secoes e
13 votos oficiais, com reconciliacao evento por evento.

## 3 Ausencia de diferenca onde ha testes nao conclusivos

Primario (+0,81; -1,67 a +3,29; 11 secoes), secundario (-0,08; -0,27 a +0,12),
fila apos 17h (-0,05; -0,11 a -0,002; p = 0,042), fechamento apos 19h (-0,04;
-0,26 a +0,19), governador apos 19h nao estimavel. Formulacao adequada: os
contrastes confirmatorios nao identificaram associacao significativa; um exploratorio
identificou efeito muito pequeno; outros nao tiveram dados suficientes.

## 4 Inconsistencia na contagem horaria

2024: 10.546 secoes com ultimo voto apos 17h e 0 votos apos 17h pelo histograma.
Reproduzir a contagem a partir dos eventos; reconciliar campos por secao com o
horario de Brasilia.

## 5 Dados excluidos

1.443 secoes com problema de coerencia (1.419 log x BU, 21 campos ausentes,
3 divergencia temporal). Separar populacao estatistica validada de populacao de
auditoria; manter inventario com classificacao de causas.

## 6 Conversao de horarios nao valida o relogio

brasilia_offsets usa a hora de abertura do proprio BU. Usar tabela externa de fusos
por municipio (Acre, oeste do Amazonas). Distinguir ultimo voto, encerramento
confirmado, fechamento no BU, geracao, impressao, transmissao, recepcao e totalizacao.
A recepcao e referencia externa de processamento, nao do horario do ultimo voto.

## 7 Materialidade interpretada de forma ampla

Formulacao defensavel: "Uma transferencia de votos exclusivamente entre os dois
finalistas, limitada aos votos validos registrados nas secoes identificadas como
tardias pelo criterio utilizado, nao seria suficiente para inverter a margem
nacional." Nao exclui alteracoes distribuidas nem comprometimento anterior ao BU; a
propria classificacao da coorte depende do relogio.

## 8 Abstencao e votos invalidos omitidos

Comparecimento 125.275.835 (1T) e 128.236.074 (2T), +2.960.239; abstencao 21,08% e
19,22%; brancos e nulos 5.975.047 e 4.153.801 (-1.821.246); votos dos eliminados no
1T 9.316.747; crescimento dos finalistas +14.098.232 = 9.316.747 + 2.960.239 +
1.821.246. Fechamento contabil nao e explicacao comportamental; a identidade nao
demonstra quais eleitores mudaram de candidato, quem deixou de se abster ou [trecho
truncado no original].

## 9 Erro metodologico e diretriz

Segundos turnos presidenciais nao podem ser paradigma de normalidade temporal
(circularidade diante da hipotese de comprometimento da cadeia de desenvolvimento).
Hierarquia: (1) eleicoes estaduais e municipais anteriores a urna eletronica
(1990, 1992, 1994); (2) segundos turnos municipais (2000-2024); (3) segundos turnos
estaduais (complementares quando simultaneos ao presidencial). Grupo C (presidencial
eletronico) nao define parametros. Modelo lambda_s(t) por minuto, jornada integral,
periodos sem movimento, rajadas, habilitacoes sem biometria, poder para mecanismos
distribuidos, controles negativos. O relatorio deve reconhecer que a hipotese de
comportamento temporal atipico em eleicoes presidenciais permanece nao testada de
forma abrangente. Registrado como `protocolos/08_diretriz01_referencias_historicas_20261030.md`.
