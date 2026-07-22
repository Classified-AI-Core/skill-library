---
name: slidev-deck
description: Build animated, branded Slidev decks from proposal content and export to PDF/SPA for sharing.
compatibility: Created for Zo Computer
metadata:
  author: zmann.zo.computer
  category: content-publishing
  maturity: beta
  tags:
    - presentation
    - slides
    - slidev
    - markdown
  related:
    - impress-deck
---

# Slidev Deck Skill

Use this skill when a proposal or presentation should be produced with richer motion, better theming, and a clean deck workflow.

## What this skill does
- Scaffolds/updates a Slidev project
- Applies custom branded theme tokens (colors, typography, accents)
- Generates a deck from markdown slides
- Exports static SPA build for hosting and optional PDF output

## Usage

### 1) Build deck from markdown

```bash
cd /home/workspace/Skills/slidev-deck/scripts
bun slidev.ts build \
  --project "/home/workspace/Classified-clients/Proposals/Rythmm/slidev" \
  --markdown "/home/workspace/Classified-clients/Proposals/Rythmm/slidev/slides.md"
```

### 2) Dev preview (local)

```bash
cd /home/workspace/Skills/slidev-deck/scripts
bun slidev.ts dev --project "/home/workspace/Classified-clients/Proposals/Rythmm/slidev"
```

### 3) Export PDF

```bash
cd /home/workspace/Skills/slidev-deck/scripts
bun slidev.ts export-pdf --project "/home/workspace/Classified-clients/Proposals/Rythmm/slidev" --out "/home/workspace/Classified-clients/Proposals/Rythmm/Rythmm - Social Media Strategy Proposal (Slidev).pdf"
```

### 4) Build static site (for hosting)

```bash
cd /home/workspace/Skills/slidev-deck/scripts
bun slidev.ts export-spa --project "/home/workspace/Classified-clients/Proposals/Rythmm/slidev"
```

## Notes
- This skill installs dependencies in the target Slidev project if missing.
- Use the generated `dist/` folder for hosting.

## Related Skills
- **impress-deck** — alternative presentation tool for cinematic Prezi-style decks
- **nano-banana-2** — generate AI images for use as slide visuals

