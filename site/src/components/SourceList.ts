import type { Language } from "../types/content.ts";
import { sources } from "../content/sources.ts";
import { escapeHtml } from "../lib/formatters.ts";
import { safeLink } from "../lib/citations.ts";
export function SourceList(lang: Language): string {
  return '<section class="section section-paper" id="fontes"><div class="container">' +
    '<div class="section-top"><p class="eyebrow">06 / ' + (lang === "pt" ? "RASTREABILIDADE" : "TRACEABILITY") + '</p><h2>' +
    (lang === "pt" ? "Fontes e documentação" : "Sources and documentation") + '</h2><p>' +
    (lang === "pt" ? "Documentos científicos permanecem no repositório, e a versão publicada original continua identificada separadamente." : "Research documents remain in the repository, while the original publication is separately identified.") +
    '</p></div><ul class="sources-list">' + sources.map(s => '<li><a target="_blank" rel="noopener noreferrer" href="' + escapeHtml(safeLink(s.url)) + '">' +
    escapeHtml(s.name) + ' ↗</a><span>' + (s.verification === "pendente" ? (lang === "pt" ? "Link externo: conferência pendente" : "External link: verification pending") : (lang === "pt" ? "Conferido no GitHub" : "Checked on GitHub")) +
    '</span></li>').join("") + '</ul></div></section>';
}
