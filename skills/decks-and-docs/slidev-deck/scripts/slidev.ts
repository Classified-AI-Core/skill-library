#!/usr/bin/env bun
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

function getArg(name: string, fallback?: string) {
  const i = Bun.argv.indexOf(name);
  if (i >= 0 && Bun.argv[i + 1]) return Bun.argv[i + 1];
  return fallback;
}

const cmd = Bun.argv[2];
const project = resolve(getArg("--project", "/home/workspace/Classified-clients/Proposals/Rythmm/slidev")!);
const markdown = getArg("--markdown");
const out = getArg("--out");

function run(command: string, args: string[], cwd = project) {
  const r = spawnSync(command, args, { cwd, stdio: "inherit", shell: false });
  if (r.status !== 0) process.exit(r.status ?? 1);
}

function ensureProject() {
  mkdirSync(project, { recursive: true });
  const pkgFile = resolve(project, "package.json");
  if (!existsSync(pkgFile)) {
    run("npm", ["init", "-y"], project);
  }
  const pkg = JSON.parse(readFileSync(pkgFile, "utf-8"));
  pkg.scripts = pkg.scripts || {};
  pkg.scripts.dev = pkg.scripts.dev || "slidev";
  pkg.scripts.build = pkg.scripts.build || "slidev build";
  pkg.scripts.export = pkg.scripts.export || "slidev export";
  writeFileSync(pkgFile, JSON.stringify(pkg, null, 2));

  if (!existsSync(resolve(project, "node_modules"))) {
    run("npm", ["install", "@slidev/cli", "@slidev/theme-default", "vue"], project);
  }

  const themeCss = resolve(project, "styles", "theme.css");
  if (!existsSync(dirname(themeCss))) mkdirSync(dirname(themeCss), { recursive: true });
  if (!existsSync(themeCss)) {
    writeFileSync(themeCss, `:root{--r-bg:#1b1c20;--r-panel:#2c303a;--r-panel2:#343949;--r-line:#4f5568;--r-text:#f4f6fb;--r-muted:#b7bdc9;--r-cyan:#73f0ff;--r-indigo:#a6b8ff;--r-class:#ff4d4f}
.slidev-layout{background:radial-gradient(1200px 700px at 10% 10%,#3a3e4a66 0%,transparent 55%),linear-gradient(135deg,#181a1f,#20242d 55%,#1c1f27);color:var(--r-text)}
h1,h2,h3{letter-spacing:-.02em}
.card{background:linear-gradient(160deg,#10152199,#171d2db0);border:1px solid var(--r-line);border-radius:16px;padding:16px;box-shadow:inset 0 1px 0 #ffffff17,0 8px 24px #00000030}
.badge{font-size:11px;letter-spacing:.12em;text-transform:uppercase;border:1px solid #646b80;border-radius:999px;padding:4px 9px;background:#ffffff14}
`);
  }

  // Do not generate setup/main.ts; Slidev setup files require specific default export semantics.
  // Theme styles can be imported directly from slides.md frontmatter CSS blocks when needed.
}

if (!cmd || cmd === "help") {
  console.log(`Usage:\n  bun slidev.ts build --project <dir> --markdown <slides.md>\n  bun slidev.ts dev --project <dir>\n  bun slidev.ts export-pdf --project <dir> --out <file.pdf>\n  bun slidev.ts export-spa --project <dir>`);
  process.exit(0);
}

ensureProject();

if (cmd === "build") {
  if (!markdown) {
    console.error("--markdown required");
    process.exit(1);
  }
  const targetSlides = resolve(project, "slides.md");
  const src = readFileSync(resolve(markdown), "utf-8");
  writeFileSync(targetSlides, src);
  run("npx", ["slidev", "build"], project);
  console.log(resolve(project, "dist"));
} else if (cmd === "dev") {
  run("npx", ["slidev"], project);
} else if (cmd === "export-pdf") {
  const args = ["slidev", "export"];
  if (out) args.push("--output", out);
  run("npx", args, project);
  if (out) console.log(resolve(out));
} else if (cmd === "export-spa") {
  run("npx", ["slidev", "build"], project);
  console.log(resolve(project, "dist"));
} else {
  console.error(`Unknown command: ${cmd}`);
  process.exit(1);
}
