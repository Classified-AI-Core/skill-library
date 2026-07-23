---
name: toprank
description: Use the local Toprank upstream repo to run SEO and Google Ads workflows for Zo projects. Activate when the
  user asks for SEO audits, ranking improvements, metadata cleanup, schema markup, keyword research, sitemap/robots
  work, content gap analysis, Search Console analysis, or Google Ads audit/optimization.
compatibility: Created for Zo Computer
metadata:
  author: Classified AI
  category: research
  maturity: beta
  tags:
    - seo
    - search-console
    - google-ads
    - metadata
    - schema
    - content-strategy
  related:
    - defuddle
    - fal-generate
    - memelord
---

## Purpose

This skill adapts the upstream Toprank repo at `/home/workspace/Skills/toprank-upstream` for Zo workflows.

Use it to:
- audit a live site or codebase for SEO issues
- turn findings into code changes
- prioritize fixes by expected traffic impact
- optionally extend the workflow into Google Ads once organic basics are in place

## When to activate

- "improve our SEO"
- "audit my sites for search"
- "why is traffic down?"
- "fix titles / descriptions / canonical / schema / sitemap / robots"
- "what content should we publish?"
- "set up Search Console workflow"
- "review Google Ads or wasted spend"

## Working modes

### 1. Crawl-only

Use when Google Search Console is not connected yet.

Focus on:
- metadata quality
- canonical setup
- robots and sitemap coverage
- internal linking
- schema opportunities
- crawlability and indexability
- page speed observations

### 2. Search Console + crawl

Use when GSC access is available.

Focus on:
- low-CTR queries
- striking-distance keywords
- losing pages
- cannibalization
- branded vs non-branded split
- prioritizing changes by actual impressions and clicks

### 3. SEO + implementation

Use when the user wants fixes shipped, not just a report.

After the audit:
- update metadata in the repo
- add sitemap/robots/schema
- improve page titles/descriptions
- create missing landing pages
- strengthen internal links
- verify before/after

### 4. SEO + Google Ads

Use only after the site has reasonable landing pages and measurement.

Ads is optional here. Organic foundations come first.

## Upstream map

Consult these upstream files when needed:
- SEO audit logic: `/home/workspace/Skills/toprank-upstream/seo/seo-analysis/SKILL.md`
- Keyword workflows: `/home/workspace/Skills/toprank-upstream/seo/keyword-research/SKILL.md`
- Metadata workflows: `/home/workspace/Skills/toprank-upstream/seo/meta-tags-optimizer/SKILL.md`
- CMS connector patterns: `/home/workspace/Skills/toprank-upstream/seo/setup-cms/SKILL.md`
- Search Console setup notes: `/home/workspace/Skills/toprank-upstream/seo/shared/preamble.md`

Do not treat the upstream repo as directly executable in Zo. It is a reference and workflow source.

## Local workflow

1. Identify the target
   - Determine project path and public URL.
   - For user-named apps, use the project mapping already defined in workspace rules.

2. Inventory the codebase
   - Run:
   ```bash
   bash /home/workspace/Skills/toprank/scripts/seo-inventory.sh /absolute/project/path
   ```
   - This surfaces metadata, canonicals, robots, sitemap, schema, and obvious gaps.

3. Decide the audit depth
   - If no GSC access: do a crawl/code audit.
   - If GSC access is available: follow the upstream `seo-analysis` flow and use real query/page data to rank fixes.

4. Build a priority list
   - Always sort by:
     1. indexation/canonical problems
     2. missing sitemap/robots/schema
     3. title/description CTR fixes on high-impression pages
     4. internal linking and page architecture
     5. new content / landing pages

5. Ship fixes
   - Make code changes in the repo.
   - Prefer direct implementation over broad recommendations when the user asks to improve SEO.

6. Verify
   - Confirm metadata output, sitemap coverage, and robots behavior.
   - If the app is live, fetch the rendered page and verify actual tags.

7. Record the next backlog
   - Keep a short list of follow-up items: content pages, schema expansion, measurement, and link targets.

## Project-specific guidance


## Guardrails

- Do not start with Google Ads if core crawl/index/metadata basics are broken.
- Do not assume localhost defaults are safe for production metadata.
- When the user asks for a report only, do not edit code until asked.

