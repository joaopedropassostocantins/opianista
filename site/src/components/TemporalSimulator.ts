import type { Language } from "../types/content.ts";
import { githubFile } from "../lib/github-links.ts";
import { escapeHtml } from "../lib/formatters.ts";
import { firstMinute,hhmm,lastMinute,runSimulation,scenarioDescriptions } from "../lib/temporal-simulator.ts";
import type { Scenario } from "../lib/temporal-simulator.ts";

export function TemporalSimulator(lang:Language):string {
  const labels = {
    pt:{tag:"05 / LABORATÓRIO TEMPORAL",title:"Entre 17h e 19h: o que os registros mostram?",lead:"Explore a sequência hipotética de eventos, logs e Boletim de Urna. Os dados são inteiramente fictícios; o modelo não executa a urna real nem reproduz seu código-fonte.",scenario:"Cenário de teste",minute:"Momento observado (horário de Brasília)",state:"Estado",events:"Eventos da seção",logs:"Log ilustrativo",report:"BU sintético / resumo",check:"Verificações",source:"Metodologia e critérios",warning:"Simulação independente, não perícia",caption:"A reconstrução pública do VOTA identifica componentes de horário e geração de BU, mas não comprova o comportamento do binário lacrado. Nenhuma lacuna de segurança após 17h ou 19h foi demonstrada por este simulador."},
    en:{tag:"05 / TEMPORAL LAB",title:"Between 5 p.m. and 7 p.m.: what can records show?",lead:"Explore hypothetical events, logs and section reports. All data are fictional; this model neither executes the real voting machine nor reproduces its source.",scenario:"Test scenario",minute:"Observed time (Brasília time)",state:"State",events:"Section events",logs:"Illustrative log",report:"Synthetic bulletin / summary",check:"Checks",source:"Methodology and criteria",warning:"Independent simulation, not forensics",caption:"A public VOTA reconstruction describes time-control and report-generation components, but does not establish behavior of the sealed election executable. This simulator demonstrates no vulnerability after 5 p.m. or 7 p.m."}
  }[lang];
  const options=(Object.keys(scenarioDescriptions) as Scenario[]).map(id=>'<option value="'+id+'">'+escapeHtml(scenarioDescriptions[id][lang])+'</option>').join("");
  return '<section class="section section-lab" id="simulador" aria-labelledby="simulator-title"><div class="container">' +
    '<div class="section-top"><p class="eyebrow">'+labels.tag+'</p><h2 id="simulator-title">'+labels.title+'</h2><p>'+labels.lead+'</p></div>' +
    '<div class="sim-alert" role="note"><strong>'+labels.warning+'</strong><p>'+labels.caption+'</p></div>' +
    '<div class="sim-controls"><label for="sim-scenario">'+labels.scenario+'</label><select id="sim-scenario">'+options+'</select>' +
    '<label for="sim-time">'+labels.minute+'</label><div class="sim-slider-row"><input id="sim-time" type="range" min="'+firstMinute+'" max="'+lastMinute+'" step="1" value="'+firstMinute+'" aria-describedby="sim-time-value"><output id="sim-time-value" for="sim-time">16:55</output></div>' +
    '<div class="sim-presets"><button type="button" data-time="16:59">16:59</button><button type="button" data-time="17:00">17:00</button><button type="button" data-time="17:03">17:03</button><button type="button" data-time="18:59">18:59</button><button type="button" data-time="19:00">19:00</button><button type="button" data-time="19:06">19:06</button></div>' +
    '</div><div class="sim-state">'+labels.state+': <strong id="sim-state" aria-live="polite">ABERTA</strong></div>' +
    '<div class="sim-grid"><article class="sim-panel"><h3>'+labels.events+'</h3><ol id="sim-events" class="sim-timeline"></ol></article>' +
    '<article class="sim-panel"><h3>'+labels.logs+'</h3><pre id="sim-logs" tabindex="0" class="sim-logs"></pre></article>' +
    '<article class="sim-panel"><h3>'+labels.report+'</h3><div id="sim-bu"></div></article>' +
    '<article class="sim-panel"><h3>'+labels.check+'</h3><ul id="sim-checks" class="sim-checks"></ul></article></div>' +
    '<p class="sim-footnote"><a href="'+githubFile("estudos/05_simulacao_temporal/README.md")+'" target="_blank" rel="noopener noreferrer">'+labels.source+' ↗</a></p>' +
    '</div></section>';
}
export function attachTemporalSimulator(lang:Language):void {
  const select=document.querySelector<HTMLSelectElement>("#sim-scenario");
  const slider=document.querySelector<HTMLInputElement>("#sim-time");
  if(!select || !slider)return;
  const stateNode=document.querySelector<HTMLElement>("#sim-state")!;
  const timeline=document.querySelector<HTMLOListElement>("#sim-events")!;
  const log=document.querySelector<HTMLElement>("#sim-logs")!;
  const bu=document.querySelector<HTMLElement>("#sim-bu")!;
  const checks=document.querySelector<HTMLElement>("#sim-checks")!;
  const time=document.querySelector<HTMLOutputElement>("#sim-time-value")!;
  const draw=()=>{
    const scenario=select.value as Scenario;
    const minute=Number(slider.value);
    const model=runSimulation(scenario,minute);
    time.value=hhmm(minute);
    stateNode.textContent=model.state;
    timeline.innerHTML=model.displayEvents.map(e=>'<li><time>'+hhmm(e.minute)+'</time><div><strong>'+escapeHtml(e.title)+'</strong><small>'+escapeHtml(e.details)+'</small></div></li>').join("");
    log.textContent=model.logLines.join("\n") || (lang==="pt"?"Ainda sem eventos":"No events yet");
    const countRows=[["A",model.bu?.votes.A],["B",model.bu?.votes.B],["BRANCO",model.bu?.votes.BRANCO],["NULO",model.bu?.votes.NULO]]
      .map(([k,v])=>'<tr><th scope="row">'+k+'</th><td>'+(v??"—")+'</td></tr>').join("");
    bu.innerHTML='<p class="sim-notice">'+(lang==="pt"?"RELATÓRIO FICTÍCIO • SEM VALOR ELEITORAL":"FICTIONAL REPORT • NOT ELECTION DATA")+'</p>' +
      '<table class="sim-report"><tbody>'+countRows+'</tbody></table><p><strong>'+(lang==="pt"?"Total":"Total")+
      ': '+(model.bu?.total??"—")+'</strong></p><small>'+(
        model.bu ? ((lang==="pt"?"BU simulado às ":"Simulated report at ")+hhmm(model.bu.minute)) :
        (lang==="pt"?"Relatório disponível apenas após o encerramento.":"Report available only after closing.")
      )+'</small>';
    checks.innerHTML=model.checks.map(c=>'<li class="sim-check '+c.status+'"><strong>'+escapeHtml(c.id)+'</strong><span>'+(
      c.status==="ok"?(lang==="pt"?"Sem alerta":"No alert"):c.status==="alerta"?(lang==="pt"?"Alerta sintético":"Synthetic alert"):(lang==="pt"?"Não avaliado":"Not assessed")
    )+'</span><small>'+escapeHtml(c.explanation)+'</small></li>').join("");
  };
  select.addEventListener("change",draw);
  slider.addEventListener("input",draw);
  document.querySelectorAll<HTMLButtonElement>(".sim-presets button").forEach(b=>{
    b.addEventListener("click",()=>{const t=b.dataset.time;if(!t)return; const [h,m]=t.split(":").map(Number);slider.value=String(h*60+m);draw();slider.focus();});
  });
  draw();
}
