// Refuse to build a site without the exported research data.
import { existsSync, readFileSync } from "node:fs";
const m = new URL("../public/data/manifest.json", import.meta.url);
if (!existsSync(m)) {
  console.error("public/data/manifest.json is missing. Run `python -m webexport` in the project root first.");
  process.exit(1);
}
const man = JSON.parse(readFileSync(m, "utf8"));
console.log(`data exported ${man.generated_utc}: ${man.races_simulator} races, ${man.reports.length} reports`);
if (man.missing?.length) console.log("not exported:", man.missing.join(", "));
