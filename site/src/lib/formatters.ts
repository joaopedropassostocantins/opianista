import type { Language, StageStatus, StudyStatus } from "../types/content.ts";
export function escapeHtml(text: string): string {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
export function statusLabel(status: StageStatus | StudyStatus, lang: Language): string {
  const dictionary: Record<StageStatus | StudyStatus, { pt: string; en: string }> = {
    pendente: { pt: "Pendente", en: "Pending" },
    em_andamento: { pt: "Em andamento", en: "In progress" },
    bloqueada: { pt: "Bloqueada", en: "Blocked" },
    concluida: { pt: "Concluída", en: "Completed" },
    aprovada: { pt: "Aprovada", en: "Approved" },
    preregistrado: { pt: "Pré-registrado", en: "Preregistered" },
    exploratorio: { pt: "Exploratório", en: "Exploratory" },
    proposta: { pt: "Proposta", en: "Proposal" }
  };
  return dictionary[status][lang];
}
