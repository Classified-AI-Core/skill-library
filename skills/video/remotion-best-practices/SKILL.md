---
name: remotion-best-practices
description: Deep reference for Remotion composition, animation, sequencing, audio, captions, assets, and troubleshooting.
compatibility: Created for Zo Computer
metadata:
  author: Classified AI
  category: content-publishing
  maturity: stable
  tags:
    - remotion
    - video
    - best-practices
    - reference
  related:
    - remotion-setup
    - remotion-studio
---

# remotion-best-practices

Use this skill when building or debugging Remotion videos.

## How to use
1. Read this file.
2. Open the relevant rule docs in `rules/` for the task.
3. Apply patterns in the active project and validate with a still render + full render.

## Rule index
- `rules/animations.md`
- `rules/compositions.md`
- `rules/sequencing.md`
- `rules/timing.md`
- `rules/text-animations.md`
- `rules/transitions.md`
- `rules/audio.md`
- `rules/videos.md`
- `rules/images.md`
- `rules/assets.md`
- `rules/fonts.md`
- `rules/import-srt-captions.md`
- `rules/transcribe-captions.md`
- `rules/display-captions.md`
- `rules/trimming.md`
- `rules/calculate-metadata.md`
- `rules/common-mistakes.md`
- `rules/troubleshooting.md`
- `rules/3d.md`

## Core non-negotiables
- Use frame-based animation only (`useCurrentFrame`, `interpolate`, `spring`).
- Clamp interpolation output ranges where needed.
- Keep composition props typed and serializable.
- Prefer deterministic rendering over time-based browser behavior.
- Validate with both:
  - still frame render at an important frame
  - full composition render

## Related Skills
- **remotion-setup** — install and configure Remotion projects before applying best practices
- **remotion-studio** — run renders and preview compositions using the orchestration layer

