#!/usr/bin/env python3
"""Generate a Claude Design-ready brief from a DESIGN.md file."""
import argparse
import os
import re
import sys
from datetime import datetime

LIBRARY = os.environ.get("DESIGN_LIBRARY", "/home/workspace/Design/Library")

TEMPLATES = {
    "dashboard": {
        "label": "Analytics Dashboard",
        "description": "A data-rich dashboard with charts, KPI cards, filters, and a sidebar nav.",
        "components": ["sidebar navigation", "KPI stat cards", "line/bar charts", "data table", "filter bar", "header with user menu"],
        "layout": "sidebar + main content area, responsive",
    },
    "landing": {
        "label": "Landing Page",
        "description": "A marketing landing page with hero, features, social proof, and CTA.",
        "components": ["hero section", "feature grid", "testimonials", "pricing table", "CTA section", "footer"],
        "layout": "full-width single column, max-width container",
    },
    "auth": {
        "label": "Auth Flow",
        "description": "Login, signup, and password reset screens.",
        "components": ["centered card", "email/password inputs", "social login buttons", "error states", "forgot password link"],
        "layout": "centered card on minimal background",
    },
    "component": {
        "label": "Component Library",
        "description": "A component showcase with buttons, inputs, cards, and modals.",
        "components": ["button variants", "form inputs", "cards", "modals", "badges", "alerts", "tables"],
        "layout": "stacked sections with spacing",
    },
    "mobile": {
        "label": "Mobile App Screen",
        "description": "A mobile-first app screen with bottom nav and list views.",
        "components": ["top header bar", "list items", "bottom navigation", "FAB button", "pull-to-refresh"],
        "layout": "375px mobile viewport, bottom tab bar",
    },
}


def resolve_path(name: str) -> str:
    if os.path.exists(name):
        return name
    candidate = os.path.join(LIBRARY, name.lower(), "DESIGN.md")
    if os.path.exists(candidate):
        return candidate
    sys.exit(f"Cannot find DESIGN.md for '{name}'.")


def extract_summary(text: str) -> dict:
    colors = re.findall(r'`(#[0-9a-fA-F]{3,8})`', text)[:6]
    fonts = re.findall(r'\*\*([A-Za-z][A-Za-z0-9 ]+)\*\*', text)
    fonts = [f for f in fonts if 2 < len(f) < 40][:3]
    radii = re.findall(r'`([\d.]+(?:px|rem))`', text)[:3]
    name_m = re.search(r'^#\s+(.+)', text, re.MULTILINE)
    name = name_m.group(1).strip() if name_m else "Unknown"
    return {"name": name, "colors": colors, "fonts": fonts, "radii": radii}


def build_brief(design_path: str, template_key: str, output: str = None) -> str:
    with open(design_path) as f:
        design_text = f.read()

    tmpl = TEMPLATES[template_key]
    summary = extract_summary(design_text)
    brand_dir = os.path.basename(os.path.dirname(design_path))

    color_block = "\n".join(f"  - {c}" for c in summary["colors"]) if summary["colors"] else "  - (see DESIGN.md)"
    font_block = ", ".join(summary["fonts"]) if summary["fonts"] else "(see DESIGN.md)"
    radius_block = ", ".join(summary["radii"]) if summary["radii"] else "default"

    brief = f"""# Claude Design Brief — {summary['name']} × {tmpl['label']}
Generated: {datetime.now().strftime('%Y-%m-%d')}

---

## Paste this prompt into Claude Design:

---

**Design a {tmpl['description']}**

Apply the {summary['name']} design system with these exact specifications:

### Colors
{color_block}

### Typography
- Font(s): {font_block}
- Use appropriate weight hierarchy (bold headers, regular body, medium labels)

### Border Radius
- {radius_block}

### Layout
- {tmpl['layout']}

### Required Components
{chr(10).join(f'- {c}' for c in tmpl['components'])}

### Design Principles
- Clean, professional, high contrast
- Consistent spacing (8px base unit)
- Accessible (WCAG AA minimum)
- Match the brand's established visual language exactly

### Full Design Reference
(Paste the contents of DESIGN.md below this line)

---

{design_text}

---
"""

    if output:
        dest = output
    else:
        dest = os.path.join(LIBRARY, brand_dir, f"brief-{template_key}.md")

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(brief)

    print(f"Brief saved: {dest}")
    print(f"\n{'='*60}")
    print(f"CLAUDE DESIGN PROMPT ({len(brief)} chars)")
    print(f"{'='*60}")
    print(brief[:800])
    print("...(truncated — see full file)")
    return dest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a Claude Design-ready brief from DESIGN.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Templates: {', '.join(TEMPLATES.keys())}",
    )
    parser.add_argument("design", help="Brand name or path to DESIGN.md")
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        default="dashboard",
        help="UI template type",
    )
    parser.add_argument("--output", help="Output path for brief.md")
    args = parser.parse_args()

    path = resolve_path(args.design)
    build_brief(path, args.template, args.output)
