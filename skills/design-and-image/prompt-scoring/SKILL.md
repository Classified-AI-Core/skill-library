---
name: prompt-scoring
description: Score and learn from AI image and video generations. Asks the user for a 1-10 rating plus why after every generation, logs it, and feeds the accumulated lessons back into the next prompt build. Use when the user rates a generation ("score: 8, faces drifted"), after delivering any image or video prompt, or when he asks what has been working.
compatibility: Created for Zo Computer
metadata:
  author: brent55.zo.computer
---

> Pairs with `image-prompt`, `video-prompt` and `higgsfield-run`. Standalone use works for logging any generation score.

# Prompt Scoring

Every prompt used to be a one-off with no memory. This closes the loop: read before building, ask after delivering, log the answer.

**The read half is the half that matters.** A log nobody consults is not a control, it is a file. Never skip step 1.

## Step 1: Read before building (mandatory)

Before writing ANY image or video prompt, run:

```bash
python3 /home/workspace/Skills/prompt-scoring/scripts/lessons.py --medium video
python3 /home/workspace/Skills/prompt-scoring/scripts/lessons.py --medium image
```

Apply what it reports. Specifically:

- Anything under ESTABLISHED PATTERNS changes how you build.
- RECENT FAILURES are things not to repeat, quoted in the user's own words.
- RECENT WINS are constructions to reuse.
- **Anything under INSUFFICIENT EVIDENCE is not a rule.** Do not act on it, do not mention it as a finding, and never let one bad clip become a standing constraint.

On an empty log it says so and you build from skill defaults. That is the correct early state, not a problem to work around.

## Step 2: Ask after delivering (mandatory)

After the user has seen a generated image or video, ask exactly this, once, in one line:

> Score 1-10, and what worked or broke?

Do not ask before he has seen output. Do not ask twice. Do not pad the question with options or a rubric: his own words are the data.

If he answers with a number and no reason, ask once for the reason, because a score with no explanation teaches nothing and `log_result.py` will refuse it.

If he ignores the question, drop it. Never re-ask in a later turn.

## Step 3: Log it

Translate his answer into a record. He never types flags or tags.

```bash
python3 /home/workspace/Skills/prompt-scoring/scripts/log_result.py \
  --medium video --slug cafe-sip --mode reference \
  --generator higgsfield --model seedance-2.0 \
  --register locked --duration 15.7 --aspect 9:16 \
  --prompt-file Content/video-prompts/cafe-sip-2026-09-19.md \
  --output-file Videos/cafe-sip-v1.mp4 \
  --score 8 \
  --why "looked great until the last two seconds, his face turned into someone else" \
  --tags identity_drift,good_lighting,good_pacing
```

Rules for logging:

- `--why` is the user's wording, lightly cleaned, never your paraphrase of what you think he meant.
- `--tags` come from `references/failure-tags.md`. Assign them yourself by reading his text. A new tag requires adding the row to that file in the same change.
- Log every rated generation, including good ones. A log of only failures cannot tell you what works.
- One record per generation, not per prompt. Four variants of one prompt are four records.

## Standalone trigger

The user may score out of band: "score: 6, hands were mush" or "that one was a 9". Log it against the most recent generation in the conversation. If the target is genuinely unclear, ask which one, once.

## Reviewing

```bash
python3 /home/workspace/Skills/prompt-scoring/scripts/lessons.py --min-n 3
python3 /home/workspace/Skills/prompt-scoring/scripts/lessons.py --medium video --min-n 5
```

When the user asks what has been working, run it and relay the output. Do not editorialize past what the numbers support, and repeat the evidence threshold when a claim rests on thin data.

## Hard rules

- Never state a pattern the script placed under INSUFFICIENT EVIDENCE.
- Never invent a score, a reason, or a tag the user did not give you.
- Never skip step 1 because the log seems small.
- Log lives at `Content/prompt-results/results.jsonl`, append-only. Never rewrite or prune it.
