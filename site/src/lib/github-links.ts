export const repositoryBase = "https://github.com/joaopedropassostocantins/opianista";
export function githubFile(path: string): string {
  if (!path || path.startsWith("/") || path.includes("..") || path.includes("\\\\")) {
    throw new Error("Invalid repository path");
  }
  const isDir = path.endsWith("/");
  const cleanPath = path.replace(/\/$/, "").split("/").map(encodeURIComponent).join("/");
  return repositoryBase + "/" + (isDir ? "tree" : "blob") + "/main/" + cleanPath;
}
