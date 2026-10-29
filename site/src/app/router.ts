import type { Language } from "../types/content.ts";

export function getLanguage(search: string): Language {
  return new URLSearchParams(search).get("lang") === "en" ? "en" : "pt";
}
export function languageUrl(lang: Language, hash = "#inicio"): string {
  return "?lang=" + encodeURIComponent(lang) + hash;
}
export function normalizedHash(hash: string): string {
  return hash.startsWith("#") ? hash.slice(1) : hash;
}
