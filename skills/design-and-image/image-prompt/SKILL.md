---
name: image-prompt
description: Turn a casual sentence or a reference photo into a photorealistic image generation prompt for Higgsfield. The user supplies plain English or a file; this skill supplies all photographic vocabulary (light, lens, grade, texture, imperfection). Use when the user says "image prompt:", drops a photo and asks for something similar, asks for a prompt to generate a realistic image, or asks for a hero/background/portrait image for any project.
compatibility: Created for Zo Computer
metadata:
  author: brent55.zo.computer
---

> Depends on: `prompt-scoring` (reads and logs lessons) and `higgsfield-run` (executes the prompt). Install the four prompt skills together: image-prompt, video-prompt, higgsfield-run, prompt-scoring.

# Image Prompt

Companion to `video-prompt`, same contract. The user gives three casual sentences or drops a file. The detailed prompt is the OUTPUT.

**The skill carries the vocabulary.** Never ask the user for a lens, an f-stop, a lighting setup, a color grade, or a film stock. Pull those from `references/photo-blocks.md`.

**Generator is Higgsfield** per standing rule. Never use `generate_image` or another provider for image generation.

## Step 0: Read the results log (mandatory, before anything else)

```bash
python3 /home/workspace/Skills/prompt-scoring/scripts/lessons.py --medium image
```

Apply ESTABLISHED PATTERNS to this build. Avoid what RECENT FAILURES name. Reuse what RECENT WINS name. Anything under INSUFFICIENT EVIDENCE is NOT a rule: do not act on it or cite it. An empty log means build from the defaults below.

## Mode routing (decide first, silently)

| the user's input | Mode | Questions |
|---|---|---|
| A photo or link attached | **Reference** | Zero |
| A sentence describing a scene | **Describe** | Max 3, only if they change the output |
| A project need ("hero image for X") | **Describe** | Usually zero, infer from the project |

---

## Mode A: Reference

Zero questions.

1. Read the image with the image tool.
2. Record measurable facts: aspect ratio, orientation, where the frame cuts the subject.
3. Read the register before writing:
   - **Light**: direction, quality, contrast, where shadows fall
   - **Finish**: editorial / documentary / commercial / snapshot / archival
   - **Depth**: background sharp, gently softened, or dissolved
4. Describe only what is visible. Phrase lens as an approximation ("perspective resembling an 85mm lens"), never as metadata.

Match restraint when the reference is restrained. A clean studio portrait gets no grain, no flare, no vignette.

---

## Mode B: Describe

Ask at most three, and only when the answer changes the output:

1. **What is it for?** (post, hero, background, thumbnail, print) — determines aspect and crop
2. **Vertical, square, or wide?** — skip if the use answers it
3. **Anything that has to be exact?** — a real person, a product, a brand, text in frame

Never ask about: lens, aperture, ISO, lighting setup, color grade, film stock, composition rules, depth of field.

### Plain-English overrides

| He says | You build |
|---|---|
| "looks like an iPhone" | Phone-camera register: even HDR, deep focus, slight over-sharpening, flat grade |
| "moodier" | Low-key, hard falloff, deep shadow occupying most of the frame, cooler grade |
| "brighter" | High-key, lifted blacks, broad diffused light, warm neutral grade |
| "make it feel expensive" | Editorial register: controlled light, 85mm compression, shallow depth, restrained grade |
| "more real" | More texture and imperfection detail, not more effects |
| "cleaner" | Remove grain, flare, vignette, clutter; add negative constraints |

---

## Build the prompt

Five labeled blocks, plain text inside one code block.

**SUBJECT** — who or what, age range and build if a person, skin and hair described structurally, 3+ garments or surfaces with color and material, what the hands are doing, expression and where the gaze goes.

**SETTING** — specific place, 5+ concrete props with color and material, one sentence on light direction and quality and where shadows fall, time of day.

**PHOTOGRAPHY** — framing (where the frame cuts the subject), perspective approximation, depth of field and what it does to the background, angle and height relative to the subject.

**FINISH** — palette in actual colors, contrast level, skin and surface rendering, grain or clarity, and the texture details that sell it (pores, flyaway hair, fabric weave, dust, condensation, wear).

**EXCLUDE** — negative constraints. This block does more work than any adjective. Pull from the bank in `references/photo-blocks.md`.

### Quality gates

- Every garment, prop, and surface carries a color or a material.
- Texture is named specifically, never as the word "realistic."
- The imperfection level matches the register; a clean commercial look gets none.
- No em dashes.
- Exclude block is present and non-generic.

---

## Real-person check

Image models distort or refuse real likenesses. If the subject is a real or famous person, say so and offer the edit path instead: source a real photograph, then use Higgsfield image EDITING (crop, recolor, reframe, outpaint, cleanup) rather than generating from scratch.

## Deliver

1. Full prompt in chat, ONE code block, paste-ready.
2. Offer to generate it immediately, via `higgsfield-run`, which takes the saved
   file directly:
   `python3 Skills/higgsfield-run/scripts/hf_run.py generate --model soul --variants 4 --prompt-file <that file>`.
   Default to 4 variants: stills cost $0.0032 each, so four is about a cent, and
   these models are a lottery draw at every seed. Selection beats a perfect prompt.
3. If generated, display the result inline in chat, never a bare path.
4. Save to `Content/image-prompts/<slug>-YYYY-MM-DD.md` with a header: concept, mode, aspect, generator.
5. State any inference you made outside the code block.
6. **After the user has seen the generated image**, ask once, in one line: "Score 1-10, and what worked or broke?" Then log his answer with `prompt-scoring`. Do not ask before there is output to judge, and never ask twice.
