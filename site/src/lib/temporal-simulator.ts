/**
 * Estudo 05: modelo DIDÁTICO determinístico e sintético de eventos de seção.
 * NÃO executa, reproduz nem valida o binário de produção do TSE ou a build WASM.
 * Relatórios e linhas de log são inventados para exercitar consistência.
 */
export type Scenario = "regular" | "fila" | "prorrogacao" | "discordancia" | "sequencia_invalida";
export type EventKind = "situacao" | "fila" | "extensao" | "voto" | "fechamento" | "bu" | "relatorio" | "verificacao" | "sistema";
export interface ModelEvent {
  minute: number;
  kind: EventKind;
  title: string;
  details: string;
  log: boolean;
  vote?: "A" | "B" | "BRANCO" | "NULO";
}
export interface AuditCheck {
  id: string;
  status: "ok" | "alerta" | "nao_avaliado";
  explanation: string;
}
export interface SimulationState {
  scenario: Scenario;
  minute: number;
  events: ModelEvent[];
  displayEvents: ModelEvent[];
  state: "ABERTA" | "CONTINUIDADE_FILA" | "JANELA_EXCEPCIONAL" | "ENCERRANDO" | "ENCERRADA";
  logLines: string[];
  totals: Record<"A" | "B" | "BRANCO" | "NULO", number>;
  bu: null | { minute: number; total: number; votes: Record<"A" | "B" | "BRANCO" | "NULO", number> };
  checks: AuditCheck[];
}

export const firstMinute = 16 * 60 + 55;
export const lastMinute = 19 * 60 + 15;
export function minuteOf(time: string): number {
  const match = /^(\d{2}):(\d{2})$/.exec(time);
  if (!match) throw new Error("Invalid time");
  const hours = Number(match[1]), minutes = Number(match[2]);
  if (hours > 23 || minutes > 59) throw new Error("Invalid time");
  return hours * 60 + minutes;
}
export function hhmm(minute: number): string {
  if (!Number.isInteger(minute) || minute < 0 || minute >= 24 * 60) throw new Error("Invalid minute");
  return String(Math.floor(minute / 60)).padStart(2,"0") + ":" + String(minute % 60).padStart(2,"0");
}
function ev(time: string, kind: EventKind, title: string, details: string, log = true, vote?: ModelEvent["vote"]): ModelEvent {
  return { minute: minuteOf(time), kind, title, details, log, vote };
}
const baseEvents: ModelEvent[] = [
  ev("16:55", "situacao", "Seção em funcionamento", "Marco inicial fictício: 206 votos confirmados anteriormente (102 A, 99 B, 3 brancos, 2 nulos)."),
  ev("16:58", "sistema", "Habilitação de eleitor", "Registro demonstrativo, sem informação pessoal."),
  ev("16:59", "voto", "Voto concluído", "Voto fictício para A, contabilizado.", true, "A"),
  ev("17:00", "situacao", "Chegada ao limite regular", "A continuidade depende da fila e, se aplicável, de decisão excepcional.")
];

const regular: ModelEvent[] = [
  ev("17:01","fechamento","Encerramento iniciado","Sem fila e sem extensão neste cenário."),
  ev("17:02","bu","BU elaborado","Totais derivados dos votos fictícios até o encerramento."),
  ev("17:03","relatorio","Relatório e arquivos preparados","Eventos de relatório sintéticos; não representam bytes de arquivos oficiais."),
  ev("17:04","verificacao","Conferência didática","Comparação interna entre eventos do modelo, log e BU.")
];
const fila: ModelEvent[] = [
  ev("17:00","fila","Senhas distribuídas","Duas pessoas já estavam na fila às 17h."),
  ev("17:06","voto","Voto concluído — fila","Pessoa com senha já presente às 17h.",true,"B"),
  ev("17:12","voto","Voto concluído — fila","Última pessoa com senha.",true,"A"),
  ev("17:15","fechamento","Encerramento iniciado","Fila hipotética concluída."),
  ev("17:16","bu","BU elaborado","Totais após os últimos votantes."),
  ev("17:18","relatorio","Relatório e arquivos preparados","Sequência de finalização didática."),
  ev("17:19","verificacao","Conferência didática","Conciliação de contagem.")
];
const extension: ModelEvent[] = [
  ev("17:03","extensao","Continuidade excepcional autorizada","Premissa do cenário: decisão válida até as 19h, aplicável à seção ainda em funcionamento."),
  ev("17:10","voto","Voto concluído","Voto fictício na janela excepcional.",true,"B"),
  ev("18:25","voto","Voto concluído","Voto fictício na janela excepcional.",true,"A"),
  ev("19:00","situacao","Marco final da janela excepcional","Hora-limite hipotética; procedimentos de encerramento podem ocorrer depois."),
  ev("19:02","fechamento","Encerramento iniciado","Não há novos votos nesta simulação após o fim da janela."),
  ev("19:04","bu","BU elaborado","Totalização da seção fictícia."),
  ev("19:05","relatorio","Relatório e arquivos preparados","Gerados após encerrar a recepção dos votos."),
  ev("19:06","verificacao","Conferência didática","Conciliação final.")
];
// Falha artificial: registro sintético de um evento foi omitido no log demonstrativo.
// NÃO reproduz mecanismo de urna nem demonstra adulteração real.
const discrepancy: ModelEvent[] = extension.map(e =>
  e.minute === minuteOf("18:25") && e.kind === "voto"
    ? {...e, log:false, details:"Evento contabilizado no modelo, mas linha didática foi suprimida para testar a auditoria."}
    : e
);
const postClosing: ModelEvent[] = [...extension, ev("19:07","voto","Evento de voto pós-fechamento (injetado pelo simulador)","Anomalia proposital em um modelo fictício; não descreve comportamento de urna real.",true,"B")];
const scenarioTail: Record<Scenario, ModelEvent[]> = { regular, fila, prorrogacao:extension, discordancia:discrepancy, sequencia_invalida:postClosing };
export const scenarioDescriptions: Record<Scenario, { pt:string; en:string }> = {
  regular: {pt:"17h: sem fila e encerramento regular", en:"5 p.m.: no queue, normal closing"},
  fila: {pt:"Fila com senhas: votos após 17h", en:"Queue with tickets: votes after 5 p.m."},
  prorrogacao: {pt:"Extensão excepcional até 19h", en:"Exceptional extension to 7 p.m."},
  discordancia: {pt:"Extensão com lacuna artificial de log", en:"Extension with artificial log gap"},
  sequencia_invalida: {pt:"Evento artificial depois do encerramento", en:"Artificial event after closing"}
};

const initial = { A:102, B:99, BRANCO:3, NULO:2 } as const;
const total = (votes:Record<"A"|"B"|"BRANCO"|"NULO",number>):number => votes.A+votes.B+votes.BRANCO+votes.NULO;
export function runSimulation(scenario:Scenario, minute:number):SimulationState {
  if (!Object.hasOwn(scenarioTail,scenario)) throw new Error("Unknown scenario");
  if (!Number.isInteger(minute) || minute<firstMinute || minute>lastMinute) throw new Error("Invalid simulation minute");
  const events=[...baseEvents,...scenarioTail[scenario]].sort((a,b)=>a.minute-b.minute);
  const displayEvents=events.filter(x=>x.minute<=minute);
  const votes: Record<"A"|"B"|"BRANCO"|"NULO",number> = {...initial};
  for(const e of displayEvents){if(e.kind==="voto" && e.vote) votes[e.vote]++;}
  const close=displayEvents.find(e=>e.kind==="fechamento");
  const buEvent=displayEvents.find(e=>e.kind==="bu");
  const loggedVotes=displayEvents.filter(e=>e.kind==="voto" && e.log).length;
  const votedAfterStart=displayEvents.filter(e=>e.kind==="voto").length;
  // Snapshot: o relatório não se modifica retroativamente quando o modelo recebe evento posterior.
  const votesAtBu: Record<"A"|"B"|"BRANCO"|"NULO",number> = {...initial};
  if(buEvent) for(const e of displayEvents){if(e.kind==="voto" && e.vote && e.minute<=buEvent.minute)votesAtBu[e.vote]++;}
  const bu=buEvent ? {minute:buEvent.minute,total:total(votesAtBu),votes:{...votesAtBu}} : null;
  const closed=Boolean(displayEvents.find(e=>e.kind==="verificacao"));
  const hasExtension=displayEvents.some(e=>e.kind==="extensao");
  let state:SimulationState["state"]="ABERTA";
  if(scenario==="fila" && minute>=minuteOf("17:00") && !close)state="CONTINUIDADE_FILA";
  if((scenario==="prorrogacao" || scenario==="discordancia" || scenario==="sequencia_invalida") && hasExtension && !close)state="JANELA_EXCEPCIONAL";
  if(close)state=closed?"ENCERRADA":"ENCERRANDO";
  const logLines=displayEvents.filter(e=>e.log).map(e=>"["+hhmm(e.minute)+":00] SIM|"+e.kind.toUpperCase()+"|"+e.title);
  const checks:AuditCheck[]=[
    {id:"CONCILIACAO_LOG_BU",status:bu ? (loggedVotes===votedAfterStart?"ok":"alerta"):"nao_avaliado",
      explanation:bu?(loggedVotes===votedAfterStart?"Correspondência no contrato didático 1 evento = 1 linha. Não se deve presumir esse contrato nos logs oficiais.":"A lacuna artificial foi detectada. Não é evidência de falha ou fraude da urna real."):"Aguardando elaboração do BU no cenário."},
    {id:"VOTO_APOS_ENCERRAMENTO",status:close ? (displayEvents.some(e=>e.kind==="voto" && e.minute>=close.minute)?"alerta":"ok"):"nao_avaliado",
      explanation:close?"Checagem de ordem temporal em eventos sintéticos.":"Encerramento ainda não iniciado."},
    {id:"CONTAGEM_BU_SINTETICO",status:bu?(total(votes)===bu.total?"ok":"alerta"):"nao_avaliado",
      explanation:bu?(total(votes)===bu.total?"O relatório fictício coincide com o total do modelo no momento exibido.":"Evento artificial posterior à elaboração do BU gera diferença no modelo. Não representa urna real."):"Sem relatório, comparação não aplicável."},
    {id:"LIMITE_HORARIO",status:displayEvents.some(e=>e.kind==="voto" && e.minute>minuteOf("17:00") && scenario==="regular")?"alerta":"ok",
      explanation:"Votos após 17h exigem contexto normativo: fila já existente ou autorização excepcional; horário isolado não demonstra irregularidade."},
    {id:"ARQUIVOS_ASSINATURA",status:"nao_avaliado",explanation:"O simulador não gera BU, RDV nem assinaturas criptográficas reais; hashes e assinaturas devem ser avaliados em documentos oficiais."}
  ];
  return {scenario,minute,events,displayEvents,state,logLines,totals:votes,bu,checks};
}
