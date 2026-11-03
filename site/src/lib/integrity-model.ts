/**
 * Estudo 05 / ameaça insider: fixtures acadêmicas inteiramente sintéticas.
 *
 * NÃO processa arquivos de urna, não injeta instruções, não manipula assinaturas,
 * não reproduz algoritmos do TSE, e NÃO revela vetor para alterar votação real.
 *
 * A referência externa representa um experimento hipotético independente,
 * NÃO uma fonte disponível para conhecer o voto secreto do cidadão.
 */
export type IntegrityScenario = "controle" | "origem_comprometida" | "totalizador_divergente" | "processamento_tardio";
export type VoteTotals = Readonly<{ A:number; B:number; BRANCO:number; NULO:number }>;
export type IntegrityCheck = { id:string; label:string; status:"coerente"|"divergente"|"nao_testado"; note:string };
export interface IntegrityRun {
  scenario:IntegrityScenario;
  baseline:VoteTotals;
  ledger:VoteTotals;
  sectionBU:VoteTotals;
  publishedBU:VoteTotals;
  totalized:VoteTotals;
  independentHypothesis:VoteTotals | null;
  audit:IntegrityCheck[];
  timeOfLastVote:string;
  timeOfBU:string;
  timeOfReceipt:string;
}
export const scenarios:Record<IntegrityScenario,{pt:string;en:string}> = {
  controle:{pt:"Controle — todos os relatórios coincidem",en:"Control — reports match"},
  origem_comprometida:{pt:"Hipótese: registro de origem comprometido",en:"Hypothesis: compromised source records"},
  totalizador_divergente:{pt:"Hipótese: totalização diverge do BU",en:"Hypothesis: totals diverge from section BU"},
  processamento_tardio:{pt:"Recepção tardia sem alteração de votos",en:"Late processing without vote changes"}
};
const baseline:VoteTotals = {A:104,B:100,BRANCO:3,NULO:2};
// As diferenças abaixo são fixtures declarativas artificiais, não procedimentos
// para modificar arquivos, sistemas ou contadores de votação.
const fixture:Record<IntegrityScenario,{
  ledger:VoteTotals; sectionBU:VoteTotals; publishedBU:VoteTotals;
  totalized:VoteTotals; independentHypothesis:VoteTotals|null;
  timeOfLastVote:string; timeOfBU:string; timeOfReceipt:string;
}>={
  controle:{
    ledger:baseline,sectionBU:baseline,publishedBU:baseline,totalized:baseline,
    independentHypothesis:null,timeOfLastVote:"17:00",timeOfBU:"17:04",timeOfReceipt:"17:20"
  },
  origem_comprometida:{
    ledger:{A:102,B:102,BRANCO:3,NULO:2},
    sectionBU:{A:102,B:102,BRANCO:3,NULO:2},
    publishedBU:{A:102,B:102,BRANCO:3,NULO:2},
    totalized:{A:102,B:102,BRANCO:3,NULO:2},
    independentHypothesis:baseline,timeOfLastVote:"18:25",timeOfBU:"19:04",timeOfReceipt:"19:20"
  },
  totalizador_divergente:{
    ledger:baseline,sectionBU:baseline,publishedBU:baseline,
    totalized:{A:102,B:102,BRANCO:3,NULO:2},independentHypothesis:null,
    timeOfLastVote:"17:00",timeOfBU:"17:04",timeOfReceipt:"19:20"
  },
  processamento_tardio:{
    ledger:baseline,sectionBU:baseline,publishedBU:baseline,totalized:baseline,
    independentHypothesis:null,timeOfLastVote:"17:00",timeOfBU:"17:04",timeOfReceipt:"19:20"
  }
};
export function aggregate(t:VoteTotals):number{return t.A+t.B+t.BRANCO+t.NULO;}
export function same(a:VoteTotals,b:VoteTotals):boolean {
  return a.A===b.A && a.B===b.B && a.BRANCO===b.BRANCO && a.NULO===b.NULO;
}
export function evaluateIntegrity(scenario:IntegrityScenario):IntegrityRun {
  if(!Object.prototype.hasOwnProperty.call(fixture,scenario))throw new Error("Unknown fixture");
  const f=fixture[scenario];
  const audit:IntegrityCheck[]=[
    {id:"LEDGER_X_BU",label:"Registro interno × BU da seção",
      status:same(f.ledger,f.sectionBU)?"coerente":"divergente",
      note:"Coerência interna, mesmo quando registros derivam da mesma origem; não é prova de correção material."},
    {id:"BU_LOCAL_X_PUBLICADO",label:"BU da seção × BU publicado",
      status:same(f.sectionBU,f.publishedBU)?"coerente":"divergente",
      note:"Exige uma cópia independente do BU emitido e vínculo verificável à seção."},
    {id:"BU_PUBLICADO_X_TOTALIZACAO",label:"Soma independente dos BUs × totalização",
      status:same(f.publishedBU,f.totalized)?"coerente":"divergente",
      note:"O teste de uma seção é ilustrativo; na prática, somar todas as seções e reconciliar agregados."},
    {id:"REFERENCIA_EXTERNA_HIPOTETICA",label:"Referência independente hipotética × BU",
      status:f.independentHypothesis ? (same(f.independentHypothesis,f.sectionBU)?"coerente":"divergente"):"nao_testado",
      note:"A referência externa é inventada para fins pedagógicos. Não há observação disponível do voto secreto individual."},
    {id:"ASSINATURA_HASH_REAIS",label:"Assinaturas, certificados, RDV e hashes reais",
      status:"nao_testado",
      note:"Não são produzidos nem verificados por este modelo; requerem artefatos oficiais e verificador independente."}
  ];
  return {scenario,baseline, ...f,audit};
}
