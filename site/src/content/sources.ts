import type { Source } from "../types/content.ts";

export const sources: Source[] = [
  { id: "repo", name: "opianista — repositório", url: "https://github.com/joaopedropassostocantins/opianista", category: "repositorio", verification: "conferida_no_repositorio" },
  { id: "reg", name: "Registro de pré-registros e emendas", url: "https://github.com/joaopedropassostocantins/opianista/blob/main/protocolos/REGISTRO.md", category: "repositorio", verification: "conferida_no_repositorio" },
  { id: "emenda", name: "Emenda metodológica do Estudo 03", url: "https://github.com/joaopedropassostocantins/opianista/blob/main/protocolos/01_emenda_20261028_pianista.md", category: "repositorio", verification: "conferida_no_repositorio" },
  { id: "tse", name: "Portal de Dados Abertos do TSE", url: "https://dadosabertos.tse.jus.br/", category: "institucional", verification: "pendente" },
  { id: "original", name: "ChatGPT Sites — publicação original", url: "https://arquiteto-fiscal-evidencia.hazyzebra6.chatgpt.site", category: "original", verification: "pendente" }
];
