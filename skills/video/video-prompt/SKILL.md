---
name: video-prompt
description: Turn a casual sentence or a reference video into a production-grade AI video generation prompt. The user supplies plain English or a file; this skill supplies all technical vocabulary (lighting, lens, grade, texture, imperfection, pacing) and writes the full prompt. Use when the user says "video prompt:", drops a video and asks for a similar one, asks for a prompt for an AI video, or wants to recreate a video style he saw.
compatibility: Created for Zo Computer
metadata:
  author: brent55.zo.computer
---

> Depends on: `prompt-scoring` (reads and logs lessons) and `higgsfield-run` (executes the prompt). Install the four prompt skills together: image-prompt, video-prompt, higgsfield-run, prompt-scoring.

# Video Prompt

The user never writes technical language. He gives three casual sentences or drops a file. The 60-line prompt block is the OUTPUT, not the input.

**The skill carries the vocabulary.** Never ask the user for a lens, a frame rate, a color grade, a lighting setup, an aspect ratio in decimals, or a camera movement name. Pull those from `references/prompt-blocks.md` and `references/camera-aesthetics.md` yourself.

## Step 0: Read the results log (mandatory, before anything else)

```bash
python3 /home/workspace/Skills/prompt-scoring/scripts/lessons.py --medium video
```

Apply ESTABLISHED PATTERNS to this build. Avoid what RECENT FAILURES name. Reuse what RECENT WINS name. Anything under INSUFFICIENT EVIDENCE is NOT a rule: do not act on it or cite it. An empty log means build from the defaults below, which is the correct early state.

## Mode routing (decide first, silently)

| the user's input | Mode | Questions to ask |
|---|---|---|
| A video, image, or link attached | **Reference** | Zero |
| A sentence or two describing a scene | **Describe** | Max 3, only if they change the output |
| "video prompt:" plus a full paragraph | **Describe** | Usually zero |

---

## Mode A: Reference

Zero questions. Analyze the file, then write the prompt.

### A1. Measure it, do not guess

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,duration,nb_frames \
  -show_entries format=duration -of default=noprint_wrappers=1 "<file>"
ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 "<file>"
```

Record: exact duration, fps, resolution, computed aspect ratio, whether an audio stream exists.
Silent reference means the prompt says "Silent." Never invent a soundtrack.

### A2. Look at it

```bash
mkdir -p /home/.z/workspaces/<conv>/vp
ffmpeg -y -i "<file>" -vf "fps=2,scale=480:-1,tile=5x4" -frames:v 1 /tmp/vp/contact-sheet.jpg
ffmpeg -y -ss <mid> -i "<file>" -frames:v 1 -q:v 2 /tmp/vp/detail.jpg
```

Read both with the image tool. Contact sheet gives motion and beat structure. Detail frame gives wardrobe, props, skin, background objects, light direction.

Extract a third frame at any moment where the contact sheet shows a change (a turn, a gesture, an expression shift).

### A3. Read the register before writing

**This is the step the old version of this skill got wrong.** It forced 5+ camera imperfections onto every prompt. A steady, softly lit lifestyle clip has none of them, and adding shake and focus hunting actively breaks the match.

Classify the reference on two axes, then build to that classification:

- **Camera energy**: locked / near-static / gentle handheld / active handheld / chaotic
- **Finish**: polished commercial / naturalistic lifestyle / consumer device / degraded archival

Restraint is a valid answer. If the camera does not move, the prompt says so and adds explicit negatives: "No zoom, orbit, deliberate pan, focus hunting, artificial camera shake, or scene cuts."

### A4. Describe only what is visible

Never assert camera metadata you cannot verify. Write "natural perspective resembling a 50mm full-frame lens," not "shot on a 50mm." Flag any inference as an approximation in the chat message, not inside the prompt block.

---

## Mode B: Describe

The user gives a casual sentence. Ask at most three questions, and only the ones whose answer changes the output:

1. **How long?** (skip if he said, or if it is obviously a short social clip; default 10-12s)
2. **Vertical or wide?** (skip if the use case implies it; default 9:16)
3. **Anything that has to be exact?** (a line of dialogue, a real person, a brand, a specific moment)

Everything else is yours to invent: casting, wardrobe, location props, time of day, light direction, lens, grade, texture, camera behavior, beat pacing, ending.

**Never ask about**: lens, fps, aspect ratio in numbers, color grade, lighting setup, camera movement names, imperfection packs, film stock, depth of field.

### Plain-English overrides

The user may append casual direction. Translate silently:

| He says | You build |
|---|---|
| "looks like an iPhone" | Smartphone Vertical pack, HDR clipping, tap-to-focus |
| "moodier" | Lower key, harder falloff, deeper shadows, cooler grade |
| "brighter" / "happier" | High-key soft light, lifted blacks, warm neutral grade |
| "less polished" | Consumer device finish, mild handheld, natural imperfect framing |
| "make it feel expensive" | Cinematic inverse rules: named lens, controlled light, shallow DOF, deliberate grade |
| "more real" | Add texture and behavior detail, not more camera effects |
| "slower" | Fewer beats, longer holds, single continuous action |

---

## Build the prompt (both modes)

Six labeled blocks, in order, plain text inside one code block. No markdown inside the prompt itself.

**MAIN SUBJECT** — age range, build, skin and hair described structurally, 3+ garments with color and fit, 1-2 accessories, what each hand is holding, one demeanor line. Always close with: "Maintain consistent identity, clothing, hairstyle, and appearance throughout the entire video."

**LOCATION** — specific place type plus 5+ concrete props with color and material. One sentence on light: direction, quality, and where shadows fall. Close with negative constraints (no crowds, no signage, no logos, no other people, whatever the reference excludes).

**VISUAL STYLE** — 4-6 short declarative fragments naming the finish, the palette in actual colors, contrast level, skin rendering, and texture. Close with what to avoid: beauty smoothing, dramatic posing, stylized film effects.

**CAMERA STYLE** — shot count and exact duration, framing (where the frame cuts the body), perspective approximation, background separation, and the camera-energy register from A3. For active registers, pull an imperfection pack from `references/camera-aesthetics.md`. For restrained registers, write the negatives instead. Never write only "realistic."

**ACTION AND TIMING** — timestamped beats covering the full duration, one action per 2-3 seconds. Each beat states body position, the action, and where the gaze goes. Close with: "Movements flow continuously between the timing cues, without pauses or resets at each boundary." The final beat is a deliberate ending, never a fade.

**AUDIO** — dialogue, ambience, or "Silent. No dialogue, music, or added ambience."

### Quality gates before delivery

- Beat timings sum exactly to the stated duration.
- No em dashes anywhere.
- Every garment, prop, and surface carries a color or material.
- The camera block's register matches the reference or the stated vibe, with no default imperfections bolted on.
- Identity-consistency clause present.
- Ending is explicit.

---

## Real-person check

If the subject is a real or famous person, text-to-video models block or distort likenesses. Produce a second variant for image-to-video: name the source photo needed (pose, angle, framing, setting) and write only the motion and beat blocks, omitting the appearance block.

For any reference-mode prompt, also tell the user that using the reference's opening frame as an image-to-video input is the closest possible match.

## Deliver

1. Full prompt in chat, ONE code block, paste-ready.
2. Save to `Content/video-prompts/<slug>-YYYY-MM-DD.md` with a header: concept, mode, duration, aspect, target model.
3. If a target model is known, append notes. Higgsfield and Seedance handle long structured prompts well; Veo wants audio described explicitly; Kling is strongest for image-to-video physics.
4. State any inference you made (lens, fps on a describe-mode build) in the chat message, outside the code block.
5. Offer to run it. `higgsfield-run` takes the saved file directly:
   `python3 Skills/higgsfield-run/scripts/hf_run.py generate --video --prompt-file <that file>`.
   Prefer the image-first path when the shot has a specific look: generate the
   first frame with `image-prompt` for a third of a cent, let the user pick one,
   then animate it with `--model kling3-turbo-i2v --start-frame <uploaded URL>`.
   Keep clips at 5 to 8 seconds; past that, faces drift and hands melt.
6. Display any generated clip inline in chat, never a bare path.
7. **After the user has seen generated output**, ask once, in one line: "Score 1-10, and what worked or broke?" Then log his answer with `prompt-scoring`. Do not ask before there is output to judge, and never ask twice.
