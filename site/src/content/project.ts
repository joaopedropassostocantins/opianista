import type { Localized } from "../types/content.ts";

export const project = {
  name: "opianista",
  siteTitle: "O Paradoxo do Arquiteto-Fiscal",
  canonicalOriginal: "https://arquiteto-fiscal-evidencia.hazyzebra6.chatgpt.site",
  repository: "https://github.com/joaopedropassostocantins/opianista",
  updated: "2026-10-29",
  question: {
    pt: "Se houve fraude, os registros do próprio sistema bastariam para demonstrá-la?",
    en: "If fraud occurred, would the system's own records be enough to establish it?"
  } satisfies Localized,
  lead: {
    pt: "A resposta exige examinar como as evidências são produzidas, quem controla os registros e quais observações independentes podem confrontá-los.",
    en: "The answer requires examining how evidence is produced, who controls the records, and which independent observations can challenge them."
  } satisfies Localized,
  caveat: {
    pt: "Ensaio conceitual e acompanhamento de pesquisa independente. Nenhuma anomalia, por si só, prova fraude; a ausência de anomalias também não prova invulnerabilidade. Não há aqui conclusão pericial sobre eleições.",
    en: "Conceptual essay and independent research tracker. An anomaly alone does not prove fraud, nor does its absence prove invulnerability. This is not an electoral forensic finding."
  } satisfies Localized
};
