import type { Language } from "../types/content.ts";
import { classify, clockDisagreements, declaredNationalCounts, fixtures, summarize, thresholdDisagreements, totalVotes } from "../lib/cohort-model.ts";
import type { ClosureClass,ClockBasis } from "../lib/cohort-model.ts";
import { escapeHtml } from "../lib/formatters.ts";
import { githubFile } from "../lib/github-links.ts";

export function LateClosureCohorts(lang:Language):string{
 const pt=lang==="pt";
 const titles={
  pt:{eyebrow:"07 / COORTES DE URNAS",title:"A urna é a unidade. Todos os votos entram na análise.",
   lead:"Não contabilizamos apenas votos após 17h. Selecionamos seções por horário de encerramento e examinamos o BU integral de cada seção. O relógio do próprio sistema não é tratado como fonte independente.",
   warning:"Laboratório 100% sintético. As dez seções F-01 a F-10 são fictícias; não representam eleições reais. O horário de fonte externa é igualmente fictício e serve somente para demonstrar o efeito de uma classificação por relógio não confiável.",
   group:"Limiar de encerramento",basis:"Fonte usada para classificar",late1710:"Após 17h10",late1900:"Após 19h",self:"Horário registrado internamente",ext:"Corroboração externa fictícia (somente subconjunto)",summary:"Total de votos de TODAS as seções selecionadas",
   sections:"Seções selecionadas",total:"Votos em todas essas seções",share:"Fração A / B dos votos válidos",unverified:"Seções sem relógio externo, excluídas desta visão",disagreement:"Seções que mudam de grupo conforme a origem do horário",
   table:"Verificação de cada seção (dados fictícios)",id:"Seção",logged:"Encerramento interno",external:"Encerramento externo",votes:"Todos os votos",a:"A",b:"B",status:"Classificação",unknown:"Sem validação",in:"Incluída",out:"Não incluída",reference:"Plano de investigação e critérios",data:"Números nacionais publicados pelo TSE: >17h: 497.333; >17h10: 24.268; >19h: 6.766 seções. Os números NÃO são votos e não representam quantos eleitores votaram após esses horários."},
  en:{eyebrow:"07 / LATE-CLOSING SECTIONS",title:"The section is the unit. Every vote is counted.",
   lead:"We do not analyze only post-5 p.m. votes. Sections are selected by their closing time and their entire bulletin is evaluated. The system's own clock is not an independent source.",
   warning:"100% fictional laboratory. All ten F-01–F-10 sections are invented and not election data. The external time reference is fictional, illustrating how an untrusted clock affects group assignment.",
   group:"Closing threshold",basis:"Source used for classification",late1710:"After 5:10 p.m.",late1900:"After 7 p.m.",self:"Internally recorded time",ext:"Fictional external corroboration (subset only)",summary:"All votes in ALL selected sections",sections:"Selected sections",total:"Votes in these sections",share:"A / B share of valid votes",unverified:"Sections without external timestamps, excluded",disagreement:"Sections reassigned when the time source changes",
   table:"Section-level audit (fictional data)",id:"Section",logged:"Internal closing time",external:"External closing time",votes:"All votes",a:"A",b:"B",status:"Classification",unknown:"Unverified",in:"Included",out:"Not included",reference:"Study plan and criteria",data:"TSE national counts: >5 p.m.: 497,333; >5:10 p.m.: 24,268; >7 p.m.: 6,766 sections. These counts are NOT votes nor the number of post-threshold voters."}
 }[lang];
 return '<section id="coortes" class="section section-cohort" aria-labelledby="cohort-title"><div class="container"><div class="section-top"><p class="eyebrow">'+titles.eyebrow+'</p><h2 id="cohort-title">'+titles.title+'</h2><p>'+titles.lead+'</p></div>'+
 '<aside class="sim-alert" role="note"><strong>'+(pt?"DADOS FICTÍCIOS":"FICTIONAL DATA")+'</strong><p>'+titles.warning+'</p></aside>'+
 '<p class="cohort-national">'+titles.data+' <a href="'+declaredNationalCounts.source+'" target="_blank" rel="noopener noreferrer">'+(pt?"Fonte: TSE":"Source: TSE")+' ↗</a></p>'+
 '<div class="cohort-controls"><label for="cohort-threshold">'+titles.group+'</label><select id="cohort-threshold"><option value="depois1710">'+titles.late1710+'</option><option value="depois1900" selected>'+titles.late1900+'</option></select>'+
 '<label for="cohort-basis">'+titles.basis+'</label><select id="cohort-basis"><option value="autodeclarado">'+titles.self+'</option><option value="externo">'+titles.ext+'</option></select></div>'+
 '<div class="cohort-cards"><div><small>'+titles.sections+'</small><strong id="cohort-count">0</strong></div><div><small>'+titles.total+'</small><strong id="cohort-total">0</strong></div><div><small>'+titles.share+'</small><strong id="cohort-share">—</strong></div><div><small>'+titles.unverified+'</small><strong id="cohort-unverified">0</strong></div></div>'+
 '<p class="cohort-discrepancy">'+titles.disagreement+': <strong id="cohort-reassignment">—</strong></p>'+
 '<div class="table-scroller" tabindex="0"><table class="cohort-table"><caption>'+titles.table+'</caption><thead><tr><th scope="col">'+titles.id+'</th><th scope="col">'+titles.logged+'</th><th scope="col">'+titles.external+'</th><th scope="col">'+titles.votes+'</th><th scope="col">'+titles.a+'</th><th scope="col">'+titles.b+'</th><th scope="col">'+titles.status+'</th></tr></thead><tbody id="cohort-rows"></tbody></table></div>'+
 '<p class="cohort-foot"><a href="'+githubFile("estudos/05_simulacao_temporal/COORTES_HORARIO_NAO_CONFIAVEL.md")+'" target="_blank" rel="noopener noreferrer">'+titles.reference+' ↗</a></p></div></section>';
}
export function attachLateClosureCohorts(lang:Language):void{
 const threshold=document.querySelector<HTMLSelectElement>("#cohort-threshold");
 const basis=document.querySelector<HTMLSelectElement>("#cohort-basis");
 const tbody=document.querySelector<HTMLElement>("#cohort-rows");
 if(!threshold||!basis||!tbody)return;
 const pt=lang==="pt";
 const set=(id:string,value:string)=>{const node=document.getElementById(id);if(node)node.textContent=value;};
 const percent=(value:number|null)=>value===null?"—":(value*100).toFixed(1).replace(".",pt?",":".")+"%";
 const draw=()=>{
   const group=threshold.value as ClosureClass,clock=basis.value as ClockBasis;
   const data=summarize(fixtures,group,clock);
   set("cohort-count",data.includedSections+" / "+data.classifiedSections);
   set("cohort-total",data.allVotes.toLocaleString(pt?"pt-BR":"en-US"));
   set("cohort-share",percent(data.shareA)+" / "+percent(data.shareB));
   set("cohort-unverified",String(data.unverifiedSections));
   set("cohort-reassignment",thresholdDisagreements(fixtures,group).join(", ")||(pt?"Nenhuma":"None"));
   tbody.innerHTML=fixtures.map(s=>{
     const state=classify(s,group,clock);
     const label=state==="incluir"?(pt?"Incluída":"Included"):state==="excluir"?(pt?"Fora":"Excluded"):(pt?"Sem validação":"Unverified");
     return '<tr><th scope="row">'+escapeHtml(s.id)+'</th><td>'+s.recordedClose+'</td><td>'+(s.externalClose??"—")+'</td><td>'+totalVotes(s.votes)+'</td><td>'+s.votes.A+'</td><td>'+s.votes.B+'</td><td><span class="cohort-status '+state+'">'+label+'</span></td></tr>';
   }).join("");
 };
 threshold.addEventListener("change",draw);basis.addEventListener("change",draw);
 draw();
}
