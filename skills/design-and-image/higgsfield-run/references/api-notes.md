# Higgsfield API, verified facts

Retrieved 2026-09-20 from `docs.higgsfield.ai/docs/*.md` and the per-model pages
under `docs.higgsfield.ai/docs/models/`. Each claim below has a source. Anything
without one does not belong in this file.

## Shape

```
POST https://api.higgsfield.ai/<vendor>/<model>/<variant>
Authorization: Key ${HF_API_KEY_ID}:${HF_API_KEY_SECRET}
Content-Type: application/json

{"prompt": "...", "duration": 5, "resolution": "720p", "aspect_ratio": "16:9"}
```

Returns immediately:

```json
{"status": "queued",
 "request_id": "d7e6c0f3-...",
 "status_url": "https://api.higgsfield.ai/requests/d7e6c0f3-.../status",
 "cancel_url": "https://api.higgsfield.ai/requests/d7e6c0f3-.../cancel"}
```

Legacy `hf-api-key` / `hf-secret` headers still work; new code uses
`Authorization`. Source: `docs/authentication.md`.

## Statuses

From the `RequestStatus` schema in `docs/openapi.json`:

`queued`, `in_progress`, `completed`, `failed`, `nsfw`, `canceled`.

Terminal: `completed`, `failed`, `nsfw`, `canceled`. **`nsfw` is its own
terminal state, not a flavor of `failed`**, so code that only watches for
`failed` polls a finished request forever.

## Output shapes, all four of them

The same schema carries `images` (array), `video` (single object), `audio`
(single object), and `audios` (array). Each item is `{"url": "..."}` and nothing
else. Reading only `images[]` loses every video. Files stay available at least
seven days, so a pipeline's last step is always saving to our own storage.
Source: `docs/openapi.json`, `docs/quickstart.md`.

## Polling

Documented strategy: start at 2 s, grow by 1.5x to a 10 s ceiling, add jitter,
stop on any terminal state, and set a local timeout. Retry table: `200`
non-terminal keep polling, `401` stop and fix credentials, `404` stop and check
the id, `5xx` or network failure retry with backoff. Source:
`docs/concepts/polling.md`.

## File uploads

Three steps. `POST /files/generate-upload-url` with `{"content_type": "..."}`
returns `public_url`, `upload_url`, and `upload_headers`. `PUT` the bytes to
`upload_url` with **every** returned header. Then pass `public_url` to whichever
parameter the model documents: `image_url`, `video_url`, `file_url`.

**Do not send Higgsfield credentials to the presigned storage URL.** The upload
URL expires after one hour. Accepted types: `image/jpeg`, `image/jpg`,
`image/png`, `image/webp`, `image/gif`, `audio/wav`, `audio/x-wav`, `video/mp4`,
and the type used for the PUT must match the one the URL was created with.
Source: `docs/concepts/file-uploads.md`.

## Endpoints are per model and the OpenAPI file is not authoritative

Higgsfield's own `llms.txt` says to discover models at `console.higgsfield.ai`
and treat `/docs/openapi.json` as supplementary, adding that a model's absence
from that file does not establish it is unavailable.

That matters concretely. On the retrieval date openapi.json listed
`/kling-video/v2.5-turbo/pro/text-to-video` while the live Kling 3 model page
documented `/kling-video/v3.0-turbo/text-to-video`, and it listed soul at
`/higgsfield-ai/soul/standard` while the quickstart used
`/higgsfield-ai/soul/v2/standard`. Both disagreements are recorded in
`scripts/models.json`.

Verified endpoints, each from its own model page:

| Model | Endpoint | Key params |
|---|---|---|
| Soul (image) | `/higgsfield-ai/soul/v2/standard` | `prompt` |
| Grok Imagine Image 2.0 | `/xai/grok-imagine-image-2.0` | `prompt`, `resolution`, `aspect_ratio` |
| Kling 3.0 Turbo t2v | `/kling-video/v3.0-turbo/text-to-video` | `prompt`, `duration`, `resolution`, `aspect_ratio` |
| Kling 3.0 Turbo i2v | `/kling-video/v3.0-turbo/image-to-video` | `prompt`, `image_url`, `duration`, `resolution` |
| Wan 3.0 reference to video | `/alibaba/wan-3.0/reference-to-video` | `prompt`, `file_url`, `link_url`, `duration`, `resolution`, `aspect_ratio` |

**The start-frame parameter is named differently per model**: Kling calls it
`image_url`, Wan calls it `file_url`. The registry maps `--start-frame` onto the
right one, which is why the flag exists rather than raw `--param`.

## Billing

Pay per generation from a prepaid US dollar balance. No subscription, and a
higgsfield.ai website plan grants nothing here: API and website billing are
separate products. Failed generations are refunded automatically. Creating a key
allows 20 concurrent requests.

Multi-variant is not a video request parameter. Four variants means four
requests and four charges. Some image models document a batch size; video models
do not. Source: `higgsfield.ai/creator-hub`, model pages.

## What is NOT verified

- Rates in `models.json` come from the published catalog, not from an invoice.
  The account's real charge is authoritative.
- Video-to-video exists per the official skills repo's media-inputs table
  (`seedance_2_5` modes `video_edit` and `video_extension`, `gemini_omni`
  `video_references`), but no seedance or gemini endpoint has been read off a
  model page yet, so neither is in the registry. Add them from their own pages
  before use, never from the skills-repo table alone.
- No request has ever been submitted from this workspace. Everything above is
  documentation, not observed behavior.
