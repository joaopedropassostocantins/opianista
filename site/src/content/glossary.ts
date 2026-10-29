import type { Localized } from "../types/content.ts";

export const glossary: { term: string; definition: Localized }[] = [
  { term: "BU", definition: { pt: "Boletim de Urna: documento com os totais da seção apurados pela urna.", en: "Voting-machine bulletin with the machine's section totals." } },
  { term: "RDV", definition: { pt: "Registro Digital do Voto: estrutura eletrônica dos votos armazenados, sem identificação nominal do eleitor.", en: "Digital voting record, without named voter attribution." } },
  { term: "Log", definition: { pt: "Registro de evento reconhecido por um sistema.", en: "Record of an event acknowledged by a system." } },
  { term: "RLA", definition: { pt: "Registro de Log de Aplicação, conforme denominação a verificar no contexto técnico.", en: "Application log record, terminology to verify in technical context." } },
  { term: "FDR", definition: { pt: "Sigla dependente do documento-fonte; não presumir significado sem referência.", en: "Context-dependent acronym; do not assume a definition without a source." } }
];
