import { defineConfig } from "vite";

export default defineConfig({
  base: process.env.GITHUB_PAGES === "true" ? "/opianista/" : "/",
  build: { outDir: "dist", sourcemap: true },
});
