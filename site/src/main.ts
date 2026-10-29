import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/layout.css";
import "./styles/components.css";
import "./styles/responsive.css";
import "./styles/lab.css";
import { getLanguage } from "./app/router.ts";
import { enhanceAccessibility } from "./app/accessibility.ts";
import { Header } from "./components/Header.ts";
import { Hero } from "./components/Hero.ts";
import { MethodNotice } from "./components/MethodNotice.ts";
import { ProjectBrief } from "./components/ProjectBrief.ts";
import { InteractiveJourney } from "./components/InteractiveJourney.ts";
import { StudyCard } from "./components/StudyCard.ts";
import { StatusTimeline } from "./components/StatusTimeline.ts";
import { EvidenceCard } from "./components/EvidenceCard.ts";
import { SourceList } from "./components/SourceList.ts";
import { Footer } from "./components/Footer.ts";
import { TemporalSimulator, attachTemporalSimulator } from "./components/TemporalSimulator.ts";
import { studies } from "./content/studies.ts";
import { evidence } from "./content/evidence.ts";

const lang = getLanguage(window.location.search);
document.documentElement.lang = lang === "pt" ? "pt-BR" : "en";
document.title = (lang === "pt" ? "O Paradoxo do Arquiteto-Fiscal" : "The Architect-Auditor Paradox") + " | opianista";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("Missing #app root");
app.innerHTML = [
  Header(lang),
  Hero(lang),
  MethodNotice(lang),
  '<main id="conteudo">',
  ProjectBrief(lang),
  InteractiveJourney(lang),
  '<section class="section" id="estudos"><div class="container">',
  '<div class="section-top"><p class="eyebrow">03 / ' + (lang === "pt" ? "INVESTIGAÇÃO" : "RESEARCH") + '</p><h2>' +
    (lang === "pt" ? "Cinco estudos. Perguntas verificáveis." : "Five studies. Testable questions.") + '</h2><p>' +
    (lang === "pt" ? "O site explica; os arquivos canônicos, as limitações e as revisões estão no GitHub." : "This site explains; canonical files, limitations and revisions live on GitHub.") +
    '</p></div><div class="study-grid">',
  ...studies.map(s => StudyCard(s, lang)),
  '</div></div></section>',
  StatusTimeline(lang),
  TemporalSimulator(lang),
  '<section class="section" id="evidencias"><div class="container">',
  '<div class="section-top"><p class="eyebrow">05 / ' + (lang === "pt" ? "TEORIA DA PROVA" : "EVIDENCE THEORY") + '</p><h2>' +
    (lang === "pt" ? "O que cada evidência realmente permite concluir" : "What each evidence type can actually support") +
    '</h2></div><div class="evidence-grid">',
  ...evidence.map(e => EvidenceCard(e, lang)),
  '</div></div></section>',
  SourceList(lang),
  '</main>',
  Footer(lang)
].join("");
enhanceAccessibility();
attachTemporalSimulator(lang);
