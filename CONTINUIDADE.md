# Continuidade do trabalho (para outra IA ou nova sessao)

Atualizado em 29/10/2026. Leia este arquivo primeiro. Ele resume o estado, onde
cada coisa esta e como retomar. Atualize-o ao fim de cada etapa, no mesmo
commit do trabalho.

## 1 Regras que nao podem ser quebradas

1. Pre-registros e emendas em `protocolos/` nunca sao editados depois de
   commitados; mudancas entram como nova emenda, com SHA-256 em
   `protocolos/REGISTRO.md`.
2. Dados brutos ficam em `data/` (fora do Git, ver `.gitignore`). Nunca commitar
   arquivos do TSE, logs, BU ou listas com titulo de eleitor/CPF. O log da urna
   registra o titulo do eleitor que encerra a secao: nao copiar essa linha.
3. Nada de alegacao de fraude: resultados sao associacoes, com a limitacao do
   relogio da urna (README do Estudo 05). Nulos e positivos com o mesmo destaque.
4. O proponente e joaopedropassostocantins. Decisoes de abertura de dados e de
   aprovacao de GATE sao dele e ficam registradas em `REGISTRO.md`.
5. Textos sem emojis; documentos finais em ABNT (preferencias do proponente).

## 2 Estado em 29/10/2026

| Frente | Estado | Onde |
|---|---|---|
| Estudo 03 (mesario pianista), piloto TO | Concluido: nenhuma hipotese sustentada | `estudos/03_pianista/etapas/05_inferencia/resultados_piloto_TO/` |
| Estudo 03 fora de TO | Rebaixado a exploratorio (2T2026 aberto antes da emenda nacional) | `REGISTRO.md`, ultima secao |
| Estudo 05 pre-registro | E05-0 aprovado com emendas 01 e 02 (TO fora do confirmatorio) | `protocolos/04_...`, `05_...`, `07_...` |
| Estudo 05 placebo 2T2024 | Concluido, 51 municipios, resultado nulo | `estudos/05_simulacao_temporal/RESULTADO_PLACEBO_2T2024_TO_20261029.md` |
| Estudo 05 placebo 1T2026 | Bloqueado pela trava da emenda 01 (eventos 05-12/10); exige emenda | mesmo arquivo, secao 9 |
| Estudo 05 analise 2T2026 | EM ANDAMENTO: extracao por UF | ver secao 3 |
| Relatorio preliminar | A fazer, apos a extracao | ver secao 4 |
| Pedido LAI ao TSE | Rascunho pronto, envio pelo proponente | `estudos/05_simulacao_temporal/PEDIDO_LAI_TSE_20261029.md` |
| PR #3 | Rascunho, CI verde | branch `feat/migracao-site-independente-20261029` |
| PR #5 | Site, empilhado sobre o PR #3 | outra sessao |

## 3 Como retomar a extracao do 2T2026

Os scripts sao idempotentes: pulam UFs ja extraidas e retomam downloads.

```bash
cd /caminho/opianista
mkdir -p data/2026_2t/arq data/2026_2t/horarios
rm -rf data/2026_2t/arq/lock_*        # travas de execucao interrompida
S=estudos/05_simulacao_temporal/scripts/processa_2T2026.sh
# UFs pequenas e medias (3 em paralelo), depois BA RJ MG (2), depois SP (sozinho, 25,8 GB)
L="AC ZZ RR AP TO RO SE MS DF AL AM PI MT RN ES PB GO MA SC PA PE CE PR RS"
( $S $L & $S $L & $S $L & wait; $S BA RJ MG & $S BA RJ MG & wait; $S SP )
ls data/2026_2t/horarios/            # um CSV por UF, mais manifesto.tsv
```

Total de 124 GB em 28 arquivos (27 UFs e exterior). Disco livre na sessao
original: cerca de 30 GB, por isso a ordem acima. Cada ZIP e apagado depois da
extracao; URL, Last-Modified e SHA-256 ficam em `manifesto.tsv`.

O placebo 2T2024 usa `scripts/processa_2T2024.sh` com as mesmas regras
(saida em `data/2024/horarios/`).

## 4 Como gerar a analise e o relatorio

```bash
python3 -I estudos/05_simulacao_temporal/analise_2t2026.py \
  --h2026 data/2026_2t/horarios/horarios_2T2026_*.csv \
  --h2024 data/2024/horarios/horarios_2T2024_*.csv \
  --liberado-d4 "REGISTRO.md 2026-10-29" \
  --out estudos/05_simulacao_temporal/resultados/analise_2T2026.json
```

O JSON traz: validacao contra os numeros oficiais (totais de Lula e Flavio,
secoes apos 17h, 17h10 e 19h, votos apos 17h), contrastes do pre-registro
(primario > 19h x <= 17h; secundario > 17h10; fila > 17h; governador; TO como
sensibilidade), correcao de Holm e materialidade.

Relatorio preliminar a redigir: `estudos/05_simulacao_temporal/RELATORIO_PRELIMINAR_2T2026.md`
e versao .docx em ABNT (python-docx disponivel), reunindo: hipoteses, dados,
validacao, placebo 2024, resultados 2026, piloto TO do Estudo 03, materialidade,
limitacoes e proximos passos.

## 5 Cuidados tecnicos aprendidos

1. O relogio da urna registra a **hora local**; a votacao segue a hora de
   Brasilia. `contraste_local.brasilia_offsets` converte por municipio usando a
   hora de abertura mais frequente (abertura as 8h de Brasilia). No exterior
   (ZZ) a votacao segue a hora local: fica fora dos contrastes.
2. A imagem do BU de 2026 escreve "2° Turno" (sinal de grau); a de 2024,
   "2º Turno" (ordinal).
3. O log da urna contem o 1o e o 2o turno. Filtrar pela data da eleicao.
4. Log com menos votos que o BU indica urna substituida: a secao e excluida
   (emenda 01, secao 3).
5. Em 2024 nao houve ultimo voto depois das 19h; os cortes de 17h10 e 19h so
   sao estimaveis em 2026.
6. Os arquivos `votacao_secao_2026_*.zip` foram regravados apos o 2T e misturam
   turnos; use os arquivos transmitidos por turno (`arqurnatot`).

## 6 Decisoes pendentes do proponente

1. Emenda para o placebo 1T2026 (criterio "nenhum evento a partir de 25/10/2026").
2. Envio do pedido LAI.
3. Revisao do relatorio preliminar e decisao sobre o PR #3 sair de rascunho.
