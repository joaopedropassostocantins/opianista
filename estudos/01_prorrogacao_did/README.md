# Estudo 01 - Prorrogacao do horario e votacao por secao (DiD pre-registrado)

## Pergunta

Os votos registrados apos as 17h no 2o turno de 25/10/2026, inclusive na
prorrogacao efetiva a partir de 17h49, alteraram a votacao das secoes alem do
esperado pela comparacao com o 1o turno e com os 2os turnos de 2022 e 2018?

## Protocolo

- Prompt de origem: `protocolos/00_prompt_preregistro_original_20261026.md`
- Pre-registro: `protocolos/00_preregistro.md` (pendente de envio; hash em
  `protocolos/REGISTRO.md`)
- Teste primario: dL_s = alfa_local + beta * V17_s + gamma * X_s + e_s, com
  efeitos fixos de local de votacao e erros agrupados por zona.
- Limite de materialidade: nenhum efeito pode exceder o total de votos apos
  17h da secao.

## Situacao

| Item | Status |
|------|--------|
| Pre-registro congelado (2026-10-26T04:13:03Z) | Feito |
| Coleta 2T 2026 por secao | Bloqueada em 26/10: BU e logs do 2T nao publicados |
| Pipeline validado com 2T 2022 (calibracao de sigma_d e placebo S5) | Pendente |
| Base do 1T 2026 | Pendente |
| Censo de votos apos 17h e apos 17h49 | Pendente |

## Analises exploratorias ja realizadas (nao confirmatorias)

Registradas em conversa de 26/10/2026; precisam de codigo e dados neste
repositorio para serem reproduzidas.

1. Correlacao entre proporcao de eleitores sem biometria e ganho de Lula entre
   turnos: desaparece com efeitos fixos regionais (regressao, permutacao e
   placebo).
2. Amostra de ~2,1% das secoes: 553 votos apos 17h; diferenca pareada no voto
   em Lula entre secoes sinalizadas e controles da mesma zona de 0,0 p.p.
   (IC95% -2,0 a +2,1).
3. Ordem de grandeza: extrapolacao da amostra indicou cerca de 26 mil votos
   apos 17h, frente a margem de 4.430.191 votos. A confirmar pelo censo dos
   logs.

## Como contribuir

Prioridade atual: parser de `.logjez` validado no 2T 2022 e extracao de V17,
T e T_prorr. Ver `CONTRIBUTING.md` na raiz.
