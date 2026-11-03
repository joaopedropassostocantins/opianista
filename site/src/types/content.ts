export type Language = "pt" | "en";
export type Localized = Record<Language, string>;
export type StageStatus = "pendente" | "em_andamento" | "bloqueada" | "concluida" | "aprovada";
export type StudyStatus = "preregistrado" | "exploratorio" | "em_andamento" | "proposta";
export interface Stage {
  number: number;
  slug: string;
  title: Localized;
  summary: Localized;
  status: StageStatus;
  gate?: string;
  deliverables: string[];
  repositoryPath: string;
  lastUpdated: string;
}
export interface Study {
  number: number;
  title: Localized;
  question: Localized;
  status: StudyStatus;
  repositoryPath: string;
}
export interface Evidence {
  id: string;
  title: Localized;
  supports: Localized;
  doesNotSupport: Localized;
}
export interface Source {
  id: string;
  name: string;
  url: string;
  category: "repositorio" | "institucional" | "original";
  verification: "conferida_no_repositorio" | "pendente";
}
