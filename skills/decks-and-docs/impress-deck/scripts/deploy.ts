#!/usr/bin/env bun

import { readFileSync } from "fs";
import { parseArgs } from "util";

const { values } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    html: { type: "string" },
    route: { type: "string" },
    public: { type: "boolean", default: false },
    help: { type: "boolean" },
  },
});

if (values.help || !values.html) {
  console.log(`Usage: bun deploy.ts --html <file.html> --route <path> [--public]

Options:
  --html    Path to generated HTML file (required)
  --route   zo.space route path (default: /decks/presentation)
  --public  Make publicly accessible
  --help    Show this help

Outputs the zo.space API route code to stdout for use with update_space_route.`);
  process.exit(values.help ? 0 : 1);
}

const htmlContent = readFileSync(values.html!, "utf-8");
const route = values.route || "/decks/presentation";

// Escape backticks and ${} for template literal embedding
const escaped = htmlContent
  .replace(/\\/g, "\\\\")
  .replace(/`/g, "\\`")
  .replace(/\$\{/g, "\\${");

const routeCode = `import type { Context } from "hono";

const html = \`${escaped}\`;

export default (c: Context) => {
  return c.html(html);
};
`;

// Write the route code to a temp file for reference
const outPath = `/home/.z/workspaces/tmp-deck-route.ts`;
Bun.write(outPath, routeCode);

console.log(`Route code written to: ${outPath}`);
console.log(`Deploy with: update_space_route("${route}", "api", code=<contents of ${outPath}>)`);
console.log(`Route: ${route}`);
console.log(`Public: ${values.public ? "yes" : "no"}`);
