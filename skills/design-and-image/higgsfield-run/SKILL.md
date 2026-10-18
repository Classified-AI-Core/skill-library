---
name: higgsfield-run
description: Run a prompt through the Higgsfield REST API and bring the result back into the workspace. Submits, polls, downloads, records the spend, and hands off to prompt-scoring. Use after video-prompt or image-prompt has written a prompt, when the user says "generate it", "run that prompt", "make the image", or asks to animate a still he already approved.
compatibility: Created for Zo Computer
metadata:
  author: brent55.zo.computer
---

# Higgsfield Run

> Depends on: `video-prompt` and `image-prompt` (they write the prompts this runs) and `prompt-scoring` (logs the rating). Install all four together.

The execution half of the prompt system. `video-prompt` and `image-prompt` write
the text; this runs it; `prompt-scoring` records whether it was any good.

Everything goes through `scripts/hf_run.py`. Never call the Higgsfield API with
a hand-written curl: the ledger, the cost guard, and the terminal-state handling
all live in the script, and a bare curl silently skips all three.

The CLI at `/usr/local/bin/higgsfield` cannot be used from this sandbox. Its
OAuth callback lands on the sandbox's own localhost rather than the user's machine,
and the binary exposes no API-key variable. Every official Higgsfield skill
wraps that CLI and inherits the blocker. The REST API has no such problem.

## Credentials

`HIGGSFIELD_API_KEY` (single console key, id:secret; the older `HIGGSFIELD_API_KEY_ID` + `HIGGSFIELD_API_KEY_SECRET` pair still works), from
`console.higgsfield.ai`, set in Zo Settings > Advanced.

**Never write `/root/.zo_secrets.**` It is rebuilt from Settings at every sandbox
boot. Reading it is fine and the script does; writing it loses the key at the
next restart. Both names are registered in `System/secrets-manifest.json`.

```bash
python3 /home/workspace/Skills/higgsfield-run/scripts/hf_run.py doctor
```

`doctor` spends nothing. It GETs a random request id, where `404` proves the
credentials work and `401` proves they do not. Run it first whenever anything
looks wrong, before assuming a model or a prompt is at fault.

## The money rules

This command spends real dollars from a prepaid balance, so it is built to be
hard to spend by accident.

- Every run prints its estimate before submitting and **refuses above
  `--max-cost`, default $2.00**. Raise the cap deliberately, never reflexively.
- `--dry-run` prints the exact request body and sends nothing. Use it whenever
  a new model or parameter is involved.
- `--variants N` is **N separate requests and N separate charges**. The estimate
  multiplies; say the total out loud to the user before running more than two.
- Every submission writes an `intent` row to
  `Content/prompt-results/higgsfield-spend.jsonl` before the request leaves, and
  a `settled` row when it reaches a terminal state. An intent with no settlement
  means something died mid-poll and a charge may exist that nothing recorded.
- Higgsfield refunds failed generations automatically, so a settled row with a
  non-`completed` status is a refund candidate rather than a real charge.

Published rates: images $0.0032, Kling 3.0 $0.112/sec, Wan 3.0 $0.20/sec. A 5s
Kling clip is $0.56 and four variants is $2.24, which is exactly the cap's job.

## The image-first workflow, which is the point

Text-to-video has to invent identity, wardrobe, lighting, composition and motion
at once, and each is a chance to drift. Stills cost a third of a cent. So:

1. `image-prompt` writes the still prompt. Generate 4 variants for about a cent.
2. The user picks the frame. That is a decision made on something he can see.
3. `upload` the chosen still, which returns a public URL.
4. `generate` with `--model kling3-turbo-i2v --start-frame <that URL>`, so the
   video model only has to solve motion.

```bash
HF=/home/workspace/Skills/higgsfield-run/scripts/hf_run.py
python3 $HF generate --model soul --variants 4 --slug cafe-sip \
  --prompt-file /home/workspace/Content/image-prompts/cafe-sip-2026-09-20.md
URL=$(python3 $HF upload /home/workspace/Media/higgsfield/cafe-sip-2026-09-20/cafe-sip-03.jpg)
python3 $HF generate --model kling3-turbo-i2v --start-frame "$URL" --duration 5 \
  --slug cafe-sip --prompt-file /home/workspace/Content/video-prompts/cafe-sip-2026-09-20.md
```

`--prompt-file` takes the saved markdown directly and pulls the longest fenced
block out of it, so the prompt skills' output files are the input here with no
copying.

**Keep clips short.** Most models visibly degrade past 5 to 8 seconds: faces
drift, hands melt, backgrounds reorganize. Three tight clips cut together beat
one long one, and `--start-frame` on the previous clip's last frame carries
continuity across the cut.

## Commands

| Command | What it does |
|---|---|
| `doctor` | Verify credentials. Spends nothing. |
| `models` | List the registry with rates and endpoints. |
| `upload <file>` | Put a local file in Higgsfield storage, print its public URL. |
| `generate` | Submit, poll, download into `Media/higgsfield/<slug>-<date>/`. |
| `status <id> [--download]` | Inspect or recover one request. |

Useful flags on `generate`: `--model`, `--video`, `--prompt`, `--prompt-file`,
`--slug`, `--variants`, `--duration`, `--aspect`, `--resolution`,
`--start-frame`, `--param k=v`, `--max-cost`, `--timeout`, `--dry-run`.

## When a model 404s

The registry in `scripts/models.json` is a cached answer, not a guarantee.
Higgsfield's own docs say the catalog lives at `console.higgsfield.ai` and that
`/docs/openapi.json` is supplementary. That is not pedantry: openapi.json lists
Kling at `v2.5-turbo` while the live model page documents `v3.0-turbo`.

So a `404` on submit means the endpoint path moved, not that the account lacks
access. Open that model's page under `docs.higgsfield.ai/docs/models/`, read the
endpoint off it, and edit `models.json`. A `401` is credentials; `423` or `503`
is the model being unavailable to this account.

## Deliver

1. Run it, then **display the result inline in chat**, never a bare path.
2. State what it cost, from the estimate, and note that the real charge on the
   account is the authoritative number.
3. Ask once, in one line: "Score 1-10, and what worked or broke?"
4. Log the answer with `Skills/prompt-scoring/scripts/log_result.py`, passing
   `--generator higgsfield` and the model, so the lessons file can tell models
   apart rather than blaming prompts for a model's habits.
