#!/usr/bin/env python3
"""List and search available brand design systems from getdesign.md."""
import argparse
import subprocess
import sys
import re

KNOWN_BRANDS = {
    "saas": ["stripe", "linear", "notion", "vercel", "github", "figma", "loom", "intercom",
              "segment", "mixpanel", "amplitude", "retool", "airtable", "coda", "monday",
              "asana", "clickup", "jira", "confluence"],
    "fintech": ["stripe", "brex", "mercury", "wise", "robinhood", "coinbase", "plaid",
                "square", "paypal", "klarna", "affirm", "chime"],
    "ecommerce": ["shopify", "amazon", "etsy", "woocommerce", "bigcommerce"],
    "social": ["twitter", "instagram", "tiktok", "youtube", "linkedin", "discord", "slack",
                "telegram", "whatsapp", "facebook", "pinterest", "reddit"],
    "tech": ["apple", "google", "microsoft", "meta", "netflix", "spotify", "airbnb",
              "uber", "lyft", "doordash", "dropbox", "atlassian", "salesforce"],
    "productivity": ["notion", "obsidian", "roam", "craft", "bear", "todoist", "things",
                      "linear", "height", "shortcut"],
    "design": ["figma", "framer", "webflow", "canva", "sketch", "invision", "zeplin"],
    "developer": ["github", "vercel", "netlify", "heroku", "railway", "fly", "supabase",
                   "firebase", "planetscale", "neon", "prisma"],
}


def fetch_from_npm():
    """Try to get brand list from npx getdesign."""
    result = subprocess.run(
        ["npx", "--yes", "getdesign@latest", "list"],
        capture_output=True, text=True, timeout=30,
    )
    return (result.stdout or "").strip()


def display_brands(query: str = None, show_categories: bool = False):
    npm_output = fetch_from_npm()

    if npm_output:
        print("Available brands from getdesign.md:\n")
        if query:
            lines = [l for l in npm_output.splitlines() if query.lower() in l.lower()]
            print("\n".join(lines) if lines else "No matches found.")
        else:
            print(npm_output)
        return

    # Fallback to known brands list
    if show_categories:
        for category, brands in KNOWN_BRANDS.items():
            print(f"\n{category.upper()}")
            print("  " + ", ".join(brands))
        return

    if query:
        matches = []
        for brands in KNOWN_BRANDS.values():
            matches.extend([b for b in brands if query.lower() in b.lower()])
        matches = list(set(matches))
        if matches:
            print(f"Brands matching '{query}':")
            for b in sorted(matches):
                print(f"  {b}")
        else:
            print(f"No brands matching '{query}'. Try a broader term.")
        return

    all_brands = sorted(set(b for brands in KNOWN_BRANDS.values() for b in brands))
    print(f"Known brands ({len(all_brands)} total):")
    for i, brand in enumerate(all_brands):
        end = "\n" if (i + 1) % 5 == 0 or i == len(all_brands) - 1 else "  "
        print(f"  {brand}", end=end)

    print(f"\nCategories: {', '.join(KNOWN_BRANDS.keys())}")
    print("\nFetch with: python fetch_design.py <brand>")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List available brand design systems")
    parser.add_argument("query", nargs="?", help="Search query (brand name or keyword)")
    parser.add_argument("--categories", action="store_true", help="Group by category")
    args = parser.parse_args()

    display_brands(args.query, args.categories)
