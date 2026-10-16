# video-prompt

Turns a casual sentence or a reference video into a production-grade AI video prompt (Higgsfield / Seedance / Kling / Veo). The user supplies plain English or a file; the skill supplies every piece of technical vocabulary.

Rewritten 2026-09-19 after a reference test on a cafe clip exposed two problems with v1: it demanded technical input from the user, and it forced camera imperfections onto every prompt regardless of what the reference actually did.

## Two modes

- **Reference mode** — drop a video, get the full prompt, zero questions asked. The skill measures the file with ffprobe, extracts a contact sheet and detail frames with ffmpeg, and writes from what it sees.
- **Describe mode** — one casual sentence, at most three plain questions (how long, vertical or wide, anything exact), everything technical invented by the skill.

## Structure

- `SKILL.md` — mode routing, register classification, 6-block build, real-person check, delivery
- `references/prompt-blocks.md` — light, lens, grade, texture, camera-energy register, pacing, framing, audio, negative constraints
- `references/camera-aesthetics.md` — camera looks with imperfection packs, including the restrained registers
- `references/example-annotated.md` — the Seedance 2.0 reference prompt, annotated

## Usage

Say `video prompt: <concept>`, or drop a video and ask for one like it. Output lands in chat as a paste-ready code block and saves to `Content/video-prompts/`.

## The core rule

Restraint is a valid register. Most polished lifestyle and commercial footage is locked or near-static, and adding shake, focus hunting, and exposure pumping to it makes the output worse, not more real. Classify the reference on camera energy and finish before reaching for an imperfection pack.

## What the user never supplies

Lens, fps, aspect ratio in numbers, color grade, lighting setup, camera movement names, imperfection packs, film stock, depth of field. Plain-English overrides only: "moodier", "looks like an iPhone", "less polished", "make it feel expensive".
