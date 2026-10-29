import test from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { stages, editorialConflict } from "../src/content/stages.ts";
import { studies } from "../src/content/studies.ts";
import { evidence } from "../src/content/evidence.ts";
import { sources } from "../src/content/sources.ts";
import { project } from "../src/content/project.ts";
import { glossary } from "../src/content/glossary.ts";
const hasLocales = value => Boolean(value?.pt?.trim() && value?.en?.trim());
test("the five studies have unique numbers, titles, questions and existing paths", () => {
  assert.equal(studies.length, 5);
  assert.equal(new Set(studies.map(s => s.number)).size, 4);
  for (const study of studies) {
    assert.ok(hasLocales(study.title) && hasLocales(study.question));
    assert.ok(existsSync(resolve("..", study.repositoryPath)), study.repositoryPath);
  }
});
test("the eight stages have unique numbers, allowed statuses, bilingual text and existing paths", () => {
  assert.deepEqual(stages.map(s => s.number), [0,1,2,3,4,5,6,7]);
  for (const s of stages) {
    assert.ok(["pendente","em_andamento","bloqueada","concluida","aprovada"].includes(s.status));
    assert.ok(hasLocales(s.title) && hasLocales(s.summary));
    assert.ok(Array.isArray(s.deliverables) && s.deliverables.length > 0);
    assert.ok(existsSync(resolve("..", s.repositoryPath)), s.repositoryPath);
  }
  assert.equal(stages[0].status, "aprovada");
  assert.ok(hasLocales(editorialConflict), "Document inconsistency must be disclosed");
});
test("evidence explicitly states support and limitations", () => {
  for (const item of evidence) {
    assert.ok(hasLocales(item.title) && hasLocales(item.supports) && hasLocales(item.doesNotSupport));
  }
});
test("sources have unique IDs and valid HTTPS URLs", () => {
  assert.equal(new Set(sources.map(s => s.id)).size, sources.length);
  for (const source of sources) assert.equal(new URL(source.url).protocol, "https:");
  assert.ok(hasLocales(project.question) && hasLocales(project.caveat));
  assert.ok(glossary.every(g => hasLocales(g.definition)));
});
