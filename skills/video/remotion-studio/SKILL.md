---
name: remotion-studio
description: "Execute Remotion workflows across projects: setup, best-practice guidance, local editor UI, preview, and rendering."
compatibility: Created for Zo Computer
metadata: 
  category: content-publishing
  maturity: stable
  author: Classified AI
  tags:
    - remotion
    - video
    - studio
    - orchestration
  related:
    - remotion-setup
    - remotion-best-practices
author: Classified AI
---
# remotion-studio orchestrator

This skill is the execution layer. It pairs with:
- `Skills/remotion-setup` for install/upgrade
- `Skills/remotion-best-practices` for implementation patterns

## Use when
- You want to bootstrap or validate a Remotion project quickly.
- You want to run a local editor frontend and Remotion Studio.
- You want one-command render/still workflows.

## Commands
Run from `Skills/remotion-studio/scripts`:

```bash
bun remotion-studio.ts help
bun remotion-studio.ts check --project /home/workspace/remotionstudio
bun remotion-studio.ts dev --project /home/workspace/remotionstudio
bun remotion-studio.ts studio --project /home/workspace/remotionstudio
bun remotion-studio.ts render --project /home/workspace/remotionstudio --composition DemoVideo --out out/demo.mp4
bun remotion-studio.ts still --project /home/workspace/remotionstudio --composition DemoVideo --out out/frame.png --frame 30
```

## Workflow
1. Use `remotion-setup` if dependencies or project structure are missing.
2. Use `remotion-best-practices` rules while implementing features.
3. Use this skill to run and verify renders.

## Related Skills
- **remotion-setup** — install dependencies and scaffold project structure before using the studio
- **remotion-best-practices** — apply composition and animation patterns while building video content

