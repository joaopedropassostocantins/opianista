import test from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { firstMinute,lastMinute,hhmm,minuteOf,runSimulation,scenarioDescriptions } from "../src/lib/temporal-simulator.ts";

test("time boundaries are exact and malformed input is rejected",()=>{
  assert.equal(hhmm(minuteOf("17:00")),"17:00");
  assert.equal(hhmm(minuteOf("19:00")),"19:00");
  assert.throws(()=>minuteOf("19:61"));
  assert.throws(()=>minuteOf("19:00:01"));
  assert.throws(()=>runSimulation("regular",lastMinute+1));
  assert.equal(firstMinute,1015);
});

test("normal closing produces a consistent synthetic bulletin",()=>{
  assert.equal(runSimulation("regular",minuteOf("17:00")).bu,null);
  const post=runSimulation("regular",minuteOf("17:04"));
  assert.equal(post.state,"ENCERRADA");
  assert.equal(post.bu.total,207);
  assert.equal(post.checks[0].status,"ok");
  assert.equal(post.checks[1].status,"ok");
});

test("queue allows votes after 17h with no spurious alarm",()=>{
  const mid=runSimulation("fila",minuteOf("17:10"));
  assert.equal(mid.state,"CONTINUIDADE_FILA");
  assert.equal(mid.totals.B,100);
  const closed=runSimulation("fila",minuteOf("17:19"));
  assert.equal(closed.bu.total,209);
  assert.equal(closed.checks[0].status,"ok");
});

test("extension boundary at 19h is distinct from report generation",()=>{
  const mid=runSimulation("prorrogacao",minuteOf("18:59"));
  assert.equal(mid.state,"JANELA_EXCEPCIONAL");
  assert.equal(mid.bu,null);
  assert.equal(mid.totals.A,104);
  assert.equal(mid.totals.B,100);
  assert.equal(runSimulation("prorrogacao",minuteOf("19:00")).state,"JANELA_EXCEPCIONAL");
  const done=runSimulation("prorrogacao",minuteOf("19:06"));
  assert.equal(done.state,"ENCERRADA");
  assert.equal(done.bu.total,209);
  assert.equal(done.checks[0].status,"ok");
});

test("artificial log loss is detected without any claim about real machines",()=>{
  const a=runSimulation("prorrogacao",minuteOf("19:06"));
  const b=runSimulation("discordancia",minuteOf("19:06"));
  assert.deepEqual(a.bu,b.bu);
  assert.equal(b.logLines.length,a.logLines.length-1);
  assert.equal(b.checks.find(x=>x.id==="CONCILIACAO_LOG_BU").status,"alerta");
  assert.equal(b.checks.find(x=>x.id==="ARQUIVOS_ASSINATURA").status,"nao_avaliado");
  assert.ok(Object.values(scenarioDescriptions).every(s=>s.pt.length && s.en.length));
});

test("artificial event after closing is flagged and does not alter BU snapshot",()=>{
  const original=runSimulation("prorrogacao",minuteOf("19:07"));
  const altered=runSimulation("sequencia_invalida",minuteOf("19:07"));
  assert.equal(altered.bu.total,original.bu.total);
  assert.equal(altered.totals.B,original.totals.B+1);
  assert.equal(altered.checks.find(x=>x.id==="VOTO_APOS_ENCERRAMENTO").status,"alerta");
  assert.equal(altered.checks.find(x=>x.id==="CONTAGEM_BU_SINTETICO").status,"alerta");
  assert.equal(original.checks.find(x=>x.id==="CONTAGEM_BU_SINTETICO").status,"ok");
});

test("separate exploratory study is documented",()=>{
  assert.ok(existsSync(resolve("..","estudos/05_simulacao_temporal/README.md")));
  assert.ok(existsSync(resolve("..","estudos/05_simulacao_temporal/MATRIZ_VERIFICACAO.md")));
});
