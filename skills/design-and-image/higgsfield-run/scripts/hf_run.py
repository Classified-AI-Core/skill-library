#!/usr/bin/env python3
"""Submit a prompt to the Higgsfield API, poll it, download the result.

Closes the loop on video-prompt / image-prompt: the prompt skills write the
text, this runs it, and prompt-scoring records what the user thought of the output.

Five commands:
  doctor    verify credentials without spending anything
  models    list the registry
  upload    put a local file in Higgsfield storage, print its public URL
  generate  submit, poll, download
  status    inspect one request id

Money rules, because this command spends real dollars:
  - Every submission is estimated BEFORE it is sent and refused above
    --max-cost (default $2.00).
  - --dry-run prints the exact HTTP request and sends nothing.
  - Every submission writes an INTENT row to the spend ledger before the
    request leaves, and a SETTLED row after it reaches a terminal state.
    A crash between the two leaves an intent with no settlement, which is
    exactly the state worth being able to see.
  - Higgsfield refunds failed generations automatically, so a settled row
    carrying a non-completed status is a refund candidate, not a charge.

Credentials are read env-first, then /root/.zo_secrets. That file is NEVER
written: it is rebuilt from Settings > Advanced on every sandbox boot.
"""

import argparse
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

API_ROOT = "https://api.higgsfield.ai"
UPLOAD_URL = f"{API_ROOT}/files/generate-upload-url"
SECRETS_FILE = "/root/.zo_secrets"
REGISTRY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.json")

MEDIA_ROOT = os.environ.get("HF_MEDIA_ROOT", "/home/workspace/Media/higgsfield")
LEDGER_PATH = os.environ.get("HF_LEDGER_PATH", "/home/workspace/Content/prompt-results/higgsfield-spend.jsonl")

TERMINAL = {"completed", "failed", "nsfw", "canceled"}
DEFAULT_MAX_COST = 2.00

CONTENT_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif",
    ".mp4": "video/mp4", ".wav": "audio/wav",
}


# --------------------------------------------------------------------------
# credentials


def read_secrets_file():
    """Parse /root/.zo_secrets into a dict. Read only, never written."""
    out = {}
    try:
        with open(SECRETS_FILE, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                out[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def _lookup(name, secrets_cache):
    v = os.environ.get(name)
    if v:
        return v, secrets_cache
    if secrets_cache is None:
        secrets_cache = read_secrets_file()
    return secrets_cache.get(name), secrets_cache


def credentials():
    """Return (key_id, key_secret). Exits with a fix, not a stack trace.

    Prefers the single console key HIGGSFIELD_API_KEY (formatted id:secret),
    falling back to the older HIGGSFIELD_API_KEY_ID / _SECRET pair.
    """
    cache = None
    single, cache = _lookup("HIGGSFIELD_API_KEY", cache)
    if single and ":" in single:
        key_id, key_secret = single.strip().split(":", 1)
        if key_id and key_secret:
            return key_id, key_secret

    vals = {}
    for name in ("HIGGSFIELD_API_KEY_ID", "HIGGSFIELD_API_KEY_SECRET"):
        vals[name], cache = _lookup(name, cache)

    missing = [k for k, v in vals.items() if not v]
    if missing:
        sys.exit(
            "missing credentials: set HIGGSFIELD_API_KEY (id:secret) or "
            + ", ".join(missing) + "\n"
            "  Create a key at https://console.higgsfield.ai, then add it in\n"
            "  Zo Settings > Advanced. Never write it into /root/.zo_secrets: that file\n"
            "  is rebuilt from Settings at every sandbox boot and the write is lost.\n"
            "  A service that booted before the key was added does not see it; restart it."
        )
    return vals["HIGGSFIELD_API_KEY_ID"], vals["HIGGSFIELD_API_KEY_SECRET"]


def auth_header(key_id, key_secret):
    return {"Authorization": f"Key {key_id}:{key_secret}"}


# --------------------------------------------------------------------------
# http


def request_json(url, headers, method="GET", payload=None, timeout=60):
    """Return (http_status, parsed_body_or_raw_text). Does not raise on 4xx/5xx.

    Error bodies carry the reason, so swallowing them behind an exception
    would throw away the only useful part of a failure.
    """
    data = None
    headers = dict(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            code = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        code = exc.code
    except urllib.error.URLError as exc:
        return 0, {"detail": f"network failure: {exc.reason}"}
    try:
        return code, json.loads(body)
    except ValueError:
        return code, body


def redact(text, *secrets):
    for s in secrets:
        if s:
            text = text.replace(s, "***")
    return text


# --------------------------------------------------------------------------
# registry and cost


def load_registry():
    with open(REGISTRY, encoding="utf-8") as fh:
        return json.load(fh)


def resolve_model(reg, name):
    models = reg["models"]
    if name in models:
        return name, models[name]
    sys.exit(
        f"unknown model '{name}'. Known: {', '.join(sorted(models))}\n"
        "  Add a new one to scripts/models.json using its endpoint from its\n"
        "  model page under https://docs.higgsfield.ai/docs/models/."
    )


def estimate_cost(spec, duration, variants):
    """USD for the whole submission. Variants multiply: N variants is N charges."""
    if spec["rate_unit"] == "per_second":
        per = spec["rate_usd"] * float(duration or spec.get("defaults", {}).get("duration", 5))
    else:
        per = spec["rate_usd"]
    return round(per * variants, 4)


# --------------------------------------------------------------------------
# ledger


def ledger_append(row):
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    row = dict(row)
    row["at_utc"] = datetime.now(timezone.utc).isoformat()
    with open(LEDGER_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# commands


def cmd_doctor(args):
    """Verify credentials at zero cost.

    A GET on a random request id cannot charge anything, and its status code
    separates the two failures that look identical from the outside:
      401 -> the key is wrong
      404 -> the key is good and that request simply does not exist
    """
    key_id, key_secret = credentials()
    probe = f"{API_ROOT}/requests/{uuid.uuid4()}/status"
    code, body = request_json(probe, auth_header(key_id, key_secret))

    print(f"credentials found: id ends ...{key_id[-4:]}, secret present")
    print(f"probe GET /requests/<random>/status -> HTTP {code}")
    if code == 404:
        print("OK: credentials accepted. A 404 here is the expected answer.")
        return 0
    if code == 401:
        print("FAIL: 401 Unauthorized. The key id or secret is wrong, or the key was rotated.")
        return 1
    if code == 0:
        print(f"FAIL: could not reach the API. {body}")
        return 2
    print(f"UNEXPECTED: HTTP {code}. Body: {redact(str(body), key_secret)[:400]}")
    return 2


def cmd_models(args):
    reg = load_registry()
    print(f"{'name':<20} {'kind':<6} {'rate':<22} endpoint")
    for name, spec in sorted(reg["models"].items()):
        unit = "per image" if spec["rate_unit"] == "per_image" else "per second"
        rate = f"${spec['rate_usd']:.4f} {unit}"
        print(f"{name:<20} {spec['kind']:<6} {rate:<22} {spec['endpoint']}")
    print()
    print(f"defaults: image={reg['default_image']}  video={reg['default_video']}")
    print("Rates are the published list; the account's real charge is authoritative.")
    return 0


def cmd_upload(args):
    """Put a local file in Higgsfield storage and print its public URL."""
    key_id, key_secret = credentials()
    path = os.path.abspath(args.file)
    if not os.path.isfile(path):
        sys.exit(f"no such file: {path}")
    ext = os.path.splitext(path)[1].lower()
    ctype = args.content_type or CONTENT_TYPES.get(ext)
    if not ctype:
        sys.exit(f"cannot infer content type for '{ext}'. Pass --content-type.")

    code, body = request_json(
        UPLOAD_URL, auth_header(key_id, key_secret), "POST", {"content_type": ctype}
    )
    if code != 200 or not isinstance(body, dict):
        sys.exit(f"upload-url failed HTTP {code}: {redact(str(body), key_secret)[:400]}")

    put_headers = dict(body.get("upload_headers") or {})
    put_headers.setdefault("Content-Type", ctype)
    with open(path, "rb") as fh:
        blob = fh.read()
    # Presigned URL. Deliberately no Authorization header: sending Higgsfield
    # credentials to third-party storage would leak them.
    req = urllib.request.Request(body["upload_url"], data=blob, headers=put_headers, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            if resp.status not in (200, 201, 204):
                sys.exit(f"PUT failed HTTP {resp.status}")
    except urllib.error.HTTPError as exc:
        sys.exit(f"PUT failed HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:300]}")
    except urllib.error.URLError as exc:
        sys.exit(f"PUT failed: {exc.reason}")

    print(body["public_url"])
    return 0


def poll(status_url, headers, timeout_s, label=""):
    """Poll to a terminal state with the documented backoff: 2s to 10s, jittered."""
    delay = 2.0
    started = time.monotonic()
    last = None
    while True:
        code, body = request_json(status_url, headers, timeout=30)
        if code == 401:
            return {"status": "failed", "error": "401 Unauthorized while polling"}
        if code == 404:
            return {"status": "failed", "error": "404 while polling: unknown request id"}
        if code == 200 and isinstance(body, dict):
            status = body.get("status")
            if status != last:
                elapsed = int(time.monotonic() - started)
                print(f"  [{elapsed:>4}s] {label}{status}")
                last = status
            if status in TERMINAL:
                return body
        # 5xx and network failures fall through and retry under the same backoff.
        if time.monotonic() - started > timeout_s:
            return {"status": "failed", "error": f"local timeout after {timeout_s}s",
                    "last_seen": last, "timed_out_locally": True}
        time.sleep(delay + random.uniform(0, 0.5))
        delay = min(delay * 1.5, 10.0)


def media_urls(result):
    """Pull every output URL out of a completed request body.

    The response schema carries four shapes: images[], video, audio, audios[].
    """
    urls = []
    for item in result.get("images") or []:
        if isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    for key in ("video", "audio"):
        item = result.get(key)
        if isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    for item in result.get("audios") or []:
        if isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    return urls


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "zo-hf-run/1"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(dest, "wb") as fh:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            fh.write(chunk)
    return os.path.getsize(dest)


def read_prompt(args):
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as fh:
            text = fh.read()
        # A saved prompt file is markdown with the prompt in a fenced block.
        blocks = re.findall(r"```(?:text)?\s*\n(.*?)```", text, re.S)
        return (max(blocks, key=len) if blocks else text).strip()
    if args.prompt:
        return args.prompt.strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    sys.exit("no prompt: pass --prompt, --prompt-file, or pipe it on stdin")


def cmd_generate(args):
    reg = load_registry()
    name, spec = resolve_model(reg, args.model or (reg["default_video"] if args.video else reg["default_image"]))
    prompt = read_prompt(args)
    if not prompt:
        sys.exit("prompt is empty")

    payload = dict(spec.get("defaults") or {})
    payload["prompt"] = prompt
    if args.duration is not None:
        payload["duration"] = args.duration
    if args.aspect:
        payload["aspect_ratio"] = args.aspect
    if args.resolution:
        payload["resolution"] = args.resolution
    if args.start_frame:
        key = spec.get("start_frame_param")
        if not key:
            sys.exit(f"model '{name}' takes no start frame. Use one that does, e.g. kling3-turbo-i2v.")
        payload[key] = args.start_frame
    for raw in args.param or []:
        k, _, v = raw.partition("=")
        if not _:
            sys.exit(f"--param needs key=value, got '{raw}'")
        try:
            payload[k] = json.loads(v)
        except ValueError:
            payload[k] = v
    # Drop keys the model does not declare, so a default meant for another
    # model cannot ride along into this request.
    known = set(spec.get("params") or [])
    if known:
        dropped = [k for k in payload if k not in known]
        for k in dropped:
            payload.pop(k)
        if dropped:
            print(f"dropped params not in {name}'s schema: {', '.join(sorted(dropped))}")

    variants = max(1, args.variants)
    cost = estimate_cost(spec, payload.get("duration"), variants)

    print(f"model:    {name}  ({spec['kind']})")
    print(f"endpoint: {spec['endpoint']}")
    print(f"variants: {variants}  (each one is a separate request and a separate charge)")
    print(f"estimate: ${cost:.4f} at the published list rate")

    if cost > args.max_cost:
        sys.exit(
            f"REFUSED: ${cost:.4f} exceeds --max-cost ${args.max_cost:.2f}.\n"
            "  Raise the cap deliberately if that is the intended spend."
        )

    if args.dry_run:
        print("\n--dry-run, nothing sent. Request body would be:")
        print(json.dumps(payload, indent=2))
        return 0

    key_id, key_secret = credentials()
    headers = auth_header(key_id, key_secret)
    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", prompt.lower())[:40].strip("-") or "untitled"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outdir = os.path.join(MEDIA_ROOT, f"{slug}-{stamp}")
    os.makedirs(outdir, exist_ok=True)
    batch = uuid.uuid4().hex[:8]

    saved, failures = [], []
    for i in range(1, variants + 1):
        tag = f"v{i}/{variants} " if variants > 1 else ""
        print(f"\nsubmitting {tag}...")
        code, body = request_json(spec["endpoint"], headers, "POST", payload, timeout=90)
        if code != 200 or not isinstance(body, dict) or not body.get("request_id"):
            detail = redact(str(body), key_secret)[:400]
            print(f"  submit failed HTTP {code}: {detail}")
            if code == 404:
                print("  A 404 here usually means the endpoint path moved. Check this model's")
                print("  page under docs.higgsfield.ai/docs/models/ and update models.json.")
            ledger_append({"kind": "submit_rejected", "batch": batch, "model": name,
                           "http": code, "estimate_usd": round(cost / variants, 4),
                           "detail": detail[:200]})
            failures.append(f"submit HTTP {code}")
            continue

        rid = body["request_id"]
        # INTENT first: the request is away and billable before any poll runs.
        ledger_append({"kind": "intent", "batch": batch, "request_id": rid, "model": name,
                       "variant": i, "estimate_usd": round(cost / variants, 4),
                       "duration_s": payload.get("duration"), "slug": slug})
        print(f"  request_id {rid}")

        status_url = body.get("status_url") or f"{API_ROOT}/requests/{rid}/status"
        result = poll(status_url, headers, args.timeout, label=tag)
        status = result.get("status", "unknown")

        ledger_append({"kind": "settled", "batch": batch, "request_id": rid, "model": name,
                       "variant": i, "status": status,
                       "estimate_usd": round(cost / variants, 4),
                       "refund_expected": status != "completed",
                       "error": result.get("error")})

        if status != "completed":
            note = result.get("error") or status
            print(f"  {status}: {note}")
            if result.get("timed_out_locally"):
                print(f"  The request may still be running. Check it: hf_run.py status {rid}")
            failures.append(f"{status}")
            continue

        urls = media_urls(result)
        if not urls:
            print("  completed but the response carried no media URL")
            failures.append("no media url")
            continue
        for n, url in enumerate(urls, 1):
            ext = os.path.splitext(url.split("?")[0])[1] or (".mp4" if spec["kind"] == "video" else ".jpg")
            suffix = f"-{n}" if len(urls) > 1 else ""
            dest = os.path.join(outdir, f"{slug}-{i:02d}{suffix}{ext}")
            size = download(url, dest)
            saved.append(dest)
            print(f"  saved {dest}  ({size/1024:.0f} KB)")

    print()
    if saved:
        print(f"{len(saved)} file(s) in {outdir}")
    if failures:
        print(f"{len(failures)} of {variants} did not produce a file: {', '.join(failures)}")
        print("Higgsfield refunds failed generations automatically.")
    print(f"ledger: {LEDGER_PATH}")
    if saved:
        print("\nNext: show the result in chat, then ask for a 1-10 score and log it with")
        print("  Skills/prompt-scoring/scripts/log_result.py")
    return 0 if saved else 1


def cmd_status(args):
    key_id, key_secret = credentials()
    url = f"{API_ROOT}/requests/{args.request_id}/status"
    code, body = request_json(url, auth_header(key_id, key_secret))
    print(f"HTTP {code}")
    print(json.dumps(body, indent=2) if isinstance(body, (dict, list))
          else redact(str(body), key_secret)[:1000])
    if isinstance(body, dict) and args.download:
        urls = media_urls(body)
        if not urls:
            print("no media URL on this request")
            return 1
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        for n, u in enumerate(urls, 1):
            ext = os.path.splitext(u.split("?")[0])[1] or ".bin"
            dest = os.path.join(MEDIA_ROOT, f"{args.request_id[:8]}-{n}{ext}")
            print(f"saved {dest}  ({download(u, dest)/1024:.0f} KB)")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Run a Higgsfield generation end to end.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Credentials: HIGGSFIELD_API_KEY_ID and HIGGSFIELD_API_KEY_SECRET,\n"
               "set in Zo Settings > Advanced. Never in /root/.zo_secrets.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="verify credentials, spends nothing").set_defaults(fn=cmd_doctor)
    sub.add_parser("models", help="list the model registry").set_defaults(fn=cmd_models)

    up = sub.add_parser("upload", help="upload a local file, print its public URL")
    up.add_argument("file")
    up.add_argument("--content-type", default=None)
    up.set_defaults(fn=cmd_upload)

    g = sub.add_parser("generate", help="submit, poll, download")
    g.add_argument("--prompt", default=None)
    g.add_argument("--prompt-file", default=None, help="markdown file; the longest fenced block wins")
    g.add_argument("--model", default=None)
    g.add_argument("--video", action="store_true", help="use the default video model")
    g.add_argument("--slug", default=None)
    g.add_argument("--variants", type=int, default=1, help="N variants is N requests and N charges")
    g.add_argument("--duration", type=int, default=None)
    g.add_argument("--aspect", default=None)
    g.add_argument("--resolution", default=None)
    g.add_argument("--start-frame", default=None, help="public URL from `upload`")
    g.add_argument("--param", action="append", help="raw key=value passthrough")
    g.add_argument("--max-cost", type=float, default=DEFAULT_MAX_COST)
    g.add_argument("--timeout", type=int, default=900, help="local polling timeout, seconds")
    g.add_argument("--dry-run", action="store_true")
    g.set_defaults(fn=cmd_generate)

    s = sub.add_parser("status", help="inspect one request id")
    s.add_argument("request_id")
    s.add_argument("--download", action="store_true")
    s.set_defaults(fn=cmd_status)

    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
