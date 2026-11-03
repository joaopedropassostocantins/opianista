import type { Language } from "../types/content.ts";
import { project } from "../content/project.ts";
import { escapeHtml } from "../lib/formatters.ts";
export function Footer(lang: Language): string {
  return '<footer class="footer"><div class="container footer-grid"><div><div class="footer-brand">opianista<span>.</span></div><p>' +
    (lang === "pt" ? "Pesquisa aberta. Separação entre teoria, hipóteses, dados e evidência." : "Open research. Separating theory, hypotheses, data and evidence.") +
    '</p><small>' + (lang === "pt" ? "Versão editorial" : "Editorial snapshot") + ': ' + escapeHtml(project.updated) + ' · MIT / CC BY 4.0</small></div>' +
    '<div class="footer-links"><a href="' + project.repository + '" target="_blank" rel="noopener noreferrer">GitHub ↗</a>' +
    '<a href="./arquivo/conteudo_base_20261026.md" target="_blank" rel="noopener noreferrer">' + (lang === "pt" ? "Texto-base preservado" : "Preserved source text") + ' ↗</a>' +
    '<a href="' + project.canonicalOriginal + '" target="_blank" rel="noopener noreferrer">' + (lang === "pt" ? "Site original" : "Original website") + ' ↗</a></div></div></footer>';
}
