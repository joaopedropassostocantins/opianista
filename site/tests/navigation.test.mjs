import test from "node:test";
import assert from "node:assert/strict";
import { navigation, navigationLinks } from "../src/app/navigation.ts";
import { getLanguage, languageUrl, normalizedHash } from "../src/app/router.ts";
import { githubFile } from "../src/lib/github-links.ts";
test("navigation anchors are unique and translated", () => {
  assert.equal(new Set(navigation.map(n => n.id)).size, navigation.length);
  assert.ok(navigationLinks("en").every(n => n.label.length && n.href === "#" + n.id));
  assert.ok(navigationLinks("pt").every(n => n.label.length));
});
test("languages and hashes are deterministic", () => {
  assert.equal(getLanguage("?lang=en"), "en");
  assert.equal(getLanguage("?lang=pt"), "pt");
  assert.equal(getLanguage("?lang=other"), "pt");
  assert.equal(languageUrl("en", "#estudos"), "?lang=en#estudos");
  assert.equal(normalizedHash("#tese"), "tese");
});
test("repository helper rejects traversal", () => {
  assert.throws(() => githubFile("../protocolos/REGISTRO.md"));
  assert.match(githubFile("protocolos/REGISTRO.md"), /blob\/main\/protocolos\/REGISTRO.md$/);
  assert.match(githubFile("estudos/03_pianista/etapas/00_protocolo/"), /tree\/main\//);
});
