---
name: cloudflare-crawl
description: Crawl entire websites using Cloudflare's Browser Rendering /crawl API. Returns site content as Markdown,
  HTML, or structured JSON. Use when you need to ingest, scrape, or extract data from multiple pages of a website in one
  operation.
compatibility: Created for Zo Computer
metadata:
  author: zmann.zo.computer
  category: content-publishing
  maturity: stable
  tags:
    - cloudflare
    - crawl
    - api
    - auth
    - automation
    - capture
    - cli
    - data-pull
  related:
    - bright-api
    - brainsync
    - google-account-router
    - impress-deck
---

# Cloudflare Crawl

Crawl entire websites using Cloudflare's Browser Rendering `/crawl` API. Supports returning content as Markdown, HTML, or structured JSON with optional AI-powered extraction.

## Requirements

Two environment variables must be set:

- `CLOUDFLARE_API_TOKEN` - Your Cloudflare API token with Browser Rendering permissions
- `CLOUDFLARE_ACCOUNT_ID` - Your Cloudflare account ID

## Usage

```bash
bun Skills/cloudflare-crawl/scripts/crawl.ts <command> [options]
```

## Commands

### `start <url>` - Initiate a crawl job

Starts an asynchronous crawl and returns the job ID.

```bash
bun Skills/cloudflare-crawl/scripts/crawl.ts start https://example.com --format markdown --limit 50 --depth 3
```

Options: `--format`, `--limit`, `--depth`, `--render/--no-render`, `--include`, `--exclude`, `--external`, `--subdomains`, `--source`, `--prompt`, `--schema`, `--max-age`, `--purposes`

### `status <job_id>` - Check job progress

```bash
bun Skills/cloudflare-crawl/scripts/crawl.ts status <job_id>
```

### `results <job_id>` - Fetch crawl results

Handles pagination automatically. Can save results to individual files.

```bash
bun Skills/cloudflare-crawl/scripts/crawl.ts results <job_id> --save ./output --format text
```

Options: `--status`, `--limit`, `--save`, `--format`

### `cancel <job_id>` - Cancel a running job

```bash
bun Skills/cloudflare-crawl/scripts/crawl.ts cancel <job_id>
```

### `run <url>` - All-in-one crawl

Starts a crawl, polls for completion, and returns results. Accepts all `start` options plus `--save`, `--poll-interval`, and `--timeout`.

```bash
bun Skills/cloudflare-crawl/scripts/crawl.ts run https://docs.example.com --limit 20 --save ./docs
```

### `--help` - Show usage information

```bash
bun Skills/cloudflare-crawl/scripts/crawl.ts --help
```

