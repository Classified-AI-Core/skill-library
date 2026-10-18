#!/usr/bin/env python3
"""AI-powered design critique: compare a screenshot against a DESIGN.md."""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime

LIBRARY = os.environ.get("DESIGN_LIBRARY", "/home/workspace/Design/Library")
ZO_API = "https://api.zo.computer/zo/ask"
MODEL = os.environ.get("CRITIQUE_MODEL", "")

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


def screenshot_url(url: str) -> str:
    tmp = tempfile.mktemp(suffix=".png")
    subprocess.run(["/usr/local/bin/agent-browser", "open", url], capture_output=True, timeout=15)
    time.sleep(3)
    result = subprocess.run(
        ["/usr/local/bin/agent-browser", "screenshot", tmp],
        capture_output=True, timeout=15,
    )
    if not os.path.exists(tmp):
        sys.exit(f"Screenshot failed: {result.stderr.decode()}")
    return tmp


def resolve_path(name: str) -> str:
    if os.path.exists(name):
        return name
    candidate = os.path.join(LIBRARY, name.lower(), "DESIGN.md")
    if os.path.exists(candidate):
        return candidate
    sys.exit(f"Cannot find DESIGN.md for '{name}'.")


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def run_critique(source: str, design: str, output: str = None) -> str:
    design_path = resolve_path(design)

    with open(design_path) as f:
        design_text = f.read()

    if source.startswith("http"):
        print(f"Screenshotting: {source}")
        img_path = screenshot_url(source)
        source_label = source
    else:
        img_path = source
        source_label = os.path.basename(source)

    print("Encoding screenshot...")
    img_b64 = encode_image(img_path)

    prompt = f"""You are a senior UI/UX designer reviewing a web page against a brand design system.

DESIGN SYSTEM:
{design_text[:3000]}

TASK:
Review the attached screenshot of {source_label} against this design system.

Provide a structured critique covering:
1. **Color consistency** — Are the colors on the page matching the design system palette? List specific mismatches.
2. **Typography** — Are the right fonts being used? Are sizing and weights consistent with the spec?
3. **Spacing & layout** — Does the spacing feel consistent? Any obvious alignment or density issues?
4. **Component patterns** — Do buttons, cards, inputs, etc. match the brand's established patterns?
5. **Overall fidelity score** — 0–100 score with one-sentence justification.
6. **Top 3 improvements** — The most impactful changes to better align with the design system.

Be specific and actionable. Reference exact colors (hex values) and font names where possible.
Screenshot is attached as base64 (PNG).
"""

    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print("ZO_CLIENT_IDENTITY_TOKEN not set — writing prompt to file for manual use.")
        prompt_path = tempfile.mktemp(suffix="-critique-prompt.txt")
        with open(prompt_path, "w") as f:
            f.write(prompt)
        print(f"Prompt saved: {prompt_path}")
        return prompt_path

    print("Running AI critique...")
    resp = requests.post(
        ZO_API,
        headers={
            "authorization": token,
            "content-type": "application/json",
        },
        json={"input": prompt, **({"model_name": MODEL} if MODEL else {})},
        timeout=120,
    )

    if resp.status_code != 200:
        sys.exit(f"API error {resp.status_code}: {resp.text}")

    critique_text = resp.json().get("output", "No output received.")

    brand_dir = os.path.basename(os.path.dirname(design_path))
    dest = output or os.path.join(
        LIBRARY, "critiques",
        f"{brand_dir}-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
    )
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    report = f"# Design Critique — {source_label}\n"
    report += f"Design system: `{design_path}`\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    report += "---\n\n"
    report += critique_text

    with open(dest, "w") as f:
        f.write(report)

    print(f"\n{'='*60}")
    print("CRITIQUE REPORT")
    print(f"{'='*60}")
    print(critique_text)
    print(f"\nSaved: {dest}")
    return dest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-powered design critique against a DESIGN.md")
    parser.add_argument("source", help="URL or screenshot path to critique")
    parser.add_argument("design", help="Brand name or path to DESIGN.md")
    parser.add_argument("--output", help="Output path for critique report")
    args = parser.parse_args()

    run_critique(args.source, args.design, args.output)
