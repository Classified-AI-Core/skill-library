# image-prompt

Turns a casual sentence or a reference photo into a photorealistic image generation prompt for Higgsfield. The user supplies plain English; the skill supplies every piece of photographic vocabulary.

Companion to `video-prompt`, same two-mode contract.

## Two modes

- **Reference mode** — drop a photo, get the full prompt, zero questions asked.
- **Describe mode** — one casual sentence, at most three plain questions, everything technical invented by the skill.

## Structure

- `SKILL.md` — mode routing, 5-block build, real-person check, delivery
- `references/photo-blocks.md` — light, register, lens, angle, grade, texture, imperfection dial, exclude bank, aspect ratios

## Usage

Say `image prompt: <concept>`, drop a photo and ask for something similar, or ask for a hero/background/portrait image for a project. Output lands in chat as a paste-ready code block and saves to `Content/image-prompts/`.

Generation always goes through Higgsfield per standing rule. Never `generate_image`.

## What the user never supplies

Lens, aperture, ISO, lighting setup, color grade, film stock, composition rules, depth of field. Plain-English overrides only: "moodier", "brighter", "looks like an iPhone", "make it feel expensive".
