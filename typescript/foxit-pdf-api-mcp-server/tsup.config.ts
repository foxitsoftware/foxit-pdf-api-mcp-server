import { readFileSync } from "node:fs";

import { defineConfig } from "tsup";

const pkg = JSON.parse(
  readFileSync(new URL("./package.json", import.meta.url), "utf8"),
) as { version: string };

export default defineConfig({
  entry: {
    // CLI entry (shebang from src/main.ts is preserved, used by `bin`)
    main: "src/main.ts",
    // Library entry
    index: "src/index.ts",
    // Programmatic server entry
    server: "src/server.ts",
  },
  format: ["esm"],
  dts: true,
  // Share common chunks across entries instead of duplicating the tool code
  splitting: true,
  sourcemap: true,
  clean: true,
  outDir: "dist",
  platform: "node",
  // Matches `engines.node: >=24`
  target: "node24",
  bundle: true,
  // Keep runtime dependencies (fastmcp, zod, dotenv) out of the bundle so
  // they resolve from node_modules as declared in `dependencies`.
  skipNodeModulesBundle: true,
  // Build-time version injection: no runtime fs read of package.json
  define: {
    __VERSION__: JSON.stringify(pkg.version),
  },
  esbuildOptions(options) {
    options.legalComments = "none";
  },
});
