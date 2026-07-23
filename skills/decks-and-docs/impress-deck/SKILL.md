---
name: impress-deck
description: Generate cinematic Prezi-style presentation decks using impress.js with zoom, pan, rotate, and 3D effects. Deploy to zo.space as a shareable URL. Use when the user wants to create a pitch deck, presentation, or interactive slide deck.
compatibility: Created for Zo Computer
metadata:
  author: Classified AI
  category: content-publishing
  maturity: stable
  tags:
    - presentation
    - slides
    - prezi
    - cinematic
    - deploy
  related:
    - slidev-deck
    - nano-banana-2
---

# Impress Deck — Prezi-Style Presentation Generator

## Overview

Generate cinematic, spatially-navigated presentations using impress.js — the open-source Prezi engine. Presentations deploy to zo.space as shareable URLs with full zoom/pan/rotate/3D effects.

## When to Use

- User asks for a "pitch deck", "presentation", "slide deck", or "prezi-style" deck
- User wants interactive, non-linear slide navigation
- User wants a shareable URL for a presentation (not a PDF/PPTX)

## Quick Start

1. Gather slide content from the user (topic, key points, structure)
2. Run the generator: `cd /home/workspace/Skills/impress-deck/scripts && bun generate.ts --config /path/to/config.json --out /path/to/output.html`
3. Deploy to zo.space as an API route serving the HTML

## Config Format

Create a JSON config file with this structure:

```json
{
  "title": "Presentation Title",
  "theme": "dark",
  "transitionDuration": 1500,
  "slides": [
    {
      "id": "title",
      "type": "title",
      "heading": "Main Title",
      "subheading": "Subtitle or tagline",
      "layout": { "x": 0, "y": 0, "scale": 3 }
    },
    {
      "id": "problem",
      "type": "content",
      "heading": "The Problem",
      "body": "Description text here",
      "bullets": ["Point 1", "Point 2", "Point 3"],
      "layout": { "x": 2500, "y": 0, "scale": 1, "rotate": 0 }
    },
    {
      "id": "demo",
      "type": "image",
      "heading": "See It In Action",
      "imageUrl": "https://example.com/screenshot.png",
      "caption": "Live dashboard screenshot",
      "layout": { "x": 5000, "y": 1000, "z": -500, "scale": 1.5, "rotateY": 15 }
    },
    {
      "id": "overview",
      "type": "overview",
      "layout": { "x": 2500, "y": 500, "scale": 6 }
    }
  ]
}
```

### Slide Types

| Type | Fields | Purpose |
|------|--------|---------|
| `title` | heading, subheading | Opening/closing title slides |
| `content` | heading, body, bullets | Text content with optional bullet points |
| `image` | heading, imageUrl, caption | Image showcase with caption |
| `quote` | quote, attribution | Large quote with source |
| `metrics` | heading, metrics[{value, label}] | Big number stats display |
| `code` | heading, code, language | Code snippet display |
| `split` | heading, left, right | Two-column layout |
| `overview` | (none) | Zoomed-out view of all slides |
| `custom` | html | Raw HTML content |

### Layout Properties

| Property | Description | Default |
|----------|-------------|---------|
| `x` | Horizontal position (px) | auto-calculated |
| `y` | Vertical position (px) | auto-calculated |
| `z` | Depth position (px) | 0 |
| `scale` | Zoom level (1 = normal) | 1 |
| `rotate` | 2D rotation (degrees) | 0 |
| `rotateX` | 3D X-axis rotation | 0 |
| `rotateY` | 3D Y-axis rotation | 0 |

### Themes

| Theme | Description |
|-------|-------------|
| `dark` | Dark background, light text, blue accents |
| `light` | White background, dark text, indigo accents |
| `midnight` | Deep navy with gradient accents |
| `ember` | Dark with orange/red accents |
| `frost` | Cool blue-gray palette |
| `custom` | Provide `customTheme` object (see below) |

Custom theme:
```json
{
  "theme": "custom",
  "customTheme": {
    "bg": "#0a0a0a",
    "text": "#ffffff",
    "heading": "#e0e0e0",
    "accent": "#ff6b35",
    "accentAlt": "#ffa500",
    "muted": "#666666",
    "surface": "rgba(255,255,255,0.05)",
    "fontFamily": "'Inter', sans-serif",
    "headingFont": "'Space Grotesk', sans-serif"
  }
}
```

### Layout Strategies

If you omit `layout` from slides, the generator auto-calculates positions. You can set a global strategy:

```json
{
  "layoutStrategy": "spiral"
}
```

| Strategy | Effect |
|----------|--------|
| `linear` | Horizontal left-to-right |
| `spiral` | Outward spiral from center |
| `grid` | Grid layout with zoom transitions |
| `scatter` | Artistic scattered placement with rotations |
| `story` | Narrative path: zoom in → explore → zoom out |

## Deployment

After generating the HTML file, deploy to zo.space:

```bash
bun deploy.ts --html /path/to/output.html --route /decks/my-pitch --public
```

Options:
- `--route` — zo.space path (default: `/decks/<title-slug>`)
- `--public` — make publicly accessible (default: private)

The script creates an API route on zo.space that serves the HTML.

## Manual Deployment

If you prefer to deploy manually, use `update_space_route` with:
- `route_type: "api"`
- The generated HTML embedded in a Hono handler that returns `text/html`

## Keyboard Controls (in presentation)

| Key | Action |
|-----|--------|
| → / Space / Page Down | Next slide |
| ← / Page Up | Previous slide |
| Home | First slide |
| End | Last slide |
| Esc | Overview (if overview slide exists) |

## Tips for Great Presentations

1. **Start zoomed out** — Title slide with `scale: 3-4` gives cinematic zoom-in effect
2. **Use depth sparingly** — `z` values of -500 to -2000 add drama without disorientation
3. **Rotate for emphasis** — Small rotations (5-15°) feel intentional; large rotations feel chaotic
4. **End with overview** — A high-scale overview slide as the finale shows the full narrative arc
5. **Keep slides sparse** — 3-5 elements per slide max; the motion IS the visual interest
6. **Use metrics slides for impact** — Big numbers with zoom-in effects are very compelling

## Related Skills
- **slidev-deck** — alternative presentation tool for markdown-based Slidev decks
- **nano-banana-2** — generate AI images for use as slide visuals and backgrounds

