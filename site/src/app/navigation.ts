import type { Language } from "../types/content.ts";
export const navigation = [
  { id: "tese", label: { pt: "Tese", en: "Thesis" } },
  { id: "percurso", label: { pt: "O percurso", en: "The journey" } },
  { id: "estudos", label: { pt: "Estudos", en: "Studies" } },
  { id: "etapas", label: { pt: "Etapas", en: "Stages" } },
  { id: "simulador", label: { pt: "Simulador", en: "Simulator" } },
  { id: "evidencias", label: { pt: "Evidências", en: "Evidence" } },
  { id: "fontes", label: { pt: "Fontes", en: "Sources" } }
] as const;
export function navigationLinks(lang: Language) {
  return navigation.map(item => ({ id: item.id, label: item.label[lang], href: "#" + item.id }));
}
