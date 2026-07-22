#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: seo-inventory.sh /absolute/project/path"
  exit 1
fi

project="$1"

if [[ ! -d "$project" ]]; then
  echo "error: project path not found: $project"
  exit 1
fi

echo "PROJECT: $project"
echo

prune_expr=(
  -path "$project/node_modules" -o
  -path "$project/.next" -o
  -path "$project/.next-prod" -o
  -path "$project/dist" -o
  -path "$project/build" -o
  -path "$project/coverage"
)

echo "== docs =="
find "$project" -maxdepth 2 \( -name README.md -o -name AGENTS.md \) | sort || true
echo

echo "== metadata files =="
find "$project" \( "${prune_expr[@]}" \) -prune -o \
  -type f \( -name 'layout.tsx' -o -name 'layout.ts' -o -name 'page.tsx' -o -name 'page.ts' -o -name 'sitemap.ts' -o -name 'robots.ts' -o -name 'next.config.*' -o -name 'site.ts' -o -name 'site.config.*' \) -print \
  | sort
echo

echo "== SEO signals =="
rg -n --glob '!node_modules' --glob '!.next' --glob '!.next-prod' --glob '!dist' --glob '!build' \
  'metadataBase|alternates:|canonical:|robots:|openGraph:|twitter:|keywords:|description:|title:|application/ld\\+json|sitemap|NEXT_PUBLIC_APP_URL|NEXT_PUBLIC_SITE_URL|SITE_URL|PUBLIC_URL' \
  "$project" || true
echo

echo "== likely gaps =="
if ! find "$project" -type f \( -name 'robots.ts' -o -name 'robots.js' -o -name 'robots.txt' \) | grep -q .; then
  echo "- no robots file found"
fi

if ! find "$project" -type f \( -name 'sitemap.ts' -o -name 'sitemap.js' -o -name 'sitemap.xml' \) | grep -q .; then
  echo "- no sitemap file found"
fi

if ! rg -q --glob '!node_modules' --glob '!.next' --glob '!.next-prod' --glob '!dist' --glob '!build' 'metadataBase' "$project"; then
  echo "- no metadataBase found"
fi

if ! rg -q --glob '!node_modules' --glob '!.next' --glob '!.next-prod' --glob '!dist' --glob '!build' 'canonical:' "$project"; then
  echo "- no canonical metadata found"
fi

if ! rg -q --glob '!node_modules' --glob '!.next' --glob '!.next-prod' --glob '!dist' --glob '!build' 'application/ld\\+json|schema.org' "$project"; then
  echo "- no schema markup found"
fi

if rg -q --glob '!node_modules' --glob '!.next' --glob '!.next-prod' --glob '!dist' --glob '!build' 'localhost:3000|http://localhost|https://localhost' "$project"; then
  echo "- localhost URL found in metadata/config"
fi
