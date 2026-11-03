import type { Language } from "../types/content.ts";
import { project } from "../content/project.ts";
import { escapeHtml } from "../lib/formatters.ts";
export function Hero(lang: Language): string {
  return '<section class="hero" aria-labelledby="hero-title"><div class="container hero-grid"><div>' +
    '<p class="eyebrow">' + (lang === "pt" ? "ENSAIO · AUDITABILIDADE · PESQUISA ABERTA" : "ESSAY · AUDITABILITY · OPEN RESEARCH") + '</p>' +
    '<h1 id="hero-title">' + (lang === "pt" ? 'Quem fiscaliza o <em>arquiteto</em>?' : 'Who audits the <em>architect</em>?') + '</h1>' +
    '<p class="hero-question">' + escapeHtml(project.question[lang]) + '</p>' +
    '<p class="hero-lead">' + escapeHtml(project.lead[lang]) + '</p>' +
    '<div class="hero-actions"><a class="btn btn-accent" href="#tese">' + (lang === "pt" ? "Explorar a tese" : "Explore the thesis") + ' ↗</a>' +
    '<a class="btn btn-outline" href="#estudos">' + (lang === "pt" ? "Acompanhar os estudos" : "Follow the studies") + '</a></div></div>' +
    '<div class="hero-art" aria-hidden="true"><div class="orbit o1"></div><div class="orbit o2"></div><div class="orbit o3"></div><span class="art-center">E ≠ R</span><span class="art-caption">EVENTO / REGISTRO</span></div>' +
    '</div></section>';
}
