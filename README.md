# Classified AI Skill Library

A curated, sanitized library of 200+ agent skills for [Zo Computer](https://zo.computer) and Claude-based agents, maintained by [Classified AI](https://www.classified.llc).

Every skill is a self-contained folder with a `SKILL.md` (what it does, when to use it, how to run it) and optional `scripts/`, `references/`, and `assets/`. Drop a folder into your `Skills/` directory and your agent can use it.

## Categories

| Category | Skills | Focus |
|---|---|---|
| `content-and-social` | 38 | Copywriting, captions, hooks, threads, voice tuning, repurposing |
| `dev-and-web` | 34 | GitHub workflows, scraping, crawling, SEO, web tooling |
| `research` | 21 | Briefings, monitoring, deep dives, fact-checking |
| `ai-efficiency` | 19 | Specs, premortems, skill authoring, agent best practices |
| `design-and-image` | 22 | Graphic generation, thumbnails, editing, upscaling, critique |
| `video` | 19 | Cutting, storyboarding, captions, rendering, lip sync |
| `integrations` | 17 | Third-party service connectors and setup guides |
| `productivity` | 19 | Tasks, reminders, calendars, prioritization |
| `utilities` | 14 | General-purpose helpers |
| `decks-and-docs` | 12 | Slides, PDFs, document pipelines |

`manifest.json` at the repo root indexes every skill with name, category, description, and author.

## Installing a skill

Copy the skill folder into your workspace's `Skills/` directory:

```bash
git clone https://github.com/Classified-AI-Core/skill-library.git
cp -r skill-library/skills/<category>/<skill-name> ~/Skills/            # Zo Computer
cp -r skill-library/skills/<category>/<skill-name> ~/.claude/skills/     # Claude Code
```

## Start here

Do not install the whole library. Install these three, use them for a week, then browse `manifest.json` for the thing you keep doing by hand.

- `ai-efficiency/premortem`: stress-test a plan before you build it.
- `ai-efficiency/code-degunker`: strip AI-generated bloat out of a codebase.
- `content-and-social/humanizer`: remove the tells that make copy read as machine-written.

Some skills require API keys. Each `SKILL.md` documents its requirements; keys belong in your environment or secrets manager, never in the skill files.

## Attribution

This library merges original Classified AI skills with the MIT-licensed [Zo Computer community skills catalog](https://github.com/zocomputer/skills). Original author attribution is preserved in each skill's frontmatter. See `NOTICE`.

## How a skill gets in

1. Every `SKILL.md` is read by a human, not skimmed.
2. It is scanned for personal data, credentials, and hardcoded private paths. The most common catch is an absolute path that only works on the author's machine.
3. The frontmatter has to be valid: `name` matching the folder, and a `description` that says when to trigger and when not to.
4. It has to do one job. "Marketing assistant" is not a skill. "Generate six two-line hooks with a 40-character limit per line" is.
5. It gets an entry in `manifest.json` so agents can search the library without cloning it.

## Contributing

PRs welcome. The same screening applies. Keys go in your environment, never in the skill file; PRs that do otherwise are rejected.

## Community

Discussion, weekly skill write-ups, and build notes at [r/ClassifiedAI](https://www.reddit.com/r/ClassifiedAI/) and the [Classified AI Builders Discord](https://discord.gg/MtHnGKaBze).

## License

MIT. See `LICENSE` and `NOTICE`.
