import type { Evidence } from "../types/content.ts";

export const evidence: Evidence[] = [
  {
    id: "bu",
    title: { pt: "Boletim de Urna (BU)", en: "Voting-machine bulletin (BU)" },
    supports: { pt: "Totais produzidos e publicados pela urna no encerramento.", en: "Totals produced and published by the machine at closing." },
    doesNotSupport: { pt: "Por si só, a correspondência entre registro eletrônico e intenção real do eleitor.", en: "On its own, correspondence between electronic records and voter intent." }
  },
  {
    id: "log",
    title: { pt: "Logs e eventos", en: "Logs and events" },
    supports: { pt: "Sequência e horários de eventos reconhecidos pelo software.", en: "Order and timestamps of software-recorded events." },
    doesNotSupport: { pt: "A ocorrência material de fatos não observados por sensores independentes.", en: "The material occurrence of events not observed by independent sensors." }
  },
  {
    id: "estatistica",
    title: { pt: "Testes estatísticos", en: "Statistical tests" },
    supports: { pt: "Incompatibilidade com hipóteses e modelos explicitamente definidos, dadas as premissas.", en: "Incompatibility with explicit models and hypotheses, conditional on assumptions." },
    doesNotSupport: { pt: "Autoria, intenção, mecanismo específico ou prova penal automática.", en: "Authorship, intent, a specific mechanism or automatic legal proof." }
  },
  {
    id: "independente",
    title: { pt: "Observação independente", en: "Independent observation" },
    supports: { pt: "Confrontação entre domínios de controle distintos quando há procedência e integridade verificadas.", en: "Cross-checks across different control domains when provenance and integrity are verified." },
    doesNotSupport: { pt: "Infalibilidade; cada fonte também possui limites e possíveis dependências.", en: "Infallibility; every source has limitations and possible dependencies." }
  }
];
