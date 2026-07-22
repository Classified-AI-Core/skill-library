#!/usr/bin/env bun

const API_TOKEN = process.env.CLOUDFLARE_API_TOKEN;
const ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID;
const BASE_URL = `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/browser-rendering/crawl`;

function ensureEnv() {
  if (!API_TOKEN) {
    console.error("Error: CLOUDFLARE_API_TOKEN environment variable is not set.");
    process.exit(1);
  }
  if (!ACCOUNT_ID) {
    console.error("Error: CLOUDFLARE_ACCOUNT_ID environment variable is not set.");
    process.exit(1);
  }
}

function headers(): Record<string, string> {
  return {
    Authorization: `Bearer ${API_TOKEN}`,
    "Content-Type": "application/json",
  };
}

async function apiRequest(method: string, url: string, body?: unknown): Promise<unknown> {
  const opts: RequestInit = { method, headers: headers() };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const text = await res.text();

  let data: any;
  try {
    data = JSON.parse(text);
  } catch {
    if (!res.ok) {
      console.error(`HTTP ${res.status}: ${text}`);
      process.exit(1);
    }
    return text;
  }

  if (!res.ok) {
    console.error(`HTTP ${res.status}:`, JSON.stringify(data, null, 2));
    process.exit(1);
  }

  return data;
}

function sanitizeFilename(url: string): string {
  return url
    .replace(/^https?:\/\//, "")
    .replace(/[\/\\?#:*"<>|&=]/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_|_$/g, "");
}

function parseArgs(args: string[]) {
  const parsed: {
    positional: string[];
    flags: Record<string, string | boolean | string[]>;
  } = { positional: [], flags: {} };

  const repeatable = new Set(["include", "exclude"]);

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith("--")) {
      const key = arg.slice(2);
      if (key === "no-render") {
        parsed.flags.render = false;
      } else if (
        key === "render" ||
        key === "external" ||
        key === "subdomains" ||
        key === "help"
      ) {
        parsed.flags[key] = true;
      } else if (repeatable.has(key)) {
        const val = args[++i];
        if (!parsed.flags[key]) parsed.flags[key] = [];
        (parsed.flags[key] as string[]).push(val);
      } else {
        parsed.flags[key] = args[++i];
      }
    } else {
      parsed.positional.push(arg);
    }
  }
  return parsed;
}

function printHelp() {
  console.log(`Cloudflare Browser Rendering Crawl CLI

Usage: bun crawl.ts <command> [options]

Commands:
  start <url>       Start a crawl job, returns job ID
  status <job_id>   Check crawl job status and progress
  results <job_id>  Fetch crawl results (handles pagination)
  cancel <job_id>   Cancel a running crawl job
  run <url>         All-in-one: start, poll, and return results

start options:
  --format markdown|html|json   Output format (default: markdown)
  --limit <n>                   Max pages to crawl (default: 10, max: 100000)
  --depth <n>                   Max crawl depth (default: 100)
  --render / --no-render        Enable/disable JS rendering (default: true)
  --include <pattern>           URL include pattern (repeatable)
  --exclude <pattern>           URL exclude pattern (repeatable)
  --external                    Include external links (default: false)
  --subdomains                  Include subdomains (default: false)
  --source all|sitemaps|links   Link source (default: all)
  --prompt <text>               Prompt for JSON extraction
  --schema <json>               JSON schema for structured extraction
  --max-age <seconds>           Cache TTL (default: 86400)
  --purposes <list>             Comma-separated crawl purposes (default: search,ai-input,ai-train)

results options:
  --status completed|errored|skipped|disallowed   Filter by status
  --limit <n>                                     Max records to return
  --save <dir>                                    Save pages as files
  --format json|text                              Output format (default: text)

run options:
  All start options, plus:
  --save <dir>                  Save results to directory
  --poll-interval <ms>          Polling interval (default: 5000)
  --timeout <ms>                Max wait time (default: 300000)`);
}

async function cmdStart(url: string, flags: Record<string, any>): Promise<string> {
  const format = (flags.format as string) || "markdown";
  const limit = parseInt(flags.limit as string) || 10;
  const depth = parseInt(flags.depth as string) || 100;
  const render = flags.render !== false;
  const maxAge = parseInt(flags["max-age"] as string) || 86400;
  const purposesStr = (flags.purposes as string) || "search,ai-input,ai-train";
  const purposes = purposesStr.split(",").map((s: string) => s.trim());

  const body: any = {
    url,
    limit,
    depth,
    render,
    maxAge,
    crawlPurposes: purposes,
    formats: [format],
    options: {
      includeExternalLinks: flags.external === true,
      includeSubdomains: flags.subdomains === true,
    },
  };

  const source = flags.source as string;
  if (source) body.source = source;

  if (flags.include) body.options.includePatterns = flags.include;
  if (flags.exclude) body.options.excludePatterns = flags.exclude;

  if (format === "json") {
    body.jsonOptions = {};
    if (flags.prompt) body.jsonOptions.prompt = flags.prompt;
    if (flags.schema) {
      try {
        body.jsonOptions.response_format = JSON.parse(flags.schema as string);
      } catch {
        console.error("Error: --schema must be valid JSON");
        process.exit(1);
      }
    }
  }

  const data = (await apiRequest("POST", BASE_URL, body)) as any;

  const jobId = typeof data?.result === "string" ? data.result : data?.result?.id;
  if (!jobId) {
    console.error("Unexpected response:", JSON.stringify(data, null, 2));
    process.exit(1);
  }

  return jobId;
}

async function cmdStatus(jobId: string): Promise<{ status: string; finished: number; total: number }> {
  const url = `${BASE_URL}/${jobId}?limit=1`;
  const data = (await apiRequest("GET", url)) as any;
  const result = data?.result || data;
  const status = result?.status || "unknown";
  const finished = result?.completed || result?.finished || 0;
  const total = result?.total || 0;
  return { status, finished, total };
}

interface ResultPage {
  url: string;
  status: string;
  markdown?: string;
  html?: string;
  json?: any;
  metadata?: any;
  error?: string;
}

async function cmdResults(
  jobId: string,
  flags: Record<string, any>
): Promise<ResultPage[]> {
  const statusFilter = flags.status as string;
  const maxRecords = parseInt(flags.limit as string) || Infinity;
  const allPages: ResultPage[] = [];
  let cursor: string | undefined;

  while (allPages.length < maxRecords) {
    const params = new URLSearchParams();
    if (cursor) params.set("cursor", cursor);
    if (statusFilter) params.set("status", statusFilter);
    const batchLimit = Math.min(100, maxRecords - allPages.length);
    params.set("limit", String(batchLimit));

    const url = `${BASE_URL}/${jobId}?${params.toString()}`;
    const data = (await apiRequest("GET", url)) as any;
    const result = data?.result || data;
    const pages: ResultPage[] = result?.records || [];

    if (pages.length === 0) break;
    allPages.push(...pages);

    cursor = result?.cursor;
    if (!cursor) break;
  }

  return allPages.slice(0, maxRecords);
}

function formatExtension(format: string): string {
  if (format === "markdown") return ".md";
  if (format === "html") return ".html";
  return ".json";
}

async function saveResults(pages: ResultPage[], dir: string, ext: string) {
  const { mkdirSync, writeFileSync } = await import("fs");
  mkdirSync(dir, { recursive: true });

  for (const page of pages) {
    const filename = sanitizeFilename(page.url) + ext;
    const filepath = `${dir}/${filename}`;
    const content = page.json ? JSON.stringify(page.json, null, 2) : page.markdown || page.html || "";
    writeFileSync(filepath, content, "utf-8");
  }
  console.error(`Saved ${pages.length} files to ${dir}/`);
}

function printResults(pages: ResultPage[], outputFormat: string) {
  if (outputFormat === "json") {
    console.log(JSON.stringify(pages, null, 2));
  } else {
    for (const page of pages) {
      console.log(`\n--- ${page.url} [${page.status}] ---`);
      if (page.error) {
        console.log(`Error: ${page.error}`);
      } else if (page.json) {
        console.log(JSON.stringify(page.json, null, 2));
      } else if (page.markdown) {
        console.log(page.markdown);
      } else if (page.html) {
        console.log(page.html);
      }
    }
  }
}

async function cmdRun(url: string, flags: Record<string, any>) {
  const pollInterval = parseInt(flags["poll-interval"] as string) || 5000;
  const timeout = parseInt(flags.timeout as string) || 300000;
  const contentFormat = (flags.format as string) || "markdown";

  console.error(`Starting crawl of ${url}...`);
  const jobId = await cmdStart(url, flags);
  console.error(`Job started: ${jobId}`);

  const startTime = Date.now();
  while (true) {
    if (Date.now() - startTime > timeout) {
      console.error(`Timeout after ${timeout / 1000}s. Job ID: ${jobId}`);
      process.exit(1);
    }

    await new Promise((r) => setTimeout(r, pollInterval));

    const { status, finished, total } = await cmdStatus(jobId);
    console.error(`Crawling... ${finished}/${total} pages done (status: ${status})`);

    if (status === "completed") break;
    if (status !== "running") {
      console.error(`Crawl ${status}. Job ID: ${jobId}`);
      process.exit(1);
    }
  }

  console.error("Crawl complete. Fetching results...");
  const outputFormat = flags["results-format"] || "text";
  const pages = await cmdResults(jobId, { status: flags.status, limit: flags["results-limit"] });

  if (flags.save) {
    await saveResults(pages, flags.save as string, formatExtension(contentFormat));
  }

  printResults(pages, outputFormat as string);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
    printHelp();
    process.exit(0);
  }

  ensureEnv();

  const command = args[0];
  const { positional, flags } = parseArgs(args.slice(1));

  switch (command) {
    case "start": {
      const url = positional[0];
      if (!url) {
        console.error("Error: URL is required. Usage: crawl.ts start <url>");
        process.exit(1);
      }
      const jobId = await cmdStart(url, flags);
      console.log(jobId);
      break;
    }

    case "status": {
      const jobId = positional[0];
      if (!jobId) {
        console.error("Error: Job ID is required. Usage: crawl.ts status <job_id>");
        process.exit(1);
      }
      const { status, finished, total } = await cmdStatus(jobId);
      console.log(`Status: ${status}`);
      console.log(`Progress: ${finished}/${total} pages`);
      break;
    }

    case "results": {
      const jobId = positional[0];
      if (!jobId) {
        console.error("Error: Job ID is required. Usage: crawl.ts results <job_id>");
        process.exit(1);
      }
      const outputFormat = (flags.format as string) || "text";
      const pages = await cmdResults(jobId, flags);

      if (flags.save) {
        const ext = formatExtension((flags["content-format"] as string) || "markdown");
        await saveResults(pages, flags.save as string, ext);
      }

      printResults(pages, outputFormat);
      break;
    }

    case "cancel": {
      const jobId = positional[0];
      if (!jobId) {
        console.error("Error: Job ID is required. Usage: crawl.ts cancel <job_id>");
        process.exit(1);
      }
      await apiRequest("DELETE", `${BASE_URL}/${jobId}`);
      console.log(`Cancelled job ${jobId}`);
      break;
    }

    case "run": {
      const url = positional[0];
      if (!url) {
        console.error("Error: URL is required. Usage: crawl.ts run <url>");
        process.exit(1);
      }
      await cmdRun(url, flags);
      break;
    }

    default:
      console.error(`Unknown command: ${command}. Run with --help for usage.`);
      process.exit(1);
  }
}

main();
