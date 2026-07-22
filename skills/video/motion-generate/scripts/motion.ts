#!/usr/bin/env bun
/**
 * Mosaic Motion API client — generate, status, run (gen+poll), followup, downloads.
 * Env: MOTION_API_KEY
 */
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const API_BASE = "https://api.motion.so/api/motion";
const OUTPUT_DIR = "/home/workspace/Skills/motion-generate/outputs";

const ASPECTS = ["16:9", "9:16", "1:1", "4:5", "21:9"] as const;
const DURATIONS = ["<10s", "10-30s", "30s-1min", "1-5min"] as const;
const DESIGNS = [
  "mosaic", "apple", "claude", "cursor", "linear", "vercel", "stripe",
  "figma", "notion", "spotify", "supabase", "raycast", "framer", "resend",
  "mintlify", "sentry", "tesla", "nike", "shopify", "airbnb", "posthog",
] as const;

function key(): string {
  let k = process.env.MOTION_API_KEY;
  if (!k) {
    try {
      const envFile = require("node:fs").readFileSync("/etc/zo/env", "utf-8");
      const m = envFile.match(/^MOTION_API_KEY=(.+)$/m);
      if (m) k = m[1].trim();
    } catch {}
  }
  if (!k) {
    console.error("ERROR: MOTION_API_KEY not set in env or /etc/zo/env.");
    process.exit(1);
  }
  return k;
}

function headers(): HeadersInit {
  return {
    Authorization: `Bearer ${key()}`,
    "Content-Type": "application/json",
  };
}

type Attachment = {
  url: string;
  name?: string;
  type?: "image" | "video" | "audio" | "file";
  content_type?: string;
};

function parseAttach(raw: string): Attachment {
  const parts = raw.split("|").map((p) => p.trim());
  const a: Attachment = { url: parts[0] };
  if (parts[1]) a.name = parts[1];
  if (parts[2]) a.type = parts[2] as Attachment["type"];
  if (parts[3]) a.content_type = parts[3];
  return a;
}

function parseFlags(args: string[]): Record<string, string | string[]> {
  const out: Record<string, string | string[]> = {};
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (!a.startsWith("--")) continue;
    const k = a.slice(2);
    const v = args[i + 1] ?? "";
    if (k === "attach") {
      const existing = (out[k] as string[]) ?? [];
      existing.push(v);
      out[k] = existing;
    } else {
      out[k] = v;
    }
    i++;
  }
  return out;
}

async function postSession(body: Record<string, unknown>): Promise<{ job_id: string; status: string; status_url: string }> {
  const r = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) {
    console.error(`HTTP ${r.status}:`, text);
    process.exit(1);
  }
  return JSON.parse(text);
}

async function getStatus(jobId: string): Promise<any> {
  const r = await fetch(`${API_BASE}/sessions/${jobId}`, { headers: headers() });
  const text = await r.text();
  if (!r.ok) {
    console.error(`HTTP ${r.status}:`, text);
    process.exit(1);
  }
  return JSON.parse(text);
}

async function postFollowup(jobId: string, body: Record<string, unknown>): Promise<any> {
  const r = await fetch(`${API_BASE}/sessions/${jobId}/followups`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) {
    console.error(`HTTP ${r.status}:`, text);
    process.exit(1);
  }
  return JSON.parse(text);
}

function buildBody(prompt: string, flags: Record<string, string | string[]>): Record<string, unknown> {
  const body: Record<string, unknown> = { prompt };
  if (flags.aspect) body.aspect_ratio = flags.aspect;
  if (flags.duration) body.duration = flags.duration;
  if (flags.design) body.design_system_id = flags.design;
  if (flags["design-md"]) {
    const path = flags["design-md"] as string;
    const content = require("node:fs").readFileSync(path, "utf-8");
    body.design_md = { filename: path.split("/").pop(), content };
  }
  if (flags["style-ref"]) body.style_reference_url = flags["style-ref"];
  if (flags.attach) {
    const list = (Array.isArray(flags.attach) ? flags.attach : [flags.attach]) as string[];
    body.attachments = list.map(parseAttach);
  }
  return body;
}

async function downloadOutput(url: string, jobId: string, outPath?: string): Promise<string> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`download HTTP ${r.status}`);
  const buf = Buffer.from(await r.arrayBuffer());
  const path = outPath ? resolve(outPath) : `${OUTPUT_DIR}/${jobId}.mp4`;
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, buf);
  return path;
}

async function cmdGenerate(args: string[]) {
  const prompt = args[0];
  if (!prompt) {
    console.error("Usage: motion.ts generate <prompt> [--aspect ...] [--duration ...] [--design ...]");
    process.exit(1);
  }
  const flags = parseFlags(args.slice(1));
  const body = buildBody(prompt, flags);
  const res = await postSession(body);
  console.log(JSON.stringify(res, null, 2));
}

async function cmdStatus(args: string[]) {
  const jobId = args[0];
  if (!jobId) {
    console.error("Usage: motion.ts status <job_id>");
    process.exit(1);
  }
  const res = await getStatus(jobId);
  console.log(JSON.stringify(res, null, 2));
}

async function cmdRun(args: string[]) {
  const prompt = args[0];
  if (!prompt) {
    console.error("Usage: motion.ts run <prompt> [flags]");
    process.exit(1);
  }
  const flags = parseFlags(args.slice(1));
  const interval = Number(flags["poll-interval"] ?? 5);
  const timeout = Number(flags["poll-timeout"] ?? 1800);
  const outputPath = flags.output as string | undefined;

  const body = buildBody(prompt, flags);
  const create = await postSession(body);
  const jobId = create.job_id;
  console.error(`[motion] job_id=${jobId} status=${create.status}`);

  const start = Date.now();
  let lastStatus = create.status;
  while (true) {
    if ((Date.now() - start) / 1000 > timeout) {
      console.error(`[motion] timeout after ${timeout}s, last status: ${lastStatus}`);
      process.exit(2);
    }
    await new Promise((r) => setTimeout(r, interval * 1000));
    const s = await getStatus(jobId);
    if (s.status !== lastStatus) {
      console.error(`[motion] status=${s.status} elapsed=${Math.round((Date.now() - start) / 1000)}s`);
      lastStatus = s.status;
    }
    const innerStatus = s.output?.status;
    if (s.status === "completed" && innerStatus && innerStatus !== lastStatus) {
      console.error(`[motion] render=${innerStatus} elapsed=${Math.round((Date.now() - start) / 1000)}s`);
      lastStatus = innerStatus;
    }
    if (s.status === "completed" && innerStatus === "completed") {
      const dl = s.output?.download_url;
      if (!dl) {
        console.error("[motion] render completed but no download_url:", JSON.stringify(s, null, 2));
        process.exit(3);
      }
      const path = await downloadOutput(dl, jobId, outputPath);
      console.log(JSON.stringify({ job_id: jobId, status: "completed", file: path, signed_url: dl, sources: s.sources?.length ?? 0 }, null, 2));
      return;
    }
    if (s.status === "failed" || innerStatus === "failed") {
      console.error("[motion] job failed:", JSON.stringify(s.error ?? s.output?.error ?? s, null, 2));
      process.exit(4);
    }
  }
}

async function cmdPull(args: string[]) {
  const jobId = args[0];
  if (!jobId) {
    console.error("Usage: motion.ts pull <job_id> [--poll-interval 5] [--poll-timeout 1800] [--output <path>]");
    process.exit(1);
  }
  const flags = parseFlags(args.slice(1));
  const interval = Number(flags["poll-interval"] ?? 5);
  const timeout = Number(flags["poll-timeout"] ?? 1800);
  const outputPath = flags.output as string | undefined;
  const start = Date.now();
  let last = "";
  while (true) {
    if ((Date.now() - start) / 1000 > timeout) {
      console.error(`[motion] timeout after ${timeout}s, last=${last}`);
      process.exit(2);
    }
    const s = await getStatus(jobId);
    const summary = `outer=${s.status} inner=${s.output?.status ?? "n/a"}`;
    if (summary !== last) {
      console.error(`[motion] ${summary} elapsed=${Math.round((Date.now() - start) / 1000)}s`);
      last = summary;
    }
    if (s.status === "completed" && s.output?.status === "completed" && s.output?.download_url) {
      const path = await downloadOutput(s.output.download_url, jobId, outputPath);
      console.log(JSON.stringify({ job_id: jobId, file: path, signed_url: s.output.download_url, sources: s.sources?.length ?? 0 }, null, 2));
      return;
    }
    if (s.status === "failed" || s.output?.status === "failed") {
      console.error("[motion] job failed:", JSON.stringify(s.error ?? s.output?.error ?? s, null, 2));
      process.exit(4);
    }
    await new Promise((r) => setTimeout(r, interval * 1000));
  }
}

async function cmdFollowup(args: string[]) {
  const jobId = args[0];
  const prompt = args[1];
  if (!jobId || !prompt) {
    console.error("Usage: motion.ts followup <job_id> <prompt> [flags]");
    process.exit(1);
  }
  const flags = parseFlags(args.slice(2));
  const body = buildBody(prompt, flags);
  const res = await postFollowup(jobId, body);
  console.log(JSON.stringify(res, null, 2));
}

function cmdDesigns() {
  console.log(DESIGNS.join("\n"));
}

function cmdFormats() {
  console.log("aspect ratios:");
  for (const a of ASPECTS) console.log(`  ${a}`);
  console.log("durations:");
  for (const d of DURATIONS) console.log(`  ${d}`);
}

function help() {
  console.log(`motion.ts — Mosaic Motion API client

Commands:
  generate <prompt> [flags]       Create a session, print job_id (does not wait)
  status <job_id>                 Get job status
  run <prompt> [flags]            generate + poll until done, download to outputs/
  followup <job_id> <prompt> [..] Revise a completed job
  designs                         List design system presets
  formats                         List aspect ratios and durations

Flags:
  --aspect 16:9 | 9:16 | 1:1 | 4:5 | 21:9
  --duration <10s | 10-30s | 30s-1min | 1-5min
  --design <preset>
  --design-md <path-to-design.md>
  --style-ref <youtube-url>
  --attach 'url|name|type|content_type' (repeatable, up to 10)
  --poll-interval 5
  --poll-timeout 1800
  --output <path-to-mp4>

Env: MOTION_API_KEY`);
}

const [, , cmd, ...rest] = process.argv;
switch (cmd) {
  case "generate": await cmdGenerate(rest); break;
  case "status": await cmdStatus(rest); break;
  case "run": await cmdRun(rest); break;
  case "pull": await cmdPull(rest); break;
  case "followup": await cmdFollowup(rest); break;
  case "designs": cmdDesigns(); break;
  case "formats": cmdFormats(); break;
  default: help();
}
