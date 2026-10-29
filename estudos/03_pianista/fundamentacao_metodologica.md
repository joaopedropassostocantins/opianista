# Fundamentacao metodologica

## 1 Por que comparar medias horarias nao basta

1. Confundidor exogeno em 2026: em 25/10/2026 o STF (Min. Cristiano Zanin)
   determinou a prorrogacao da votacao ate 19h; a decisao foi divulgada por
   volta das 17h03, mas o TSE so comunicou os TREs as 17h49. O esclarecimento
   posterior restringiu a medida as secoes ainda abertas, e o TRE-DF informou
   nao ser possivel prorrogar. Houve ainda crise de transporte publico (onibus parados
   em Salvador, segundo o Procon-BA).
2. Comparador inadequado: 2o turno municipal ou estadual tem saliencia e
   comparecimento distintos do presidencial. Comparadores corretos: 2o turno
   presidencial de 2014, 2018 e 2022; 1o turno de 2026 na mesma secao (mesmos
   mesarios e eleitorado); secoes encerradas as 17h versus as que seguiram
   abertas.
3. Com cerca de 500 mil secoes, a H0 de igualdade de medias e rejeitada
   trivialmente; importam tamanho de efeito e assinatura especifica do
   mecanismo.
4. Diferenca de media nao identifica o mecanismo.

## 2 Assinaturas observaveis do "pianista" no log da urna

1. Habilitacao sem biometria (ano de nascimento digitado pelo presidente)
   concentrada na janela final.
2. Rajadas com intervalo entre votos abaixo do minimo operacional de um
   eleitor real.
3. Concentracao das liberacoes em um unico operador (a urna solicita a
   digital do mesario que libera eleitor sem biometria).
4. Rastro fisico: eleitor sem biometria reconhecida assina o caderno de
   votacao, o que permite pericia grafotecnica.

## 3 Armadilhas (falsos positivos)

1. Urnas substituidas (1.516 ate 18h no 2o turno de 2026) e votacao manual.
2. Fuso horario (MS votou ate 18h locais) e deriva de relogio da urna.
3. Votos apos 17h sao legitimos enquanto houver eleitores na fila.
4. RDV embaralhado: nao ha vinculo entre horario e escolha; a analise de
   associacao com resultado e necessariamente ecologica.

## 4 Corroboracao em fases

1. Logs e testes estatisticos (este repositorio).
2. Secoes priorizadas: atas da mesa, caderno de votacao, pericia de
   assinaturas, historico de abstencao.
3. Imagens e dados de ERB apenas mediante ordem judicial, por meio de
   autoridade competente.

## Referencias

DECKERT, J.; MYAGKOV, M.; ORDESHOOK, P. C. Benford's Law and the detection of
election fraud. **Political Analysis**, v. 19, n. 3, p. 245-268, 2011.

FUJIWARA, T. Voting technology, political responses, and infant health:
evidence from Brazil. **Econometrica**, v. 83, n. 2, p. 423-464, 2015.

KLIMEK, P. et al. Statistical detection of systematic election
irregularities. **Proceedings of the National Academy of Sciences**, v. 109,
n. 41, p. 16469-16473, 2012.

KOBAK, D.; SHPILKIN, S.; PSHENICHNIKOV, M. S. Integer percentages as
electoral falsification fingerprints. **The Annals of Applied Statistics**,
v. 10, n. 1, p. 54-73, 2016.

MEBANE, W. R. Election forensics: the second-digit Benford's law test and
recent American presidential elections. In: ALVAREZ, R. M.; HALL, T. E.;
HYDE, S. D. (ed.). **Election fraud**: detecting and deterring electoral
manipulation. Washington, DC: Brookings Institution Press, 2008. p. 162-181.

ROZENAS, A. Detecting election fraud from irregularities in vote-share
distributions. **Political Analysis**, v. 25, n. 1, p. 41-56, 2017.

STOLFI, J. Biometria nas eleicoes: falsa sensacao de seguranca.
**Jus.com.br**, 2014. Disponivel em:
https://jus.com.br/artigos/32009/biometria-nas-eleicoes-falsa-sensacao-de-seguranca.

Observacao: as referencias devem ser conferidas na fonte original antes do uso
no relatorio final (Etapa 7).

## Fontes jornalisticas e institucionais (contexto de 2026)

- TSE - Viralizou: e mentira que mesarios votam na urna no lugar de eleitores:
  https://www.tse.jus.br/comunicacao/noticias/2026/Agosto/viralizou-e-mentira-que-mesarios-votam-na-urna-eletronica-no-lugar-de-eleitores
- Times Brasil - STF determina prorrogacao:
  https://timesbrasil.com.br/brasil/decisao-2026-stf-determina-ao-tse-prorrogar-votacao-por-duas-horas-em-todo-o-brasil/
- Portal de Prefeitura - Zanin esclarece prorrogacao:
  https://portaldeprefeitura.com.br/bastidores-da-politica/zanin-esclarece-prorrogacao-votacao-urnas-ainda-abertas/634830/
- Times Brasil - TRE-DF descarta prorrogacao:
  https://timesbrasil.com.br/eleicoes-2026/decisao-2026-tre-df-descarta-prorrogacao-da-votacao-apos-decisao-do-stf-por-falta-de-tempo-habil/
- Times Brasil - urnas substituidas:
  https://timesbrasil.com.br/brasil/decisao-2026-tse-registra-troca-de-1-516-urnas-ate-as-18h/
- A Critica - MS ate 18h:
  https://acritica.net/eleicoes-2026/stf-prorroga-votacao-em-todo-o-brasil-em-ms-urnas-ficam-abertas-ate-as-18h/
- O Popular - votos apos 17h nao indicam fraude:
  https://opopular.com.br/politica/votos-depositados-nas-urnas-apos-as-17-horas-n-o-indicam-fraude-1.2566109
- Times Brasil - biometria nao reconhecida:
  https://timesbrasil.com.br/brasil/decisao-2026-o-que-acontece-se-a-biometria-nao-funcionar-na-hora-de-votar/
