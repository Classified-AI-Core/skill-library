---
name: critique
description: Structured design critique of a web page, component, or UI surface. Scores visual hierarchy, spacing, typography, cognitive load, and UX heuristics, flags anti-patterns, runs persona walkthroughs, and ends with a prioritized fix list. Use when asked to "critique this design", "review this page", "design review", or before showing a site, client hub, or dashboard to a client or stakeholder.
license: Apache 2.0
compatibility: Created for Zo Computer. Adapted from the critique reference in pbakaus/impeccable (v4.3.1).
metadata:
  author: zmann.zo.computer
  source: https://github.com/pbakaus/impeccable/blob/main/.claude/skills/impeccable/reference/critique.md
---

# Critique

Full procedure, scoring rubrics, cognitive-load checks, heuristics table, and persona library are in
`references/critique.md`. Read it before starting and follow it.

## Local adaptations

Upstream this is one mode of the larger `impeccable` skill, which ships a ~1.6 MB detector CLI
(`.claude/skills/impeccable/scripts/impeccable`). That detector is **not** bundled here. Consequences:

- Treat every `impeccable detect`, `critique-storage`, and `live-server` command in the reference as
  unavailable. The reference already covers this: report "deterministic scan unavailable" and continue.
- Assessment B (evidence) becomes a browser pass instead: open the target with `agent-browser`
  (`agent-browser open <url>`, then `agent-browser screenshot <file> --full`), capture desktop and
  mobile widths, and read the screenshots. Inspect the source files for the same surface.
- Skip snapshot persistence and trend history. The chat report is the deliverable.
- Still run Assessment A and B as separate sub-agents when an agent tool exists, and still print the
  degraded banner if you cannot.
- Suggested follow-up commands in the report (`/polish`, `/layout`, etc.) refer to impeccable modes
  that are not installed. Phrase next steps as plain fixes instead.
