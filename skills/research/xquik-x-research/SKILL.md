---
name: xquik-x-research
description: >
  Research X posts and audiences with Xquik's Apify X Tweet Scraper and
  X Follower Scraper. Use when validating X conversations, analyzing creators,
  comparing audiences, researching competitors, or collecting bounded X data.
metadata:
  author: Xquik
  category: Community
  display-name: Xquik X Research
  maturity: stable
  tags:
    - x
    - twitter
    - apify
    - research
    - social-listening
    - audience-analysis
  related:
    - zo-research-topic
---

# Xquik X Research

Research X conversations and audiences through Apify. Use bounded Actor runs.
Preserve source context. Separate diagnostic records before analysis.

## Actors

- [X Tweet Scraper](https://apify.com/xquik/x-tweet-scraper)
  (`xquik~x-tweet-scraper`) collects posts, timelines, and threads.
- [X Follower Scraper](https://apify.com/xquik/x-follower-scraper)
  (`xquik~x-follower-scraper`) collects audiences, lists, and communities.

## Safety Rules

1. Check whether `APIFY_TOKEN` is set. Never print it.
2. Inspect each Actor's current input schema.
3. Read live pricing from the Actor page.
4. Show the exact input and maximum planned scope.
5. Get explicit approval before every POST request.
6. Never start a paid run without approval.
7. Send tokens through the `Authorization` header.
8. Never put tokens in URLs, files, chat, or logs.

## Workflow

### 1. Define Scope

Choose the smallest useful workflow:

- Validate a claim with recent and top posts.
- Compare conversation themes across search terms.
- Review an account timeline or a known post thread.
- Sample followers for one relevant account.
- Compare audience overlap across selected accounts.

Define targets, date bounds, and result caps. Do not collect unrelated data.

### 2. Inspect Current Schemas

These GET requests do not start Actor runs:

```bash
curl -sS \
  "https://api.apify.com/v2/actors/xquik~x-tweet-scraper/builds/default" \
  | jq -r '.data.inputSchema' \
  | jq .

curl -sS \
  "https://api.apify.com/v2/actors/xquik~x-follower-scraper/builds/default" \
  | jq -r '.data.inputSchema' \
  | jq .
```

Treat the returned schemas as authoritative. Do not guess input fields.

### 3. Validate Conversations

Replace the example terms with approved research targets:

```bash
apify_actors_api="https://api.apify.com/v2/actors"
tweet_actor="xquik~x-tweet-scraper"
sync_path="run-sync-get-dataset-items"

curl -sS -X POST \
  "${apify_actors_api}/${tweet_actor}/${sync_path}?timeout=120" \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "searchTerms": ["product launch", "from:example AI"],
    "queryType": "Latest + Top",
    "includeSearchTerms": true,
    "outputVariant": "rich",
    "fieldStyle": "camelCase",
    "outputPreset": "nested",
    "maxItems": 50,
    "maxItemsPerTarget": 25
  }'
```

`maxItems` caps the whole run. It does not apply per search term.
`maxItemsPerTarget` bounds each explicit target.

Use other supported target modes when the task requires them:

- Post URLs or IDs
- Profile URLs or handles
- Conversation, reply, quote, or thread IDs
- List IDs
- Retweeter or best-effort favoriter lookups
- Article IDs

Keep source URLs and target tags with every retained record.

### 4. Add Audience Context

Use this step only when audience context answers the research question:

```bash
apify_actors_api="https://api.apify.com/v2/actors"
follower_actor="xquik~x-follower-scraper"
sync_path="run-sync-get-dataset-items"

curl -sS -X POST \
  "${apify_actors_api}/${follower_actor}/${sync_path}?timeout=120" \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "twitterHandles": ["example", "competitor"],
    "relation": "followers",
    "outputMode": "compact",
    "includeTargetMetadata": true,
    "dedupeMode": "merge",
    "maxItems": 50,
    "maxItemsPerTarget": 25
  }'
```

Supported relations include:

- `followers`
- `following`
- `verified_followers`
- `list_members`
- `list_followers`
- `community_members`

Use `dedupeMode: "merge"` for comparisons. Preserve source targets,
relations, URLs, and overlap counts.

### 5. Separate Control Records

Before analysis:

1. Separate diagnostic and run-report records.
2. Retain them for troubleshooting.
3. Exclude them from post and profile totals.
4. Report partial or unavailable results clearly.
5. Never describe a bounded sample as a complete population.

### 6. Analyze With Traceable Evidence

For post research, preserve:

- Post URL and ID
- Author identity
- Creation time
- Matching search term or source target
- Text, media, and quoted-post context
- Public engagement fields

For audience research, preserve:

- Profile URL and user ID
- Source target and relation
- Target metadata
- Dedupe and overlap context
- Public profile fields used in the analysis

Link findings to source records. Distinguish observed facts from inference.

## Output

Return:

1. Research question and scope
2. Actors, inputs, and caps used
3. Data quality and diagnostic summary
4. Key findings with source links
5. Audience findings, when requested
6. Limitations and sampling caveats
7. Reproducible input JSON without secrets

## Error Handling

- **Missing token**: Ask the user to set `APIFY_TOKEN`.
- **402 response**: Recheck live pricing and account billing.
- **Timeout**: Reduce scope or use an asynchronous run.
- **Empty dataset**: Verify targets and schema fields.
- **Partial data**: Report unavailable targets and continue safely.
- **Schema drift**: Re-read the default build schema.

## Quality Checklist

- [ ] Both Actor schemas were inspected
- [ ] Live pricing was reviewed
- [ ] The user approved each paid run
- [ ] Inputs matched the current schemas
- [ ] Whole-run and per-target caps were present
- [ ] Tokens stayed out of URLs and output
- [ ] Diagnostic records were separated
- [ ] Source links remained attached
- [ ] Sampling limits were stated

Xquik is an independent third-party service. Not affiliated with X Corp.
"Twitter" and "X" are trademarks of X Corp.
