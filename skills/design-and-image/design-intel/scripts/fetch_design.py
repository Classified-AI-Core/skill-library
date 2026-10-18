#!/usr/bin/env python3
"""Fetch a brand's DESIGN.md from getdesign.md via the official npx CLI."""
import argparse
import subprocess
import shutil
import os
import sys

LIBRARY = os.environ.get("DESIGN_LIBRARY", "/home/workspace/Design/Library")


def fetch_brand(brand: str, project: str = None):
    dest = os.path.join(LIBRARY, brand.lower())
    os.makedirs(dest, exist_ok=True)

    print(f"Fetching design system for: {brand}")
    result = subprocess.run(
        ["npx", "--yes", "getdesign@latest", "add", brand],
        cwd=dest,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        print(f"Error fetching design:\n{result.stderr}")
        # Some versions output to stdout even on "error"
        if result.stdout:
            print(result.stdout)
        sys.exit(1)

    design_file = os.path.join(dest, "DESIGN.md")
    if not os.path.exists(design_file):
        # getdesign may name it differently
        md_files = [f for f in os.listdir(dest) if f.endswith(".md")]
        if md_files:
            os.rename(os.path.join(dest, md_files[0]), design_file)
        else:
            print(f"No DESIGN.md found in {dest} after fetch.")
            print("npx output:", result.stdout)
            sys.exit(1)

    print(f"Saved: {design_file}")

    if project:
        target = os.path.join(project, "DESIGN.md")
        shutil.copy(design_file, target)
        print(f"Copied to: {target}")

    return design_file


def list_brands():
    result = subprocess.run(
        ["npx", "--yes", "getdesign@latest", "list"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout or result.stderr
    if output.strip():
        print(output)
    else:
        print("Run: npx getdesign@latest --help  to see available brands")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch brand DESIGN.md from getdesign.md")
    parser.add_argument("brand", nargs="?", help="Brand name (e.g. stripe, linear, apple)")
    parser.add_argument("--project", help="Project path to also copy DESIGN.md into")
    parser.add_argument("--list", action="store_true", help="List available brands")
    args = parser.parse_args()

    if args.list or not args.brand:
        list_brands()
    else:
        fetch_brand(args.brand, args.project)
