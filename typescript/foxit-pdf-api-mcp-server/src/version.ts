import { readFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

// Get version from package.json
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageJson = JSON.parse(
  readFileSync(join(__dirname, "../package.json"), "utf-8")
);

export const VERSION = packageJson.version;
