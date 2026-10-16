#!/usr/bin/env python3
"""Check how closely a built page matches a design system."""
import argparse
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime

LIBRARY = os.environ.get("DESIGN_LIBRARY", "/home/workspace/Design/Library")

try:
    from PIL import Image
    from colorthief import ColorThief
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "colorthief", "-q"])
    from PIL import Image
    from colorthief import ColorThief


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def color_distance(c1: tuple, c2: tuple) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def find_closest_color(target: tuple, palette: list) -> tuple[str, float]:
    best_hex = "#000000"
    best_dist = float("inf")
    for hex_color in palette:
        try:
            rgb = hex_to_rgb(hex_color)
            d = color_distance(target, rgb)
            if d < best_dist:
                best_dist = d
                best_hex = hex_color
        except Exception:
            continue
    return best_hex, best_dist


def screenshot_url(url: str) -> str:
    tmp = tempfile.mktemp(suffix=".png")
    subprocess.run(["/usr/local/bin/agent-browser", "open", url], capture_output=True, timeout=15)
    time.sleep(3)
    result = subprocess.run(
        ["/usr/local/bin/agent-browser", "screenshot", tmp, "--full-page"],
        capture_output=True, timeout=15,
    )
    if not os.path.exists(tmp):
        sys.exit(f"Screenshot failed: {result.stderr.decode()}")
    return tmp


def extract_dominant_colors(image_path: str, count: int = 10) -> list[tuple]:
    ct = ColorThief(image_path)
    palette = ct.get_palette(color_count=count, quality=1)
    return palette


def parse_design_colors(design_path: str) -> list[str]:
    with open(design_path) as f:
        text = f.read()
    return re.findall(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', text)


def resolve_path(name: str) -> str:
    if os.path.exists(name):
        return name
    candidate = os.path.join(LIBRARY, name.lower(), "DESIGN.md")
    if os.path.exists(candidate):
        return candidate
    sys.exit(f"Cannot find DESIGN.md for '{name}'.")


def run_check(url_or_image: str, design: str, save_report: bool = False) -> dict:
    design_path = resolve_path(design)
    design_colors = ["#" + c for c in parse_design_colors(design_path)]

    if not design_colors:
        print("Warning: No hex colors found in DESIGN.md. Fidelity check may be inaccurate.")
        design_colors = ["#000000", "#FFFFFF"]

    # Get screenshot
    if url_or_image.startswith("http"):
        print(f"Screenshotting: {url_or_image}")
        img_path = screenshot_url(url_or_image)
        source = url_or_image
    else:
        img_path = url_or_image
        source = img_path

    print("Extracting dominant colors from screenshot...")
    dominant = extract_dominant_colors(img_path)

    matches = []
    total_dist = 0
    MAX_OK_DIST = 60  # euclidean RGB distance threshold

    for rgb in dominant:
        closest_hex, dist = find_closest_color(rgb, design_colors)
        match_pct = max(0, 100 - (dist / MAX_OK_DIST) * 100)
        found_hex = "#{:02X}{:02X}{:02X}".format(*rgb)
        matches.append({
            "found": found_hex,
            "closest_design": closest_hex,
            "distance": round(dist, 1),
            "match_pct": round(match_pct, 1),
        })
        total_dist += dist

    avg_dist = total_dist / len(dominant) if dominant else 999
    overall_score = max(0, round(100 - (avg_dist / MAX_OK_DIST) * 100))

    result = {
        "source": source,
        "design": design_path,
        "overall_score": overall_score,
        "color_matches": matches,
        "timestamp": datetime.now().isoformat(),
    }

    # Report
    print(f"\n{'='*50}")
    print(f"FIDELITY CHECK REPORT")
    print(f"{'='*50}")
    print(f"Source:  {source}")
    print(f"Design:  {design_path}")
    print(f"Score:   {overall_score}/100")
    print(f"Rating:  {'Excellent' if overall_score >= 85 else 'Good' if overall_score >= 70 else 'Fair' if overall_score >= 50 else 'Poor'}")
    print(f"\nTop color comparisons:")
    for m in matches[:6]:
        bar = "█" * int(m['match_pct'] / 10) + "░" * (10 - int(m['match_pct'] / 10))
        print(f"  {m['found']} → {m['closest_design']}  [{bar}] {m['match_pct']:.0f}%")

    if save_report:
        brand_dir = os.path.basename(os.path.dirname(design_path))
        report_path = os.path.join(LIBRARY, brand_dir, f"fidelity-{datetime.now().strftime('%Y%m%d-%H%M')}.md")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            f.write(f"# Fidelity Check — {source}\n")
            f.write(f"Score: **{overall_score}/100**\n\n")
            f.write(f"Design system: `{design_path}`\n\n")
            f.write("## Color Matches\n\n")
            for m in matches:
                f.write(f"- Found `{m['found']}` → Design `{m['closest_design']}` — {m['match_pct']:.0f}% match (dist: {m['distance']})\n")
        print(f"\nReport saved: {report_path}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check design fidelity of a built page")
    parser.add_argument("source", help="URL or screenshot path to check")
    parser.add_argument("design", help="Brand name or path to DESIGN.md")
    parser.add_argument("--report", action="store_true", help="Save a fidelity report markdown file")
    args = parser.parse_args()

    run_check(args.source, args.design, args.report)
