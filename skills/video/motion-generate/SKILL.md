---
name: motion-generate
description: Generate polished AI videos via Mosaic Motion's REST API (motion.so). Use when Dan says "make a Motion
  video", "generate with Motion", "mosaic motion this", or asks for a launch film, brand doc, explainer, logo animation,
  or hero video and Motion's curated templates fit better than HyperFrames. Hands-off generation — one prompt in,
  finished video URL out. Each generation burns >= 1 credit.
compatibility: Created for Zo Computer
metadata:
  author: zmann.zo.computer
  category: content-publishing
  maturity: stable
  tags:
    - motion
    - generate
    - api
    - auth
    - cli
    - data-pull
    - deploy
    - export
  related:
    - fal-generate
    - humanizer
    - post-scorer
---

# Motion (Mosaic Motion) — API Skill

Programmatic access to motion.so's video generation API. Wraps `https://api.motion.so/api/motion`.

## When to use this skill vs HyperFrames

- **Motion**: polished one-prompt videos with curated design-system presets (Apple, Stripe, Linear, Notion, Vercel etc.), Pro/Max plan features. Burns credits. Hosted.
- **HyperFrames**: deterministic local renders, frame-exact GSAP timing, audio-reactive visuals, no per-video cost.

Use Motion when Dan wants a polished hero/brand video FAST and is OK paying credits. Use HyperFrames for everything else (pipelines, audio sync, batch variants, anything local).

## Auth

API key in env: `MOTION_API_KEY` (starts with `motion_`).

## CLI usage

All commands are run from `scripts/`:

```bash
cd /home/workspace/Skills/motion-generate/scripts

# Generate a video (returns job_id, status, and the polling URL)
bun motion.ts generate "Create a 15s launch video for Acme, a fictional analytics platform" \
  --aspect 16:9 --duration 10-30s --design stripe

# Check job status (poll every 5s until completed)
bun motion.ts status <job_id>

# Generate + auto-poll until done (blocks, prints download URL)
bun motion.ts run "your prompt" --aspect 9:16 --duration 10-30s --design linear

# Pull an in-flight job to completion and download (use after `generate`)
bun motion.ts pull <job_id>

# Create a follow-up on a completed job (revision)
bun motion.ts followup <job_id> "Make it 25% faster and match my brand palette"

# List available design systems
bun motion.ts designs

# List valid aspect ratios and durations
bun motion.ts formats
```

## Key flags

- `--aspect` — `16:9` | `9:16` | `1:1` | `4:5` | `21:9`
- `--duration` — `<10s` | `10-30s` | `30s-1min` | `1-5min`
- `--design` — design system preset (see `designs` subcommand). Pro/Max only.
- `--design-md` — path to a brand `design.md` to override `--design`. Pro/Max only. Point it at your own brand design file.
- `--style-ref` — YouTube URL for style reference
- `--attach` — repeatable: `url|name|type|content_type` pipe-delimited. Up to 10 attachments. URLs must be publicly accessible (no auth).
- `--poll-interval` — seconds between polls in `run` mode (default 5)
- `--poll-timeout` — max seconds to wait in `run` mode (default 1800 = 30min)

## Two-stage completion (important)

Motion has nested status:
- `status` (outer) flips to `completed` when planning/generation is done — but the file isn't ready yet
- `output.status` (inner) flips to `completed` AND `output.download_url` populates when the encoded mp4 is actually downloadable

Always wait for BOTH before downloading. The skill's `run` and `pull` commands handle this. Don't write client code that just watches the outer status — it lies.

## Output

Successful jobs return a signed `download_url` valid for ~1 hour. The skill auto-downloads to `/home/workspace/Skills/motion-generate/outputs/<job_id>.mp4` when running interactively. For pipelines that need the file elsewhere, pass `--output <path>`.

## Cost awareness

Each `generate` or `run` burns >= 1 credit. The API has no auth-validation endpoint that doesn't cost credits — every test is a real generation. Don't loop generations in scripts without explicit confirmation.

For credit balance, plans, or settings: use motion.so directly. The REST API only exposes generation endpoints.

## Errors

- `401` — bad/missing key
- `402` — out of credits (top up at motion.so)
- `400` — schema validation; the response `details` array tells you what
- `404` — job_id not found or not yours
- `409` — follow-up on a non-completed job

