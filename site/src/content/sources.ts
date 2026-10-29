import type { Source } from "../types/content.ts";

export const sources: Source[] = [
  { id: "repo", name: "opianista — repositório", url: "https://github.com/joaopedropassostocantins/opianista", category: "repositorio", verification: "conferida_no_repositorio" },
  { id: "reg", name: "Registro de pré-registros e emendas", url: "https://github.com/joaopedropassostocantins/opianista/blob/main/protocolos/REGISTRO.md", category: "repositorio", verification: "conferida_no_repositorio" },
  { id: "emenda", name: "Emenda metodológica do Estudo 03", url: "https://github.com/joaopedropassostocantins/opianista/blob/main/protocolos/01_emenda_20261028_pianista.md", category: "repositorio", verification: "conferida_no_repositorio" },
  { id: "tse", name: "Portal de Dados Abertos do TSE", url: "https://dadosabertos.tse.jus.br/", category: "institucional", verification: "pendente" },
  { id: "original", name: "ChatGPT Sites — publicação original", url: "https://arquiteto-fiscal-evidencia.hazyzebra6.chatgpt.site", category: "original", verification: "pendente" }
  { id: "reconstruction", name: "VOTA — reconstrução da versão web de desenvolvimento (não código lacrado)", url: "https://github.com/igoroalonge/urna-vota-decompiled", category: "repositorio", verification: "conferida_no_repositorio" },
  { id: "law", name: "TSE — Resolução 23.759/2026 (art. 29)", url: "https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-759-de-26-de-fevereiro-de-2026", category: "institucional", verification: "pendente" },
  { id: "extension", name: "TRE-DF — comunicação sobre extensão até 19h", url: "https://www.tre-df.jus.br/comunicacao/noticias/2026/Outubro/tredf-informa-quantidade-de-votos-computados-apos-as-17-horas-no-segundo-turno-das-eleicoes", category: "institucional", verification: "pendente" }
];
