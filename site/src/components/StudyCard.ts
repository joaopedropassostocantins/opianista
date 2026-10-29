import type { Language, Study } from "../types/content.ts";
import { githubFile } from "../lib/github-links.ts";
import { escapeHtml, statusLabel } from "../lib/formatters.ts";
export function StudyCard(study: Study, lang: Language): string {
  return '<article class="study-card"><div class="card-meta"><span class="card-index">ESTUDO ' + String(study.number).padStart(2, "0") + '</span><span class="badge ' + study.status + '">' +
    escapeHtml(statusLabel(study.status, lang)) + '</span></div><h3>' + escapeHtml(study.title[lang]) + '</h3><p>' + escapeHtml(study.question[lang]) + '</p>' +
    '<a class="text-link" href="' + githubFile(study.repositoryPath) + '" target="_blank" rel="noopener noreferrer">' +
    (lang === "pt" ? "Documentação canônica" : "Canonical documentation") + ' ↗</a></article>';
}
