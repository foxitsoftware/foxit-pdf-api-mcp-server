import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/server.ts", "src/index.ts", "src/stdio-server.ts", "src/http-server.ts"],
  format: ["esm"],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  outDir: "dist",
  platform: "node",
  target: "node18",
  bundle: true,
  external: ["fastmcp", "zod"],
});
