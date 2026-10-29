import type { Evidence, Language } from "../types/content.ts";
import { escapeHtml } from "../lib/formatters.ts";
export function EvidenceCard(item: Evidence, lang: Language): string {
  return '<article class="evidence-card"><h3>' + escapeHtml(item.title[lang]) + '</h3><div class="evidence-row"><span class="can">' +
    (lang === "pt" ? "O que sustenta" : "Can support") + '</span><p>' + escapeHtml(item.supports[lang]) + '</p></div><div class="evidence-row"><span class="cannot">' +
    (lang === "pt" ? "O que não sustenta" : "Cannot establish") + '</span><p>' + escapeHtml(item.doesNotSupport[lang]) + '</p></div></article>';
}
