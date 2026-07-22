# Sanitization Report — 2026-07-21

Scope: 207 skills staged (Zo catalog pull + Classified originals), 10 categories.

## What was found and fixed

1. **Live SMS logs and contacts** — the staged `twilio` skill originally carried `logs/sendblue_status.jsonl` (5,470 lines), `logs/outbound.jsonl`, `logs/inbound.jsonl`, and `config/contacts.json` with real phone numbers. The entire skill was dropped from the library. Also purged: copied `node_modules/` and `.git/` directories.
2. **Private brand references** — `betint-pdf-export` and `betint-dashboard-recovery` entries removed from 19 SKILL.md `related:` lists. BETINT / SAM brand mentions in example commands (motion-generate, toprank) rewritten to generic examples.
3. **Personal workflow doc** — `research/toprank/references/zmann-seo-workflow.md` and its `AGENTS.md` (contained BETINT infra notes) deleted; SKILL.md references cleaned.
4. **Infra-wired skill pulled** — `graphic-composer` hardcodes Classified Terminal paths (`/home/workspace/classified-drive/terminal/...`); moved to holdback, not shipped.
5. **Private telemetry hooks** — "Observation Logging" sections referencing the private `Skills/_observations/` system stripped from 64 skills.

## Verified clean

Final scan of all staged files found zero hits for: phone numbers, personal/business emails, home address, SendBlue/API credentials, `.env` files (only `.env.example` templates remain), client names (Posner, Huot, SAM), and Classified/BETINT infra paths. Remaining `/home/workspace/Skills/<self>` paths are the standard Zo skill install location, not leaks.

## Held back (not in this repo)

- 9 Zo-catalog skills that name-collide with Classified originals (`holdback/` staging: zo-github, zo-pdf, zo-social-content, etc.) — Classified versions shipped instead.
- `graphic-composer` (Terminal-wired, see above).
- All moat/client/personal skills per the approved exclusion list (betint-*, classified-*, google-* keyring family, digits, brainsync, etc.) were never staged.
