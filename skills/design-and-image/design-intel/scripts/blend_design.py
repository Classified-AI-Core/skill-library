#!/usr/bin/env python3
"""Blend two DESIGN.md files into a hybrid design system."""
import argparse
import os
import re
import sys
from datetime import datetime

LIBRARY = os.environ.get("DESIGN_LIBRARY", "/home/workspace/Design/Library")

SECTIONS = ["color", "typography", "font", "spacing", "component", "shape", "border", "shadow"]


def resolve_path(name: str) -> str:
    if os.path.exists(name):
        return name
    candidate = os.path.join(LIBRARY, name.lower(), "DESIGN.md")
    if os.path.exists(candidate):
        return candidate
    sys.exit(f"Cannot find DESIGN.md for '{name}'. Run fetch_design.py first.")


def parse_sections(text: str) -> dict[str, str]:
    """Split markdown into H2 sections."""
    parts = re.split(r'^(##\s+.+)$', text, flags=re.MULTILINE)
    sections = {"header": parts[0] if parts else ""}
    i = 1
    while i < len(parts) - 1:
        title = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        key = title.lstrip("#").strip().lower()
        sections[key] = title + content
        i += 2
    return sections


def pick_section(key: str, secs_a: dict, secs_b: dict, from_a: list, from_b: list) -> str:
    for hint in from_a:
        if hint.lower() in key:
            return secs_a.get(key, secs_b.get(key, ""))
    for hint in from_b:
        if hint.lower() in key:
            return secs_b.get(key, secs_a.get(key, ""))
    # Default: prefer A
    return secs_a.get(key, secs_b.get(key, ""))


def blend(path_a: str, path_b: str, from_a: list, from_b: list, output: str = None) -> str:
    with open(path_a) as f:
        text_a = f.read()
    with open(path_b) as f:
        text_b = f.read()

    secs_a = parse_sections(text_a)
    secs_b = parse_sections(text_b)

    name_a = os.path.basename(os.path.dirname(path_a)) or "Design A"
    name_b = os.path.basename(os.path.dirname(path_b)) or "Design B"

    header = f"# Hybrid: {name_a.title()} + {name_b.title()}\n"
    header += f"> Blended from {name_a} (typography: {'A' if 'typography' in from_a or 'font' in from_a else 'B'}) "
    header += f"and {name_b} (colors: {'B' if 'color' in from_b or 'colours' in from_b else 'A'})\n"
    header += f"> Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n"

    all_keys = list(dict.fromkeys(list(secs_a.keys()) + list(secs_b.keys())))
    all_keys = [k for k in all_keys if k != "header"]

    parts = [header]
    for key in all_keys:
        section = pick_section(key, secs_a, secs_b, from_a, from_b)
        if section.strip():
            parts.append(section.strip() + "\n\n")

    result = "\n".join(parts)

    if output:
        dest = output
    else:
        blend_name = f"{name_a.lower()}-{name_b.lower()}"
        dest = os.path.join(LIBRARY, "blended", blend_name, "DESIGN.md")

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(result)

    print(f"Blended DESIGN.md saved: {dest}")
    print(f"  Sections from {name_a}: {from_a or ['all defaults']}")
    print(f"  Sections from {name_b}: {from_b or []}")
    return dest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Blend two DESIGN.md files into a hybrid",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python blend_design.py stripe linear
  python blend_design.py stripe linear --typography-from stripe --colors-from linear
  python blend_design.py Design/Library/stripe/DESIGN.md Design/Library/linear/DESIGN.md --output Projects/mysite/DESIGN.md
""",
    )
    parser.add_argument("design_a", help="First brand name or path to DESIGN.md")
    parser.add_argument("design_b", help="Second brand name or path to DESIGN.md")
    parser.add_argument(
        "--typography-from", metavar="BRAND",
        help="Take typography/fonts from this brand (a or b, or full name)"
    )
    parser.add_argument(
        "--colors-from", metavar="BRAND",
        help="Take colors from this brand (a or b, or full name)"
    )
    parser.add_argument("--output", help="Output path for blended DESIGN.md")
    args = parser.parse_args()

    path_a = resolve_path(args.design_a)
    path_b = resolve_path(args.design_b)

    from_a, from_b = [], []

    def resolve_brand(val, design_a_name, design_b_name):
        if val in ("a", "1", design_a_name.lower()):
            return "a"
        return "b"

    name_a = os.path.basename(os.path.dirname(path_a))
    name_b = os.path.basename(os.path.dirname(path_b))

    if args.typography_from:
        side = resolve_brand(args.typography_from, name_a, name_b)
        (from_a if side == "a" else from_b).extend(["typography", "font"])

    if args.colors_from:
        side = resolve_brand(args.colors_from, name_a, name_b)
        (from_a if side == "a" else from_b).extend(["color", "palette", "colour"])

    blend(path_a, path_b, from_a, from_b, args.output)
