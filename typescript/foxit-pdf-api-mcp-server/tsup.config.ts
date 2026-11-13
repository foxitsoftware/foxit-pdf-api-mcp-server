import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/server.ts", "src/index.ts", "src/main.ts"],
  format: ["esm"],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  outDir: "dist",
  platform: "node",
  bundle: true,
  external: ["fastmcp", "zod"],
});
