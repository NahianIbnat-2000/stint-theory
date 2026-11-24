// Copy the research report from ../paper into the site, so the deployed site serves it.
// The copy is made at build time and is not committed (see .gitignore).
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
const src = new URL("../../paper/stint_theory_report.pdf", import.meta.url);
const dir = new URL("../public/papers/", import.meta.url);
if (!existsSync(src)) {
  console.error("paper/stint_theory_report.pdf is missing; the site links to it. Build the report first.");
  process.exit(1);
}
mkdirSync(dir, { recursive: true });
copyFileSync(src, new URL("STINT_THEORY_report_Nahian_Ibnat.pdf", dir));
console.log("report copied to public/papers/");
