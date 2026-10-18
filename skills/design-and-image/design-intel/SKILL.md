---
name: design-intel
description: Design system intelligence for Zo. Fetch brand DESIGN.md files from getdesign.md, clone any website's UI, blend two design systems into a hybrid, export CSS/Tailwind tokens, check fidelity of a built page, generate Claude Design-ready briefs, and run AI design critiques. Triggers on "design:", "fetch design", "clone UI from", "design tokens", "fidelity check", "design critique", or any UI build request when a DESIGN.md exists in the project.
compatibility: Created for Zo Computer
metadata:
  author: brent55.zo.computer
---

> Optional companion: `ui-ux-pro-max` (design intelligence layered on the brand tokens; not part of this library). The scripts `fetch_design.py`, `clone_ui.py` and `export_tokens.py` cover brand-token fetching, UI cloning and token export. Output folder is set by `DESIGN_LIBRARY` (default `/home/workspace/Design/Library`); `critique.py` uses `CRITIQUE_MODEL` if you want a specific model.

## Overview

All brand design systems are cached in `Design/Library/<brand>/DESIGN.md`.
Scripts live in `Skills/design-intel/scripts/`. Run them from anywhere using absolute paths or from the skill directory.

## Commands

### Fetch a brand design system
```bash
python Skills/design-intel/scripts/fetch_design.py stripe
python Skills/design-intel/scripts/fetch_design.py stripe --project Projects/my-site
python Skills/design-intel/scripts/fetch_design.py --list   # show all available brands
```
Fetches via `npx getdesign@latest`. Cached to `Design/Library/<brand>/DESIGN.md`.

### List & search brands
```bash
python Skills/design-intel/scripts/list_brands.py
python Skills/design-intel/scripts/list_brands.py fintech
python Skills/design-intel/scripts/list_brands.py --categories
```

### Clone UI from a URL
```bash
python Skills/design-intel/scripts/clone_ui.py https://linear.app
python Skills/design-intel/scripts/clone_ui.py https://linear.app --output Projects/my-site/DESIGN.md
```
Extracts colors, typography, spacing, and component patterns. Generates a DESIGN.md.

### Blend two design systems
```bash
python Skills/design-intel/scripts/blend_design.py Design/Library/stripe/DESIGN.md Design/Library/linear/DESIGN.md
python Skills/design-intel/scripts/blend_design.py stripe linear --typography-from stripe --colors-from linear
python Skills/design-intel/scripts/blend_design.py stripe linear --output Projects/my-site/DESIGN.md
```
Specify which brand to pull each section from. Defaults to best-guess merge.

### Export CSS / Tailwind tokens
```bash
python Skills/design-intel/scripts/export_tokens.py Design/Library/stripe/DESIGN.md
python Skills/design-intel/scripts/export_tokens.py Design/Library/stripe/DESIGN.md --format tailwind
python Skills/design-intel/scripts/export_tokens.py Design/Library/stripe/DESIGN.md --format both --output Projects/my-site/
```
Outputs `tokens.css` (CSS variables) and/or `tailwind.tokens.js` (Tailwind config extension).

### Export Claude Design brief
```bash
python Skills/design-intel/scripts/export_brief.py Design/Library/stripe/DESIGN.md
python Skills/design-intel/scripts/export_brief.py Design/Library/stripe/DESIGN.md --template dashboard
python Skills/design-intel/scripts/export_brief.py Design/Library/stripe/DESIGN.md --template landing
```
Templates: `dashboard`, `landing`, `auth`, `component`, `mobile`. Outputs a ready-to-paste Claude Design prompt.

### Fidelity check
```bash
python Skills/design-intel/scripts/fidelity_check.py https://example.com/page Design/Library/stripe/DESIGN.md
python Skills/design-intel/scripts/fidelity_check.py https://example.com/page Design/Library/stripe/DESIGN.md --report
```
Screenshots the URL, compares colors/fonts against the design system, outputs a fidelity score.

### Design critique
```bash
python Skills/design-intel/scripts/critique.py https://example.com/page Design/Library/stripe/DESIGN.md
python Skills/design-intel/scripts/critique.py /path/to/screenshot.png Design/Library/stripe/DESIGN.md
```
AI-powered gap analysis. Outputs a critique report saved to `Design/Library/critiques/`.

## Auto-apply rule

When building any UI in Zo:
1. Check if `DESIGN.md` exists in the project folder — if so, read and apply it silently.
2. If the user says `design: [brand|URL|category]`, run the appropriate script first, then build.
3. For Claude Design deliverables, run `export_brief.py` and present the output as a paste-ready block.

## Dependencies

Install once:
```bash
pip install -r Skills/design-intel/scripts/requirements.txt
```
