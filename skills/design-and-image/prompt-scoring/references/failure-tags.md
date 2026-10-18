# Failure and Success Tag Vocabulary

Controlled vocabulary for `--tags`. The user never types these. Assign them yourself from his raw "why" text, and keep the raw text too: the tag is an index for aggregation, never a replacement for what he actually said.

Adding a tag is allowed. Add the row here in the same change that first uses it, or `log_result.py` rejects it.

## Identity and anatomy

| Tag | Means |
|---|---|
| `identity_drift` | Face or body changes into a different person mid-clip |
| `face_morph` | Features warp or smear without becoming a different person |
| `hand_deformity` | Extra, missing, or melted fingers |
| `wardrobe_drift` | Clothing changes color, cut, or disappears |
| `prop_drift` | A held object changes, swaps hands, or vanishes |

## Motion and physics

| Tag | Means |
|---|---|
| `unnatural_motion` | Movement reads as animated rather than filmed |
| `physics_break` | Objects pass through each other, gravity fails, liquid behaves wrong |
| `pacing_too_fast` | Action rushed against the requested beats |
| `pacing_too_slow` | Dead air, subject idles |
| `looping_motion` | The same gesture repeats mechanically |
| `beat_ignored` | Model skipped or reordered the timed beats |

## Camera

| Tag | Means |
|---|---|
| `camera_too_shaky` | Imperfection register was overdone |
| `camera_too_static` | Needed life, got a locked tripod |
| `unrequested_cut` | Model invented a scene change |
| `unrequested_zoom` | Model added a push or pull that was excluded |
| `framing_wrong` | Crop does not match the requested framing |

## Look

| Tag | Means |
|---|---|
| `lighting_wrong` | Direction, quality, or contrast missed |
| `palette_wrong` | Colors not as specified |
| `plastic_skin` | Beauty smoothing, no texture |
| `background_drift` | Environment reorganizes itself during the clip |
| `text_artifacts` | Garbled letters, signage, or captions appeared |
| `overstylized` | Filmic effects added that were excluded |

## Prompt-side causes

| Tag | Means |
|---|---|
| `prompt_too_long` | Model appeared to drop later instructions |
| `prompt_ambiguous` | An instruction was readable two ways |
| `duration_too_long` | Quality visibly degraded past a certain point |
| `missing_negative` | An unwanted element would have been blocked by an exclude line |

## Positive

| Tag | Means |
|---|---|
| `good_identity_hold` | Subject stayed consistent throughout |
| `good_lighting` | Light matched intent |
| `good_motion` | Movement read as real |
| `good_texture` | Skin, fabric, surfaces convincing |
| `good_pacing` | Beats landed as written |
| `reference_match` | Output closely matched the source reference |
