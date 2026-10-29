import type { Localized } from "../types/content.ts";

export interface ResearchPriority {
  number:number;
  component:Localized;
  question:Localized;
  sourcePath:string;
  independentCheck:Localized;
  limitation:Localized;
}
const prefix="https://github.com/igoroalonge/urna-vota-decompiled/blob/main/";
export const researchPriorities:ResearchPriority[]=[
  {
    number:1,component:{pt:"Habilitação do eleitor",en:"Voter authorization"},
    question:{pt:"Quais condições autorizam abrir uma sessão de votação, inclusive após 17h?",en:"Which conditions permit opening a voting session, including after 5 p.m.?"},
    sourcePath:prefix+"src/uenux2/src/app/vota/operador/leidentidade/cpedeidentidade.cpp",
    independentCheck:{pt:"Confrontar eventos observáveis e regras de habilitação; identificar ausências de campos antes de inferir fraude.",en:"Compare observable events to authorization rules; identify missing fields before drawing conclusions."},
    limitation:{pt:"Terminal do mesário não executa normalmente no simulador web.",en:"The poll-worker terminal does not run in the usual web simulator."}
  },
  {
    number:2,component:{pt:"Terminal do mesário",en:"Poll-worker terminal"},
    question:{pt:"Quais ações exigem intervenção do operador e quais condições dependem do relógio?",en:"Which actions require operator intervention and what depends on the clock?"},
    sourcePath:prefix+"src/uenux2/src/app/vota/operador/comum/cinformacaothreadoperador.cpp",
    independentCheck:{pt:"Mapear transições de estado antes e depois de 17h/19h em revisão autorizada.",en:"Map state transitions around 5 and 7 p.m. in authorized review."},
    limitation:{pt:"Funções reconstruídas não provam a configuração ou execução do binário lacrado.",en:"Reconstructed functions do not prove configuration or execution of the sealed binary."}
  },
  {
    number:3,component:{pt:"Contabilização",en:"Counting"},
    question:{pt:"Como são representados votos nominais, brancos, nulos e sessões interrompidas?",en:"How are named, blank and invalid votes and interrupted sessions represented?"},
    sourcePath:prefix+"src/uenux2/src/app/comum/dados/crdvvota.cpp",
    independentCheck:{pt:"Recontar RDVs e comparar ao BU, documentando dependência entre os dois arquivos.",en:"Recount RDVs against BUs, documenting their shared provenance."},
    limitation:{pt:"Concordância RDV–BU não é uma medição externa da intenção do eleitor.",en:"RDV–BU agreement is not an external measurement of voter intent."}
  },
  {
    number:4,component:{pt:"Geração do BU",en:"BU generation"},
    question:{pt:"Quais estruturas alimentam o BU e quando o relatório é produzido?",en:"Which structures feed the BU and when is it produced?"},
    sourcePath:prefix+"src/uenux2/src/app/vota/eleitor/fimvotacao/cgerabu.cpp",
    independentCheck:{pt:"Preservar cópia impressa/QR e arquivo publicado; confrontar com mídia e totalização.",en:"Preserve independent printed/QR copies and published BU; reconcile with media and totalization."},
    limitation:{pt:"A geração do BU descrita pertence a código reconstruído de desenvolvimento.",en:"The described BU generation comes from a reconstructed development build."}
  },
  {
    number:5,component:{pt:"Logs e persistência",en:"Logs and persistence"},
    question:{pt:"Quais eventos deixam registros e quais operações não são observáveis no log público?",en:"Which events leave records and which operations are unobservable in public logs?"},
    sourcePath:prefix+"src/uenux2/src/app/comum/log/ieventoslog.u35.cpp",
    independentCheck:{pt:"Catalogar eventos reais antes dos testes; cruzar hora de voto, encerramento, BU e transmissão.",en:"Catalog actual events before tests; cross-check vote, close, BU and transmission times."},
    limitation:{pt:"O simulador pode não executar a thread responsável por essas rotinas.",en:"The web simulator may not run the threads responsible for these routines."}
  }
];
