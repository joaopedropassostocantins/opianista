import type { Language } from "../types/content.ts";
import { cases } from "../content/cases.ts";
import { escapeHtml } from "../lib/formatters.ts";
export function InteractiveJourney(lang: Language): string {
  const segments = lang === "pt" ? [
    ["E", "Evento", "O carro passa pelo cruzamento.", "Realidade observável."],
    ["S", "Sensor", "GPS ou câmera detectam passagem.", "Captura sujeita a falhas e controle."],
    ["R", "Registro", "O software grava 'trajeto concluído'.", "Uma declaração produzida pelo sistema."],
    ["I", "Interpretação", "Auditor infere que houve deslocamento.", "Inferência que requer corroboração."]
  ] : [
    ["E", "Event", "The car crosses an intersection.", "Observable reality."],
    ["S", "Sensor", "GPS or camera detects passage.", "Capture subject to failures and control."],
    ["R", "Record", "Software stores 'journey complete'.", "A system-generated assertion."],
    ["I", "Interpretation", "Auditor infers that travel occurred.", "Inference requiring corroboration."]
  ];
  const cards = segments.map(s => '<li class="journey-item"><span class="journey-letter">' + s[0] + '</span><div><strong>' + s[1] + '</strong><p>' + s[2] + '</p><small>' + s[3] + '</small></div></li>').join("");
  const example = cases.map(c => '<details class="case"><summary><span>' + escapeHtml(c.title) + '</span><span class="case-year">' + c.year + '</span></summary><p>' + escapeHtml(c.description[lang]) + '</p><p class="small-muted">' + escapeHtml(c.caution[lang]) + '</p></details>').join("");
  return '<section class="section section-dark" id="percurso"><div class="container">' +
    '<div class="section-top"><p class="eyebrow">' + (lang === "pt" ? "02 / O PARADOXO" : "02 / THE PARADOX") + '</p>' +
    '<h2>' + (lang === "pt" ? "Quatro camadas. Uma inferência." : "Four layers. One inference.") + '</h2>' +
    '<p>' + (lang === "pt" ? "Inspecionar um registro não equivale a observar novamente o evento. O exemplo do percurso mostra onde pode surgir o descompasso." : "Inspecting a record is not equivalent to observing the event anew. The journey example shows where discrepancies may arise.") + '</p></div>' +
    '<ol class="journey-list">' + cards + '</ol>' +
    '<div class="journey-bottom"><div><h3>' + (lang === "pt" ? "Casos para pensar" : "Cases to consider") + '</h3><p class="small-muted">' +
    (lang === "pt" ? "Exemplos históricos de riscos de confiança em software — não demonstrações de fraude eleitoral." : "Historical examples of software-trust risks — not evidence of electoral fraud.") +
    '</p></div><div class="case-stack">' + example + '</div></div></div></section>';
}
