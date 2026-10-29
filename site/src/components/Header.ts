import type { Language } from "../types/content.ts";
import { navigationLinks } from "../app/navigation.ts";
import { languageUrl } from "../app/router.ts";
import { escapeHtml } from "../lib/formatters.ts";
export function Header(lang: Language): string {
  const links = navigationLinks(lang).map(item => '<a class="nav-link" href="' + item.href + '">' + escapeHtml(item.label) + '</a>').join("");
  return '<header class="site-header" id="inicio">' +
    '<div class="container header-row"><a class="brand" href="#inicio" aria-label="opianista — início"><span class="brand-symbol" aria-hidden="true">O<span>·</span></span><span>opianista</span></a>' +
    '<nav class="nav" aria-label="' + (lang === "pt" ? "Navegação principal" : "Main navigation") + '">' + links + '</nav>' +
    '<div class="lang-switch" aria-label="' + (lang === "pt" ? "Idioma" : "Language") + '">' +
    '<a href="' + languageUrl("pt", window.location.hash || "#inicio") + '" lang="pt-BR" ' + (lang === "pt" ? 'aria-current="true"' : "") + '>PT</a><span aria-hidden="true">/</span>' +
    '<a href="' + languageUrl("en", window.location.hash || "#inicio") + '" lang="en" ' + (lang === "en" ? 'aria-current="true"' : "") + '>EN</a></div></div></header>';
}
