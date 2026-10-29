import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { ProjectBrief } from "../src/components/ProjectBrief.ts";
import { InteractiveJourney } from "../src/components/InteractiveJourney.ts";
import { StatusTimeline } from "../src/components/StatusTimeline.ts";
import { EvidenceCard } from "../src/components/EvidenceCard.ts";
import { evidence } from "../src/content/evidence.ts";
test("document contains language, viewport, skip link and landmark", () => {
  const html = readFileSync(resolve("index.html"), "utf-8");
  assert.match(html, /lang="pt-BR"/);
  assert.match(html, /name="viewport"/);
  assert.match(html, /class="skip-link"/);
  const css = readFileSync(resolve("src/styles/base.css"), "utf-8");
  assert.match(css, /focus-visible/);
  assert.match(css, /prefers-reduced-motion/);
});
test("rendered sections contain headings, labels and keyboard-accessible disclosures", () => {
  for (const lang of ["pt","en"]) {
    assert.match(ProjectBrief(lang), /<h2/);
    assert.match(InteractiveJourney(lang), /<details/);
    assert.match(StatusTimeline(lang), /<ol class="timeline"/);
    assert.match(EvidenceCard(evidence[0], lang), /<h3/);
  }
});
