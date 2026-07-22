# Remotion Best Practices (Synthesized)

## Project architecture
- Keep composition registration centralized in `src/remotion-root.tsx`.
- Keep each composition in its own file under `src/videos/`.
- Separate editor UI code (`@remotion/player`) from render pipeline code (`remotion` + `@remotion/cli`).

## Composition design
- Use deterministic renders: avoid non-seeded randomness.
- Prefer composition props + Zod schemas for parameterized videos.
- Use `durationInFrames`, `fps`, width, and height explicitly.
- Use `calculateMetadata()` when duration and dimensions depend on props or media.

## Timing and animation
- Use `interpolate()` for explicit value mapping over frame ranges.
- Use `spring()` for natural motion and tune damping/mass explicitly.
- Break scenes with `Sequence` and bound durations intentionally.
- Use transitions sparingly and consistently.

## Assets and media
- Keep static assets in `public/` for local reliability.
- Pre-validate external media codecs before production rendering.
- Use FFmpeg for pre-processing operations (trim, normalize audio, silence detection).
- Keep source audio/video at target fps/resolution when possible.

## Audio
- Mix narration, music, and SFX with explicit gain automation.
- Duck background music under dialogue.
- Trim silence up front before render.
- Normalize loudness to avoid clipping between scenes.

## Captions and text
- Generate caption timing from transcript metadata, not guessed frame offsets.
- Keep typography constrained: max line lengths, safe title areas.
- Measure text when fitting dynamic copy and adjust font size responsively.

## Rendering and operations
- Use dedicated scripts for still/video render commands.
- Cache bundle artifacts for faster iterative rendering.
- Keep output paths explicit (`out/*.mp4`, `out/*.png`).
- Validate compositions in CI with at least one smoke-test render.

## Performance
- Avoid expensive per-frame calculations where memoization can be used.
- Precompute data arrays before render loops.
- Prefer simple layer stacks and avoid deeply nested animated trees unless required.

## For your planned editor frontend
- Use `@remotion/player` for timeline preview inside the app UI.
- Define a project schema (clips, tracks, transitions, audio cues) and map it to composition props.
- Keep editing state serializable as JSON for save/load + future collaboration features.
