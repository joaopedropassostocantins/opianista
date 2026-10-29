import type { Study } from "../types/content.ts";

export const studies: Study[] = [
  {
    number: 1,
    title: { pt: "Prorrogação e horário de votação", en: "Extended voting hours" },
    question: { pt: "O padrão de votos após as 17h difere das explicações operacionais?", en: "Do votes after 5 p.m. differ from operational explanations?" },
    status: "preregistrado",
    repositoryPath: "estudos/01_prorrogacao_did/README.md"
  },
  {
    number: 2,
    title: { pt: "Transferência entre turnos", en: "Between-round vote transfers" },
    question: { pt: "A movimentação entre turnos é atípica diante de modelos alternativos?", en: "Are shifts between rounds unusual under alternative models?" },
    status: "exploratorio",
    repositoryPath: "estudos/02_transferencia_votos/README.md"
  },
  {
    number: 3,
    title: { pt: "Hipótese do mesário pianista", en: "Poll-worker insertion hypothesis" },
    question: { pt: "Durante TODA a jornada de votação, os logs apresentam padrões temporais incompatíveis com a operação regular?", en: "Across the FULL voting day, do voting-machine logs show timing inconsistent with normal operation?" },
    status: "em_andamento",
    repositoryPath: "estudos/03_pianista/README.md"
  },
  {
    number: 4,
    title: { pt: "Limites de auditabilidade", en: "Limits of auditability" },
    question: { pt: "Quais alterações poderiam ser detectadas por evidências independentes?", en: "Which alterations could be detected by independent evidence?" },
    status: "proposta",
    repositoryPath: "estudos/04_auditabilidade/README.md"
  },
  {
    number: 5,
    title: { pt: "Urnas de encerramento tardio: BU integral e relógio", en: "Late-closing sections: full BU and clock integrity" },
    question: { pt: "Qual o perfil de TODOS os votos das seções que encerraram tardiamente, e como verificar seus horários?", en: "What is the profile of ALL votes in late-closing sections, and how trustworthy are their timestamps?" },
    status: "exploratorio",
    repositoryPath: "estudos/05_simulacao_temporal/README.md"
  }
];
