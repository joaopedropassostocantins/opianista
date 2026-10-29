/**
 * Estudo 05 — demonstração DIDÁTICA por COORTE de seções.
 * A unidade é a seção, e o desfecho inclui TODOS os seus votos.
 * Sem arquivo eleitoral real, relógio adulterado nem hipótese demonstrada.
 * Todas as entradas são explicitamente sintéticas.
 */
export type ClosureClass = "depois1710" | "depois1900";
export type ClockBasis = "autodeclarado" | "externo";
export type VoteSet = Readonly<{ A:number; B:number; branco:number; nulo:number }>;
export interface SectionFixture {
  id: string;
  uf: string;
  municipality: string;
  eligible:number;
  votes:VoteSet;
  // horário informado pelo registro interno (hipotético), sujeito a incerteza
  recordedClose:string;
  // Hora de encerramento registrada por fonte externa fictícia; nem toda seção dispõe dela
  externalClose?:string;
  // Uma seção continua no grupo mesmo que todos os votos tenham sido emitidos antes de 17h
  note:string;
}
export interface GroupSummary {
  totalSections:number;
  classifiedSections:number;
  includedSections:number;
  unverifiedSections:number;
  allVotes:number;
  validVotes:number;
  votesA:number;
  votesB:number;
  shareA:number|null;
  shareB:number|null;
  turnout:number|null;
  cohortIds:string[];
}
export const declaredNationalCounts = {
  date:"2026-10-28",
  after17:497333,
  after1710:24268,
  after19:6766,
  source:"https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/eleicoes-2026-mais-de-34-mil-votos-foram-registrados-apos-as-17h-no-2o-turno"
} as const;

export const fixtures:SectionFixture[]=[
 {id:"F-01",uf:"UF-X",municipality:"M-A",eligible:390,votes:{A:128,B:159,branco:4,nulo:5},recordedClose:"17:04",externalClose:"17:05",note:"Encerramento próximo do limite regular."},
 {id:"F-02",uf:"UF-X",municipality:"M-A",eligible:398,votes:{A:142,B:151,branco:5,nulo:2},recordedClose:"17:09",externalClose:"17:10",note:"Nenhum voto tardio necessário para compor os totais."},
 {id:"F-03",uf:"UF-X",municipality:"M-A",eligible:385,votes:{A:152,B:132,branco:3,nulo:4},recordedClose:"17:12",externalClose:"17:13",note:"Cohorte após 17h10: o BU representa toda a seção."},
 {id:"F-04",uf:"UF-X",municipality:"M-B",eligible:400,votes:{A:168,B:124,branco:3,nulo:5},recordedClose:"17:40",externalClose:"17:41",note:"Diferença de horário não determina o motivo do fechamento."},
 {id:"F-05",uf:"UF-X",municipality:"M-B",eligible:392,votes:{A:137,B:154,branco:3,nulo:5},recordedClose:"18:20",note:"Sem comprovação externa: classificação indeterminada na visão rigorosa."},
 {id:"F-06",uf:"UF-X",municipality:"M-B",eligible:405,votes:{A:185,B:110,branco:6,nulo:4},recordedClose:"19:05",externalClose:"19:06",note:"Encerramento relatado após 19h; todos os votos contam na coorte."},
 {id:"F-07",uf:"UF-X",municipality:"M-A",eligible:410,votes:{A:140,B:160,branco:5,nulo:7},recordedClose:"19:21",note:"Classificação externa não confirmada: não extrapolar."},
 {id:"F-08",uf:"UF-X",municipality:"M-A",eligible:385,votes:{A:165,B:115,branco:6,nulo:4},recordedClose:"17:07",externalClose:"19:08",note:"DISCORDÂNCIA ARTIFICIAL: horário interno fictício 17h07, referência externa fictícia 19h08."},
 {id:"F-09",uf:"UF-X",municipality:"M-B",eligible:400,votes:{A:130,B:164,branco:2,nulo:6},recordedClose:"17:03",externalClose:"17:04",note:"Controle fictício: encerramento próximo do limite."},
 {id:"F-10",uf:"UF-X",municipality:"M-B",eligible:401,votes:{A:160,B:129,branco:4,nulo:5},recordedClose:"19:09",externalClose:"19:10",note:"Outra seção fictícia após 19h, sem inferir motivo."}
];
export function hhmmMinutes(value:string):number{
 const match=/^(\d{2}):(\d{2})$/.exec(value);
 if(!match)throw new Error("HH:mm esperado");
 const h=Number(match[1]),m=Number(match[2]);
 if(h>23||m>59)throw new Error("Hora inválida");
 return h*60+m;
}
export function totalVotes(v:VoteSet):number {return v.A+v.B+v.branco+v.nulo;}
function threshold(group:ClosureClass):number{return group==="depois1710"?hhmmMinutes("17:10"):hhmmMinutes("19:00");}
export function classify(section:SectionFixture,group:ClosureClass,basis:ClockBasis):"incluir"|"excluir"|"indeterminado"{
 const stamp=basis==="externo"?section.externalClose:section.recordedClose;
 if(!stamp)return "indeterminado";
 return hhmmMinutes(stamp)>threshold(group)?"incluir":"excluir";
}
export function summarize(sections:readonly SectionFixture[],group:ClosureClass,basis:ClockBasis):GroupSummary{
 let includedSections=0,classifiedSections=0,unverifiedSections=0,allVotes=0,validVotes=0,votesA=0,votesB=0,eligible=0;
 const cohortIds:string[]=[];
 for(const section of sections){
   const status=classify(section,group,basis);
   if(status==="indeterminado"){unverifiedSections++;continue;}
   classifiedSections++;
   if(status!=="incluir")continue;
   includedSections++;
   cohortIds.push(section.id);
   votesA+=section.votes.A;votesB+=section.votes.B;
   validVotes+=section.votes.A+section.votes.B;
   allVotes+=totalVotes(section.votes);
   eligible+=section.eligible;
 }
 return {totalSections:sections.length,classifiedSections,includedSections,unverifiedSections,
 allVotes,validVotes,votesA,votesB,shareA:validVotes?votesA/validVotes:null,shareB:validVotes?votesB/validVotes:null,
 turnout:eligible?allVotes/eligible:null,cohortIds};
}
export function clockDisagreements(sections:readonly SectionFixture[]):string[]{
 return sections.filter(x=>x.externalClose && x.externalClose!==x.recordedClose).map(x=>x.id);
}
export function thresholdDisagreements(sections:readonly SectionFixture[],group:ClosureClass):string[]{
 return sections.filter(x=>x.externalClose && classify(x,group,"externo")!==classify(x,group,"autodeclarado")).map(x=>x.id);
}
/**
 * Materialidade: fração mínima dos votos válidos de uma coorte que precisaria
 * ser transferida de um candidato ao outro para inverter a margem nacional.
 * Cada voto transferido altera a margem em 2. Fração > 1 = impossível dentro da coorte.
 * O tamanho médio da seção é ESTIMATIVA (votos válidos / seções informadas), não dado por seção.
 */
export const officialResult2T2026 = {
  validVotes:64256232+59826041,
  margin:4430191,
  source:"protocolos/00_prompt_preregistro_original_20261026.md"
} as const;
export interface MaterialityBound { sections:number; validVotesPerSection:number; cohortValidVotes:number; maxMarginShift:number; minFlipFraction:number; canOverturn:boolean; }
export function materiality(sections:number,validVotesPerSection:number,margin:number=officialResult2T2026.margin):MaterialityBound{
 if(!Number.isInteger(sections)||sections<0||!(validVotesPerSection>0)||!(margin>0))throw new Error("Parâmetros inválidos");
 const cohortValidVotes=Math.round(sections*validVotesPerSection);
 const maxMarginShift=2*cohortValidVotes;
 const minFlipFraction=cohortValidVotes?margin/maxMarginShift:Infinity;
 return {sections,validVotesPerSection,cohortValidVotes,maxMarginShift,minFlipFraction,canOverturn:minFlipFraction<=1};
}
/** Média nacional aproximada; 497.333 é limite inferior do total de seções, logo a média é limite superior. */
export const nationalValidVotesPerSection=officialResult2T2026.validVotes/declaredNationalCounts.after17;

export function verifyFixture():void{
 const ids=new Set<string>();
 for(const s of fixtures){
   if(ids.has(s.id))throw new Error("Seção duplicada");
   ids.add(s.id);
   if(totalVotes(s.votes)>s.eligible)throw new Error("Comparecimento excede aptos");
   if(Object.values(s.votes).some(n=>!Number.isInteger(n)||n<0))throw new Error("Voto negativo");
   hhmmMinutes(s.recordedClose);
   if(s.externalClose)hhmmMinutes(s.externalClose);
 }
}
verifyFixture();
