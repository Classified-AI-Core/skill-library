#!/usr/bin/env python3
"""Clone a website's design system by extracting colors, typography, spacing, and components."""
import argparse
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "-q"])
    import requests
    from bs4 import BeautifulSoup

LIBRARY = os.path.join(os.environ.get("DESIGN_LIBRARY", "/home/workspace/Design/Library"), "cloned")

COLOR_PATTERN = re.compile(
    r'(?:color|background|border|fill|stroke|shadow)[^:]*:\s*'
    r'(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|hsla?\([^)]+\))',
    re.IGNORECASE,
)
HEX_PATTERN = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')
FONT_PATTERN = re.compile(r'font-family:\s*([^;}\n]+)', re.IGNORECASE)
FONT_SIZE_PATTERN = re.compile(r'font-size:\s*([\d.]+(?:px|rem|em))', re.IGNORECASE)
FONT_WEIGHT_PATTERN = re.compile(r'font-weight:\s*(\d+|bold|normal|light)', re.IGNORECASE)
RADIUS_PATTERN = re.compile(r'border-radius:\s*([\d.]+(?:px|rem|em|%))', re.IGNORECASE)
SPACING_PATTERN = re.compile(r'(?:margin|padding):\s*([\d.]+(?:px|rem|em))\b', re.IGNORECASE)

COMPONENT_SELECTORS = {
    "button": [r'\.btn\b', r'\bbutton\b', r'\[class\*="button"\]', r'\[class\*="btn"\]'],
    "card": [r'\.card\b', r'\[class\*="card"\]'],
    "nav": [r'\bnav\b', r'\.navbar\b', r'\.header\b', r'\[class\*="nav"\]'],
    "input": [r'\binput\b', r'\.input\b', r'\[class\*="input"\]', r'\[class\*="field"\]'],
    "modal": [r'\.modal\b', r'\[class\*="modal"\]', r'\[class\*="dialog"\]'],
    "badge": [r'\.badge\b', r'\[class\*="badge"\]', r'\[class\*="tag"\]', r'\[class\*="chip"\]'],
}


def fetch_css(url: str, base_url: str, session: requests.Session) -> str:
    try:
        r = session.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception:
        return ""


def extract_google_fonts(html: str) -> list[str]:
    pattern = re.compile(r'fonts\.googleapis\.com/css[^"\']+family=([^&"\']+)', re.IGNORECASE)
    fonts = []
    for m in pattern.finditer(html):
        raw = urllib.parse.unquote(m.group(1))
        fonts.extend(re.split(r'[|+]', raw.split(":")[0].replace("+", " ")))
    return list(set(f.strip() for f in fonts if f.strip()))


def normalize_hex(h: str) -> str:
    h = h.strip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return f"#{h.upper()}"


def dedupe_colors(colors: list[str], max_colors: int = 20) -> list[str]:
    seen = {}
    for c in colors:
        h = c.upper()
        seen[h] = seen.get(h, 0) + 1
    return [c for c, _ in sorted(seen.items(), key=lambda x: -x[1])][:max_colors]


def extract_components(css_text: str) -> dict[str, str]:
    components = {}
    for comp, patterns in COMPONENT_SELECTORS.items():
        snippets = []
        for pat in patterns:
            rule_pattern = re.compile(
                rf'({pat}[^{{]*\{{[^}}]{{0,400}}}})', re.IGNORECASE
            )
            matches = rule_pattern.findall(css_text)
            snippets.extend(matches[:2])
        if snippets:
            components[comp] = "\n".join(snippets[:3])
    return components


def analyze_site(url: str) -> dict:
    print(f"Fetching: {url}")
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (compatible; design-intel/1.0)"

    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        sys.exit(1)

    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    base_url = f"{r.url.split('/')[0]}//{r.url.split('/')[2]}"

    # Collect all CSS
    all_css = ""
    css_links = soup.find_all("link", rel="stylesheet")
    print(f"Found {len(css_links)} stylesheets")
    for tag in css_links[:10]:
        href = tag.get("href", "")
        if not href:
            continue
        full_url = href if href.startswith("http") else urllib.parse.urljoin(base_url, href)
        css = fetch_css(full_url, base_url, session)
        all_css += css + "\n"

    # Inline styles
    for style_tag in soup.find_all("style"):
        all_css += (style_tag.string or "") + "\n"

    # Extract data
    hex_colors = [normalize_hex(m) for m in HEX_PATTERN.findall(all_css)]
    colors = dedupe_colors(hex_colors)

    raw_fonts = FONT_PATTERN.findall(all_css)
    fonts = []
    for f in raw_fonts:
        name = f.split(",")[0].strip().strip("'\"")
        if name and name not in fonts and not name.startswith("var(") and len(name) < 50:
            fonts.append(name)
    fonts = list(dict.fromkeys(fonts))[:8]

    google_fonts = extract_google_fonts(html)
    all_fonts = list(dict.fromkeys(google_fonts + fonts))[:6]

    font_sizes = list(set(FONT_SIZE_PATTERN.findall(all_css)))[:10]
    font_weights = list(set(FONT_WEIGHT_PATTERN.findall(all_css)))
    radii = list(set(RADIUS_PATTERN.findall(all_css)))[:5]

    components = extract_components(all_css)

    # Take screenshot
    screenshot_path = None
    try:
        domain = urllib.parse.urlparse(url).netloc.replace(".", "_")
        dest_dir = os.path.join(LIBRARY, domain)
        os.makedirs(dest_dir, exist_ok=True)
        screenshot_path = os.path.join(dest_dir, "screenshot.png")
        subprocess.run(
            ["/usr/local/bin/agent-browser", "open", url],
            capture_output=True, timeout=15,
        )
        import time; time.sleep(3)
        subprocess.run(
            ["/usr/local/bin/agent-browser", "screenshot", screenshot_path, "--full-page"],
            capture_output=True, timeout=15,
        )
        print(f"Screenshot: {screenshot_path}")
    except Exception as e:
        print(f"Screenshot skipped: {e}")

    title = soup.find("title")
    site_name = title.get_text().strip() if title else urllib.parse.urlparse(url).netloc

    return {
        "url": url,
        "site_name": site_name,
        "colors": colors,
        "fonts": all_fonts,
        "font_sizes": font_sizes,
        "font_weights": font_weights,
        "border_radii": radii,
        "components": components,
        "screenshot": screenshot_path,
    }


def generate_design_md(data: dict, output_path: str = None) -> str:
    domain = urllib.parse.urlparse(data["url"]).netloc
    dest = output_path or os.path.join(LIBRARY, domain.replace(".", "_"), "DESIGN.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    colors = data["colors"]
    primary = colors[0] if len(colors) > 0 else "#000000"
    secondary = colors[1] if len(colors) > 1 else "#666666"
    accent = colors[2] if len(colors) > 2 else "#0066CC"
    bg = colors[-1] if len(colors) > 3 else "#FFFFFF"
    text = colors[3] if len(colors) > 4 else "#111111"

    font_primary = data["fonts"][0] if data["fonts"] else "Inter"
    font_secondary = data["fonts"][1] if len(data["fonts"]) > 1 else font_primary

    comp_section = ""
    if data["components"]:
        comp_section = "\n## Component Patterns\n\n"
        for comp_name, css in data["components"].items():
            comp_section += f"### {comp_name.capitalize()}\n```css\n{css[:300]}\n```\n\n"

    md = f"""# {data['site_name']} Design System
> Cloned from {data['url']} on {datetime.now().strftime('%Y-%m-%d')}

## Brand Identity
- Source: {data['url']}
- Extracted: {datetime.now().strftime('%Y-%m-%d')}

## Color Palette

### Primary Colors
- Primary: `{primary}`
- Secondary: `{secondary}`
- Accent: `{accent}`

### Neutral Colors
- Background: `{bg}`
- Text: `{text}`

### Extended Palette
{chr(10).join(f'- `{c}`' for c in colors)}

## Typography

### Fonts
- Primary: **{font_primary}**
- Secondary: **{font_secondary}**
- All detected: {', '.join(data['fonts']) if data['fonts'] else 'None detected'}

### Scale
{chr(10).join(f'- `{s}`' for s in sorted(data['font_sizes'])) if data['font_sizes'] else '- Standard scale'}

### Weights
{chr(10).join(f'- `{w}`' for w in sorted(data['font_weights'])) if data['font_weights'] else '- 400, 600, 700'}

## Spacing & Shape

### Border Radius
{chr(10).join(f'- `{r}`' for r in data['border_radii']) if data['border_radii'] else '- Not detected'}
{comp_section}
## Usage Notes
- Colors extracted from CSS stylesheets — manual review recommended
- Screenshot saved to: {data['screenshot'] or 'not captured'}
"""

    with open(dest, "w") as f:
        f.write(md)

    print(f"\nDESIGN.md saved: {dest}")
    return dest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clone a website's design system")
    parser.add_argument("url", help="URL to analyze (e.g. https://linear.app)")
    parser.add_argument("--output", help="Output path for DESIGN.md")
    args = parser.parse_args()

    data = analyze_site(args.url)
    output = generate_design_md(data, args.output)
    print(f"\nDone. Colors: {len(data['colors'])}, Fonts: {len(data['fonts'])}, Components: {len(data['components'])}")
