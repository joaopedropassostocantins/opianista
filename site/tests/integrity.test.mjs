import test from "node:test";
import assert from "node:assert/strict";
import { evaluateIntegrity, aggregate, same, scenarios } from "../src/lib/integrity-model.ts";
import { researchPriorities } from "../src/content/insider.ts";

function status(result,id){return result.audit.find(x=>x.id===id).status;}

test("five priorities have sources and bilingual definitions",()=>{
 assert.deepEqual(researchPriorities.map(x=>x.number),[1,2,3,4,5]);
 assert.ok(researchPriorities.every(x=>x.component.pt && x.component.en && x.question.pt && x.question.en && x.sourcePath.startsWith("https://github.com/igoroalonge/urna-vota-decompiled/blob/main/")));
});
test("four hypothetical fixtures are labeled in both languages",()=>{
 assert.deepEqual(Object.keys(scenarios).sort(),["controle","origem_comprometida","processamento_tardio","totalizador_divergente"].sort());
 assert.ok(Object.values(scenarios).every(x=>x.pt && x.en));
});
test("control reconciles but does not claim real crypto verification",()=>{
 const s=evaluateIntegrity("controle");
 assert.equal(aggregate(s.sectionBU),209);
 assert.equal(status(s,"BU_PUBLICADO_X_TOTALIZACAO"),"coerente");
 assert.equal(status(s,"REFERENCIA_EXTERNA_HIPOTETICA"),"nao_testado");
 assert.equal(status(s,"ASSINATURA_HASH_REAIS"),"nao_testado");
});
test("source divergence remains invisible to common-source consistency checks",()=>{
 const s=evaluateIntegrity("origem_comprometida");
 assert.ok(same(s.ledger,s.sectionBU));
 assert.ok(same(s.publishedBU,s.totalized));
 assert.equal(status(s,"LEDGER_X_BU"),"coerente");
 assert.equal(status(s,"BU_PUBLICADO_X_TOTALIZACAO"),"coerente");
 assert.equal(status(s,"REFERENCIA_EXTERNA_HIPOTETICA"),"divergente");
 assert.equal(status(s,"ASSINATURA_HASH_REAIS"),"nao_testado");
});
test("central mismatch is visible despite identical grand total",()=>{
 const s=evaluateIntegrity("totalizador_divergente");
 assert.equal(status(s,"BU_LOCAL_X_PUBLICADO"),"coerente");
 assert.equal(status(s,"BU_PUBLICADO_X_TOTALIZACAO"),"divergente");
 assert.equal(aggregate(s.sectionBU),aggregate(s.totalized));
 assert.ok(!same(s.sectionBU,s.totalized));
});
test("late receipt without count difference is not an integrity alert",()=>{
 const s=evaluateIntegrity("processamento_tardio");
 assert.ok(s.timeOfReceipt>s.timeOfBU);
 assert.equal(status(s,"BU_PUBLICADO_X_TOTALIZACAO"),"coerente");
});
test("invalid selection is rejected",()=>{assert.throws(()=>evaluateIntegrity("other"));});
