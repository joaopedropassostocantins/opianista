import type { Language } from "../types/content.ts";
import { project } from "../content/project.ts";
import { escapeHtml } from "../lib/formatters.ts";
export function MethodNotice(lang: Language): string {
  return '<aside class="method-notice" role="note"><div class="container notice-row"><strong>' +
  (lang === "pt" ? "Limite metodológico" : "Methodological limit") +
  '</strong><p>' + escapeHtml(project.caveat[lang]) + '</p></div></aside>';
}
