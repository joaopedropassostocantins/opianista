import type { Language } from "../types/content.ts";
import { stages, editorialConflict } from "../content/stages.ts";
import { githubFile } from "../lib/github-links.ts";
import { escapeHtml, statusLabel } from "../lib/formatters.ts";
export function StatusTimeline(lang: Language): string {
  const steps = stages.map(s => '<li class="stage stage-' + s.status + '"><span class="stage-number">' + String(s.number).padStart(2, "0") + '</span>' +
    '<div class="stage-details"><div class="stage-heading"><h3>' + escapeHtml(s.title[lang]) + '</h3><span class="badge ' + s.status + '">' + escapeHtml(statusLabel(s.status, lang)) + '</span></div>' +
    '<p>' + escapeHtml(s.summary[lang]) + '</p><a class="text-link" href="' + githubFile(s.repositoryPath) + '" target="_blank" rel="noopener noreferrer">' +
    (lang === "pt" ? "Ver etapa" : "View stage") + ' ↗</a></div></li>').join("");
  return '<section class="section section-paper" id="etapas"><div class="container">' +
    '<div class="section-top"><p class="eyebrow">04 / ' + (lang === "pt" ? "ACOMPANHAMENTO" : "PROGRESS") + '</p><h2>' +
    (lang === "pt" ? "Etapas do Estudo 03" : "Study 03 stages") + '</h2><p>' +
    (lang === "pt" ? "Estado editorial congelado em 29/10/2026, conforme documentação consultada; não é um feed em tempo real." : "Editorial snapshot as of 2026-10-29, based on reviewed repository documents; not a live feed.") +
    '</p></div><ol class="timeline">' + steps + '</ol><div class="editorial-conflict" role="note"><strong>' +
    (lang === "pt" ? "Inconsistência documental identificada" : "Document inconsistency identified") + '</strong><p>' + escapeHtml(editorialConflict[lang]) + '</p></div></div></section>';
}
