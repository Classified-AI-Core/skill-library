#!/usr/bin/env python3
"""Export a DESIGN.md to CSS variables and/or Tailwind config tokens."""
import argparse
import json
import os
import re
import sys
from pathlib import Path

LIBRARY = os.environ.get("DESIGN_LIBRARY", "/home/workspace/Design/Library")

HEX_INLINE = re.compile(r'`(#[0-9a-fA-F]{3,8})`')
NAMED_COLOR = re.compile(
    r'\*\*?([^*:]+?)\*\*?[:\s]+`(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|[\w-]+)`',
    re.IGNORECASE,
)
FONT_LINE = re.compile(r'\*\*([^*]+)\*\*(?:\s*[:\-–]?\s*[`\'"]?([A-Za-z][A-Za-z0-9 ,_-]+)[`\'"]?)?')


def to_token_name(label: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')


def parse_design_md(path: str) -> dict:
    with open(path) as f:
        text = f.read()

    colors = {}
    fonts = {}
    radii = []
    current_section = ""

    for line in text.splitlines():
        h = line.lstrip('#').strip().lower()
        if line.startswith('#'):
            current_section = h
            continue

        # Named color patterns
        m = NAMED_COLOR.search(line)
        if m and 'color' in current_section or 'palette' in current_section or 'brand' in current_section:
            if m:
                name = to_token_name(m.group(1))
                val = m.group(2).strip()
                if val and name:
                    colors[name] = val

        # Hex colors in backticks
        for hex_val in HEX_INLINE.findall(line):
            if hex_val not in colors.values():
                label = line.split('`')[0].strip().lstrip('-* ').lower()
                key = to_token_name(label) if label else f"color-{len(colors)}"
                colors.setdefault(key, hex_val)

        # Fonts
        if 'font' in current_section or 'typography' in current_section:
            fm = FONT_LINE.search(line)
            if fm:
                role = to_token_name(fm.group(1))
                font_name = fm.group(2).strip().strip("'\"") if fm.group(2) else None
                if font_name and len(font_name) < 60:
                    fonts[role] = font_name

        # Border radius
        rm = re.search(r'`([\d.]+(?:px|rem|em|%))(?:\s|`)', line)
        if rm and ('radius' in current_section or 'shape' in current_section):
            radii.append(rm.group(1))

    return {"colors": colors, "fonts": fonts, "radii": radii}


def generate_css(tokens: dict) -> str:
    lines = [":root {"]

    if tokens["colors"]:
        lines.append("  /* Colors */")
        for name, val in tokens["colors"].items():
            lines.append(f"  --color-{name}: {val};")

    if tokens["fonts"]:
        lines.append("\n  /* Typography */")
        for role, font in tokens["fonts"].items():
            lines.append(f"  --font-{role}: '{font}', sans-serif;")

    if tokens["radii"]:
        lines.append("\n  /* Border Radius */")
        for i, r in enumerate(tokens["radii"]):
            suffix = ["sm", "md", "lg", "xl", "2xl"][i] if i < 5 else str(i)
            lines.append(f"  --radius-{suffix}: {r};")

    lines.append("}")
    return "\n".join(lines)


def generate_tailwind(tokens: dict) -> str:
    config = {
        "theme": {
            "extend": {}
        }
    }

    if tokens["colors"]:
        config["theme"]["extend"]["colors"] = {
            name: val for name, val in tokens["colors"].items()
        }

    if tokens["fonts"]:
        config["theme"]["extend"]["fontFamily"] = {
            role: [font, "sans-serif"] for role, font in tokens["fonts"].items()
        }

    if tokens["radii"]:
        suffixes = ["sm", "md", "lg", "xl", "2xl"]
        config["theme"]["extend"]["borderRadius"] = {
            suffixes[i] if i < 5 else str(i): r
            for i, r in enumerate(tokens["radii"])
        }

    return (
        "/** @type {import('tailwindcss').Config} */\n"
        "module.exports = " + json.dumps(config, indent=2) + ";"
    )


def resolve_path(name: str) -> str:
    if os.path.exists(name):
        return name
    candidate = os.path.join(LIBRARY, name.lower(), "DESIGN.md")
    if os.path.exists(candidate):
        return candidate
    sys.exit(f"Cannot find DESIGN.md for '{name}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export DESIGN.md to CSS variables and Tailwind tokens")
    parser.add_argument("design", help="Brand name or path to DESIGN.md")
    parser.add_argument("--format", choices=["css", "tailwind", "both"], default="both")
    parser.add_argument("--output", help="Output directory (default: next to DESIGN.md)")
    args = parser.parse_args()

    path = resolve_path(args.design)
    tokens = parse_design_md(path)

    out_dir = args.output or os.path.dirname(path)
    os.makedirs(out_dir, exist_ok=True)

    if args.format in ("css", "both"):
        css = generate_css(tokens)
        css_path = os.path.join(out_dir, "tokens.css")
        with open(css_path, "w") as f:
            f.write(css)
        print(f"CSS tokens: {css_path}")
        print(css[:400])

    if args.format in ("tailwind", "both"):
        tw = generate_tailwind(tokens)
        tw_path = os.path.join(out_dir, "tailwind.tokens.js")
        with open(tw_path, "w") as f:
            f.write(tw)
        print(f"\nTailwind tokens: {tw_path}")
        print(tw[:400])

    print(f"\nExtracted: {len(tokens['colors'])} colors, {len(tokens['fonts'])} fonts, {len(tokens['radii'])} radii")
