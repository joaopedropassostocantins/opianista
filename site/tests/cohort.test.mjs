import test from "node:test";
import assert from "node:assert/strict";
import {classify,clockDisagreements,declaredNationalCounts,fixtures,hhmmMinutes,summarize,thresholdDisagreements,totalVotes} from "../src/lib/cohort-model.ts";

test("national reference is section counts, not a count of votes",()=>{
 assert.equal(declaredNationalCounts.after17,497333);
 assert.equal(declaredNationalCounts.after1710,24268);
 assert.equal(declaredNationalCounts.after19,6766);
 assert.ok(declaredNationalCounts.after17>declaredNationalCounts.after1710);
});
test("selected cohorts include ALL section votes, not only late votes",()=>{
 const group=summarize(fixtures,"depois1900","autodeclarado");
 assert.equal(group.includedSections,3);
 assert.deepEqual(group.cohortIds,["F-06","F-07","F-10"]);
 const sum=fixtures.filter(f=>group.cohortIds.includes(f.id)).reduce((a,s)=>a+totalVotes(s.votes),0);
 assert.equal(group.allVotes,sum);
 assert.equal(group.validVotes,group.votesA+group.votesB);
});
test("observed external record may classify section differently than an internal timestamp",()=>{
 assert.equal(classify(fixtures.find(s=>s.id==="F-08"),"depois1900","autodeclarado"),"excluir");
 assert.equal(classify(fixtures.find(s=>s.id==="F-08"),"depois1900","externo"),"incluir");
 assert.deepEqual(thresholdDisagreements(fixtures,"depois1900"),["F-08"]);
 assert.ok(clockDisagreements(fixtures).includes("F-08"));
});
test("no external evidence means indeterminate status, NOT section exclusion from the election",()=>{
 const internal=summarize(fixtures,"depois1900","autodeclarado");
 const external=summarize(fixtures,"depois1900","externo");
 assert.equal(external.unverifiedSections,2);
 assert.equal(external.includedSections,3);
 assert.equal(internal.includedSections,3);
 assert.notDeepEqual(internal.cohortIds,external.cohortIds);
 assert.equal(internal.totalSections,10);
});
test("exact boundary is excluded from strict after group",()=>{
 assert.equal(classify(fixtures.find(s=>s.id==="F-02"),"depois1710","externo"),"excluir");
 assert.equal(hhmmMinutes("17:10"),1030);
 assert.throws(()=>hhmmMinutes("25:00"));
});
test("fictional outcome never encodes voter identity",()=>{
 assert.ok(fixtures.every(s=>!Object.keys(s).includes("cpf")&&!Object.keys(s).includes("electorID")));
});
