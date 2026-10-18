# prompt-scoring

Closes the feedback loop on AI image and video generation. Asks the user for a 1-10 score plus a reason after every generation, logs it, and feeds the accumulated lessons back into the next prompt build.

Companion to `video-prompt` and `image-prompt`, which both call it.

## The loop

1. **Read** — `lessons.py` runs before any prompt is written. Established patterns change the build.
2. **Ask** — one line after the user sees output: "Score 1-10, and what worked or broke?"
3. **Log** — `log_result.py` appends a record. The user never types flags or tags.

The read half is the half that matters. A log nobody consults is a file, not a control.

## Structure

- `SKILL.md` — the three steps, standalone trigger, hard rules
- `scripts/lessons.py` — aggregates the log into an applyable lessons block
- `scripts/log_result.py` — appends one scored record, validates score and tags
- `references/failure-tags.md` — controlled vocabulary, 30 tags across identity, motion, camera, look, prompt-side causes, and positives

## Data

`Content/prompt-results/results.jsonl`, append-only. One record per generation, not per prompt: four variants of one prompt are four records.

## Evidence discipline

`lessons.py` refuses to state a pattern below `--min-n` (default 3). Everything thinner is listed under INSUFFICIENT EVIDENCE with its real count, so one bad clip can never become a standing rule. On an empty log it says so and the prompt skills build from their defaults.

Score drag per tag is reported as mean-with versus mean-without. A tag present on every row has no comparison group and is reported as ubiquitous rather than given a fabricated delta.

## Usage

Automatic through `video-prompt` and `image-prompt`. Out of band, the user can say "score: 6, hands were mush" and it logs against the most recent generation. To review: "what's been working?"
