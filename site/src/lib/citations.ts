export function safeLink(url: string): string {
  const parsed = new URL(url);
  if (parsed.protocol !== "https:") throw new Error("Only HTTPS citations are permitted");
  return parsed.href;
}
