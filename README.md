# Classified AI Skill Library

A curated, sanitized library of 207 agent skills for [Zo Computer](https://zo.computer) and Claude-based agents, maintained by [Classified AI](https://www.classified.llc).

Every skill is a self-contained folder with a `SKILL.md` (what it does, when to use it, how to run it) and optional `scripts/`, `references/`, and `assets/`. Drop a folder into your `Skills/` directory and your agent can use it.

## Categories

| Category | Skills | Focus |
|---|---|---|
| `content-and-social` | 38 | Copywriting, captions, hooks, threads, voice tuning, repurposing |
| `dev-and-web` | 34 | GitHub workflows, scraping, crawling, SEO, web tooling |
| `research` | 21 | Briefings, monitoring, deep dives, fact-checking |
| `ai-efficiency` | 18 | Specs, premortems, skill authoring, agent best practices |
| `design-and-image` | 18 | Graphic generation, thumbnails, editing, upscaling, critique |
| `video` | 18 | Cutting, storyboarding, captions, rendering, lip sync |
| `integrations` | 17 | Third-party service connectors and setup guides |
| `productivity` | 17 | Tasks, reminders, calendars, prioritization |
| `utilities` | 14 | General-purpose helpers |
| `decks-and-docs` | 12 | Slides, PDFs, document pipelines |

`manifest.json` at the repo root indexes every skill with name, category, description, and author.

## Installing a skill

Copy the skill folder into your workspace's `Skills/` directory:

```bash
git clone https://github.com/Classified-AI-Core/skill-library.git
cp -r skill-library/skills/<category>/<skill-name> ~/Skills/
```

Some skills require API keys. Each `SKILL.md` documents its requirements; keys belong in your environment or secrets manager, never in the skill files.

## Attribution

This library merges original Classified AI skills with the MIT-licensed [Zo Computer community skills catalog](https://github.com/zocomputer/skills). Original author attribution is preserved in each skill's frontmatter. See `NOTICE`.

## Contributing

PRs welcome. Every submission is screened for personal data, credentials, and hardcoded private paths before merge.

## License

MIT. See `LICENSE` and `NOTICE`.
