#!/usr/bin/env python3
"""Append a scored generation result to the prompt results log.

One record per generation the user rated. Score is 1-10. The raw 'why' text is
always preserved verbatim; tags are a derived index over it, never a
replacement for it.
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone

LOG_DIR = os.environ.get("PROMPT_RESULTS_DIR", "/home/workspace/Content/prompt-results")
LOG_PATH = os.path.join(LOG_DIR, "results.jsonl")
TAGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "failure-tags.md")

MEDIA = ("video", "image")
MODES = ("reference", "describe")


def known_tags():
    """Parse the controlled vocabulary out of failure-tags.md.

    Tags are the leading backticked token on any table row. Returns an empty
    set if the file is unreadable, which makes tag validation fail OPEN: a
    missing vocabulary file must not block logging a real result.
    """
    try:
        with open(os.path.normpath(TAGS_PATH), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return set()
    tags = set()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("| `"):
            continue
        token = line.split("`")[1].strip()
        if token:
            tags.add(token)
    return tags


def main():
    p = argparse.ArgumentParser(description="Log a scored generation result.")
    p.add_argument("--medium", required=True, choices=MEDIA)
    p.add_argument("--slug", required=True, help="Short name of the concept")
    p.add_argument("--score", required=True, type=int, help="the user's rating, 1-10")
    p.add_argument("--why", required=True, help="the user's own words, verbatim")
    p.add_argument("--mode", choices=MODES, default=None)
    p.add_argument("--generator", default=None, help="higgsfield, zo, runway, ...")
    p.add_argument("--model", default=None)
    p.add_argument("--register", default=None, help="locked, gentle-handheld, editorial, ...")
    p.add_argument("--duration", type=float, default=None, help="Seconds, video only")
    p.add_argument("--aspect", default=None)
    p.add_argument("--prompt-file", default=None)
    p.add_argument("--output-file", default=None)
    p.add_argument("--tags", default="", help="Comma-separated, from references/failure-tags.md")
    p.add_argument("--allow-new-tags", action="store_true",
                   help="Permit tags outside the controlled vocabulary")
    args = p.parse_args()

    if not 1 <= args.score <= 10:
        sys.exit(f"score must be 1-10, got {args.score}")
    if not args.why.strip():
        sys.exit("why must not be empty: an unexplained score teaches nothing")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    vocab = known_tags()
    if vocab and not args.allow_new_tags:
        unknown = [t for t in tags if t not in vocab]
        if unknown:
            sys.exit(
                f"unknown tags {unknown}. Use one from references/failure-tags.md, "
                "or pass --allow-new-tags and add it to that file in the same change."
            )

    record = {
        "id": uuid.uuid4().hex[:12],
        "logged_utc": datetime.now(timezone.utc).isoformat(),
        "medium": args.medium,
        "slug": args.slug,
        "mode": args.mode,
        "generator": args.generator,
        "model": args.model,
        "register": args.register,
        "duration_s": args.duration,
        "aspect": args.aspect,
        "prompt_file": args.prompt_file,
        "output_file": args.output_file,
        "score": args.score,
        "why": args.why.strip(),
        "tags": tags,
    }

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"logged {record['id']}  {args.medium}/{args.slug}  score {args.score}/10")
    print(f"  tags: {', '.join(tags) if tags else '(none)'}")
    print(f"  -> {LOG_PATH}")


if __name__ == "__main__":
    main()
