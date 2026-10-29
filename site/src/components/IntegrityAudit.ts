import type { Language } from "../types/content.ts";
import { researchPriorities } from "../content/insider.ts";
import { evaluateIntegrity, aggregate, scenarios } from "../lib/integrity-model.ts";
import type { IntegrityScenario, VoteTotals } from "../lib/integrity-model.ts";
import { escapeHtml } from "../lib/formatters.ts";
import { githubFile } from "../lib/github-links.ts";

const labels={
  pt:{title:"O BU poderia nascer incorreto?",intro:"Comparador defensivo de origem e totalização. A simulação testa o poder de diferentes controles, não um método de ataque.",select:"Experimento hipotético",matrix:"O que cada registro consegue provar",risk:"Os dois pontos de falha em investigação",origin:"Antes de emitir o BU",central:"Depois de emitir o BU",priorities:"Cinco prioridades de auditoria do código",table:"Comparação entre registros fictícios",reference:"Referência externa de laboratório (hipotética)",ledger:"Registro de origem",local:"BU emitido na seção",published:"BU público",total:"Resultado atribuído à seção no totalizador",tests:"Testes independentes",limit:"Não existem votos reais, urnas conectadas, hashes ou assinaturas verificadas. A referência externa é uma variável artificial, não uma fonte de identificação do voto secreto. A extensão até 19h não ativa nenhuma vulnerabilidade neste laboratório.",open:"Ver código reconstruído",docs:"Protocolo e matriz de verificação",notTested:"Não testado",consistent:"Coerente",divergent:"Divergente",time:"Horários fictícios",votes:"Último voto / BU / recebimento"},
  en:{title:"Could the BU be incorrect when created?",intro:"Defensive comparison of origin and aggregation. The simulation tests the strength of independent controls, not an attack method.",select:"Hypothetical experiment",matrix:"What each record can prove",risk:"Two investigated failure domains",origin:"Before BU generation",central:"After BU generation",priorities:"Five code-review priorities",table:"Comparing fictional records",reference:"Hypothetical external laboratory reference",ledger:"Source record",local:"BU issued at the section",published:"Published BU",total:"Section result in central tally",tests:"Independent checks",limit:"There are no real votes, connected machines, verified hashes or signatures. The external reference is an invented variable, not a way to identify secret ballots. An extension to 7 p.m. does not activate a vulnerability in this laboratory.",open:"View reconstructed source",docs:"Protocol and verification matrix",notTested:"Not tested",consistent:"Consistent",divergent:"Different",time:"Fictional timestamps",votes:"Last vote / BU / receipt"}
};
function row(label:string,v:VoteTotals):string{
 return '<tr><th scope="row">'+escapeHtml(label)+'</th><td>'+v.A+'</td><td>'+v.B+'</td><td>'+v.BRANCO+'</td><td>'+v.NULO+'</td><td>'+aggregate(v)+'</td></tr>';
}
export function IntegrityAudit(lang:Language):string{
 const l=labels[lang];
 const options=(Object.keys(scenarios) as IntegrityScenario[]).map(id=>'<option value="'+id+'">'+escapeHtml(scenarios[id][lang])+'</option>').join("");
 const priorities=researchPriorities.map(p=>'<li class="priority-card"><span class="card-index">0'+p.number+'</span><div><h4>'+escapeHtml(p.component[lang])+'</h4><p>'+escapeHtml(p.question[lang])+'</p><small>'+escapeHtml(p.independentCheck[lang])+'</small><p class="priority-limitation">'+escapeHtml(p.limitation[lang])+'</p><a href="'+p.sourcePath+'" target="_blank" rel="noopener noreferrer">'+l.open+' ↗</a></div></li>').join("");
 return '<section class="section section-paper" id="auditoria-bu" aria-labelledby="audit-title"><div class="container"><div class="section-top"><p class="eyebrow">06 / INSIDER × BU × TOTALIZAÇÃO</p><h2 id="audit-title">'+l.title+'</h2><p>'+l.intro+'</p></div>'+
 '<div class="sim-alert" role="note"><strong>'+l.matrix+'</strong><p>'+l.limit+'</p></div>'+
 '<div class="risk-grid"><article><span class="card-index">A</span><h3>'+l.origin+'</h3><p>'+(lang==="pt"?"Se a origem computacional estiver comprometida antes de produzir o BU, vários registros derivados dela podem ser mutuamente coerentes e ainda assim não corresponder ao evento real. É uma possibilidade teórica, não um fato observado.":"Compromised source logic could yield mutually consistent records without reflecting the real event. This is a theoretical possibility, not an observed fact.")+'</p></article><article><span class="card-index">B</span><h3>'+l.central+'</h3><p>'+(lang==="pt"?"Uma divergência entre os BUs preservados e a totalização é verificável por soma independente. Recepção tardia não significa alteração de conteúdo.":"A mismatch between independently retained section BUs and the central tally can be found by independent addition. Late receipt does not imply changed content.")+'</p></article></div>'+
 '<div class="integrity-lab"><label for="integrity-scenario">'+l.select+'</label><select id="integrity-scenario">'+options+'</select>'+
 '<p id="integrity-times" class="mono-small"></p><div class="table-scroller" tabindex="0"><table class="integrity-table"><caption>'+l.table+'</caption><thead><tr><th scope="col">Origem</th><th scope="col">A</th><th scope="col">B</th><th scope="col">Brancos</th><th scope="col">Nulos</th><th scope="col">Total</th></tr></thead><tbody id="integrity-rows"></tbody></table></div>'+
 '<h3>'+l.tests+'</h3><ul id="integrity-checks" class="integrity-checks"></ul></div>'+
 '<h3 class="priority-title">'+l.priorities+'</h3><ol class="priorities">'+priorities+'</ol><p><a class="text-link" href="'+githubFile("estudos/05_simulacao_temporal/ANALISE_INSIDER_BU_TOTALIZACAO.md")+'" target="_blank" rel="noopener noreferrer">'+l.docs+' ↗</a></p></div></section>';
}
export function attachIntegrityAudit(lang:Language):void{
 const sel=document.querySelector<HTMLSelectElement>("#integrity-scenario");
 const tbody=document.querySelector<HTMLElement>("#integrity-rows");
 const list=document.querySelector<HTMLElement>("#integrity-checks");
 const time=document.querySelector<HTMLElement>("#integrity-times");
 if(!sel||!tbody||!list||!time)return;
 const l=labels[lang];
 const draw=()=>{
   const x=evaluateIntegrity(sel.value as IntegrityScenario);
   tbody.innerHTML=row(l.ledger,x.ledger)+row(l.local,x.sectionBU)+row(l.published,x.publishedBU)+row(l.total,x.totalized)
     +(x.independentHypothesis?row(l.reference,x.independentHypothesis):"");
   time.textContent=l.votes+": "+x.timeOfLastVote+" / "+x.timeOfBU+" / "+x.timeOfReceipt;
   list.innerHTML=x.audit.map(a=>'<li class="integrity-check '+a.status+'"><strong>'+escapeHtml(a.label)+'</strong><span>'+
      (a.status==="coerente"?l.consistent:a.status==="divergente"?l.divergent:l.notTested)+'</span><small>'+escapeHtml(a.note)+'</small></li>').join("");
 };
 sel.addEventListener("change",draw);
 draw();
}
