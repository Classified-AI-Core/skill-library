#!/usr/bin/env python3
"""Read the results log and emit a compact lessons block.

Consumed by video-prompt and image-prompt BEFORE building a new prompt.
A log nobody reads is not a control, so this is the half that matters.

Discipline: never state a pattern below --min-n. Anything thinner is listed
under INSUFFICIENT EVIDENCE with its actual count, so a single bad clip can
never become a standing rule.
"""

import argparse
import json
import os
import statistics
import sys
from collections import defaultdict

LOG_PATH = os.environ.get("PROMPT_RESULTS_LOG", "/home/workspace/Content/prompt-results/results.jsonl")


def load(medium=None):
    if not os.path.exists(LOG_PATH):
        return []
    rows = []
    with open(LOG_PATH, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                print(f"warning: skipping malformed line {n}", file=sys.stderr)
                continue
            if medium and r.get("medium") != medium:
                continue
            rows.append(r)
    return rows


def mean(xs):
    return statistics.mean(xs) if xs else None


def tag_effects(rows, min_n):
    """Score drag per tag: mean score with the tag vs mean score without it.

    A tag present on every row has no comparison group; report it as
    ubiquitous rather than inventing a delta against nothing.
    """
    all_tags = sorted({t for r in rows for t in r.get("tags", [])})
    strong, weak = [], []
    for tag in all_tags:
        present = [r["score"] for r in rows if tag in r.get("tags", [])]
        absent = [r["score"] for r in rows if tag not in r.get("tags", [])]
        entry = {"tag": tag, "n": len(present), "mean_with": mean(present),
                 "mean_without": mean(absent)}
        entry["delta"] = (
            round(entry["mean_with"] - entry["mean_without"], 2)
            if absent else None
        )
        (strong if len(present) >= min_n else weak).append(entry)
    strong.sort(key=lambda e: (e["delta"] is None, e["delta"]))
    weak.sort(key=lambda e: -e["n"])
    return strong, weak


def dimension(rows, field, min_n):
    buckets = defaultdict(list)
    for r in rows:
        v = r.get(field)
        if v is not None:
            buckets[str(v)].append(r["score"])

    strong = {k: (len(v), round(mean(v), 2)) for k, v in buckets.items() if len(v) >= min_n}
    weak = {k: (len(v), round(mean(v), 2)) for k, v in buckets.items() if len(v) < min_n}
    return strong, weak


def main():
    p = argparse.ArgumentParser(description="Emit lessons from the results log.")
    p.add_argument("--medium", choices=("video", "image"), default=None)
    p.add_argument("--min-n", type=int, default=3,
                   help="Minimum observations before a pattern may be stated")
    p.add_argument("--recent", type=int, default=5,
                   help="How many recent low scorers to print verbatim")
    args = p.parse_args()

    rows = load(args.medium)
    label = args.medium or "all media"

    if not rows:
        print(f"PROMPT LESSONS ({label}): no results logged yet.")
        print("Nothing to apply. Build from the skill defaults and log the score afterward.")
        return

    scores = [r["score"] for r in rows]
    print(f"PROMPT LESSONS ({label})")
    print(f"n={len(rows)}  mean={mean(scores):.2f}/10  "
          f"median={statistics.median(scores)}  range={min(scores)}-{max(scores)}")
    print(f"Evidence threshold: a pattern is stated only at n>={args.min_n}.")
    print()

    strong_tags, weak_tags = tag_effects(rows, args.min_n)
    if strong_tags:
        print("ESTABLISHED PATTERNS (apply these)")
        for e in strong_tags:
            if e["delta"] is None:
                print(f"  {e['tag']}: present on all {e['n']} rows, no comparison group")
            else:
                direction = "drags" if e["delta"] < 0 else "lifts"
                print(f"  {e['tag']}: n={e['n']}, {direction} score by {abs(e['delta'])} "
                      f"({e['mean_with']:.1f} with vs {e['mean_without']:.1f} without)")
        print()

    for field in ("mode", "generator", "model", "register"):
        strong, _ = dimension(rows, field, args.min_n)
        if len(strong) >= 2:
            ranked = sorted(strong.items(), key=lambda kv: -kv[1][1])
            line = ", ".join(f"{k} {v[1]}/10 (n={v[0]})" for k, v in ranked)
            print(f"BY {field.upper()}: {line}")
    print()

    low = sorted([r for r in rows if r["score"] <= 5],
                 key=lambda r: r["logged_utc"], reverse=True)[:args.recent]
    if low:
        print("RECENT FAILURES, IN THE USER'S WORDS (do not repeat these)")
        for r in low:
            print(f"  [{r['score']}/10] {r['slug']}: {r['why']}")
        print()

    high = sorted([r for r in rows if r["score"] >= 8],
                  key=lambda r: r["logged_utc"], reverse=True)[:args.recent]
    if high:
        print("RECENT WINS, IN THE USER'S WORDS (reuse what made these work)")
        for r in high:
            print(f"  [{r['score']}/10] {r['slug']}: {r['why']}")
        print()

    if weak_tags:
        print(f"INSUFFICIENT EVIDENCE (below n={args.min_n}, do NOT treat as rules)")
        print("  " + ", ".join(f"{e['tag']} (n={e['n']})" for e in weak_tags))


if __name__ == "__main__":
    main()
