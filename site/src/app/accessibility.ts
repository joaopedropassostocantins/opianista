export function enhanceAccessibility(): void {
  const links = Array.from(document.querySelectorAll<HTMLAnchorElement>(".nav-link"));
  const update = () => {
    const current = window.location.hash.replace(/^#/, "") || "inicio";
    links.forEach(link => {
      if (link.hash === "#" + current) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  };
  window.addEventListener("hashchange", update);
  update();
}
