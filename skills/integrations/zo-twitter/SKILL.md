---
name: twitter
description: Let Zo use your X (Twitter) account via bird CLI (cookie auth) or xapi (official X API v2). Use bird for reading/posting with cookie auth. Use xapi for DMs, like/retweet/block/mute actions, engagement metrics, polls, hide replies, and structured API access.
compatibility: Requires the bird CLI (pre-installed) and/or X API v2 credentials. Credentials set in Zo Settings > Advanced > Secrets.
metadata:
  author: Zo
  category: content-publishing
  display-name: X (Twitter)
  maturity: stable
  tags:
    - twitter
    - posting
    - x-api
    - bookmarks
  related:
    - social-content
    - x-monitor
---

This skill provides two tools for interacting with X/Twitter:

1. **`bird`** — Fast CLI using cookie-based auth. Best for reading timelines, search, posting, and browsing.
2. **`xapi`** — Official X API v2 via OAuth 1.0a + Bearer token. Best for DMs, engagement actions, metrics, polls, and moderation.

## When to use which

| Task | Use |
|------|-----|
| Read tweets, threads, timelines | bird (richer output) |
| Search tweets | Either (bird has nicer formatting; xapi returns structured JSON with metrics) |
| Post a tweet | Either (bird for simplicity; xapi for polls/quotes) |
| Like / Retweet / Bookmark | xapi |
| Block / Mute / Hide replies | xapi |
| Send / Read DMs | xapi |
| Get engagement metrics | xapi |
| Create polls | xapi |
| News / Trending | bird |

---

## bird CLI

`bird`: Fast X/Twitter CLI using cookie auth.

## Updating

`bird` comes pre-installed on Zo. To update:

```bash
npm install -g @steipete/bird
```

## Authentication

`bird` uses cookie-based auth. 

The USER must set their credentials in their Settings > Integrations > Connections page.

If `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` are not set, direct the USER to this page with a relative URL.

## Commands

### Account & Auth

```bash
bird whoami                    # Show logged-in account
bird check                     # Show credential sources
bird query-ids --fresh         # Refresh GraphQL query ID cache
```

### Reading Tweets

```bash
bird read <url-or-id>          # Read a single tweet
bird <url-or-id>               # Shorthand for read
bird thread <url-or-id>        # Full conversation thread
bird replies <url-or-id>       # List replies to a tweet
```

### Timelines

```bash
bird home                      # Home timeline (For You)
bird home --following          # Following timeline
bird user-tweets @handle -n 20 # User's profile timeline
bird mentions                  # Tweets mentioning you
bird mentions --user @handle   # Mentions of another user
```

### Search

```bash
bird search "query" -n 10
bird search "from:steipete" --all --max-pages 3
```

### News & Trending

```bash
bird news -n 10                # AI-curated from Explore tabs
bird news --ai-only            # Filter to AI-curated only
bird news --sports             # Sports tab
bird news --with-tweets        # Include related tweets
bird trending                  # Alias for news
```

### Lists

```bash
bird lists                     # Your lists
bird lists --member-of         # Lists you're a member of
bird list-timeline <id> -n 20  # Tweets from a list
```

### Bookmarks & Likes

```bash
bird bookmarks -n 10
bird bookmarks --folder-id <id>           # Specific folder
bird bookmarks --include-parent           # Include parent tweet
bird bookmarks --author-chain             # Author's self-reply chain
bird bookmarks --full-chain-only          # Full reply chain
bird unbookmark <url-or-id>
bird likes -n 10
```

### Social Graph

```bash
bird following -n 20           # Users you follow
bird followers -n 20           # Users following you
bird following --user <id>     # Another user's following
bird about @handle             # Account origin/location info
```

### Engagement Actions

```bash
bird follow @handle            # Follow a user
bird unfollow @handle          # Unfollow a user
```

### Posting

```bash
bird tweet "hello world"
bird reply <url-or-id> "nice thread!"
bird tweet "check this out" --media image.png --alt "description"
```

**⚠️ Posting risks**: Posting is more likely to be rate limited; if blocked, use the browser tool instead.

## Media Uploads

```bash
bird tweet "hi" --media img.png --alt "description"
bird tweet "pics" --media a.jpg --media b.jpg  # Up to 4 images
bird tweet "video" --media clip.mp4            # Or 1 video
```

## Pagination

Commands supporting pagination: `replies`, `thread`, `search`, `bookmarks`, `likes`, `list-timeline`, `following`, `followers`, `user-tweets`

```bash
bird bookmarks --all                    # Fetch all pages
bird bookmarks --max-pages 3            # Limit pages
bird bookmarks --cursor <cursor>        # Resume from cursor
bird replies <id> --all --delay 1000    # Delay between pages (ms)
```

## Output Options

```bash
--json          # JSON output
--json-full     # JSON with raw API response
--plain         # No emoji, no color (script-friendly)
--no-emoji      # Disable emoji
--no-color      # Disable ANSI colors (or set NO_COLOR=1)
--quote-depth n # Max quoted tweet depth in JSON (default: 1)
```

## Global Options

```bash
--auth-token <token>       # Set auth_token cookie
--ct0 <token>              # Set ct0 cookie
--cookie-source <source>   # Cookie source for browser cookies (repeatable)
--chrome-profile <name>    # Chrome profile name
--chrome-profile-dir <path> # Chrome/Chromium profile dir or cookie DB path
--firefox-profile <name>   # Firefox profile
--timeout <ms>             # Request timeout
--cookie-timeout <ms>      # Cookie extraction timeout
```

## Config File

`~/.config/bird/config.json5` (global) or `./.birdrc.json5` (project):

```json5
{
  cookieSource: ["chrome"],
  chromeProfileDir: "/path/to/Arc/Profile",
  timeoutMs: 20000,
  quoteDepth: 1
}
```

Environment variables: `BIRD_TIMEOUT_MS`, `BIRD_COOKIE_TIMEOUT_MS`, `BIRD_QUOTE_DEPTH`

## Troubleshooting

### Query IDs stale (404 errors)
```bash
bird query-ids --fresh
```

### Cookie extraction fails
- Check browser is logged into X
- Try different `--cookie-source`
- For Arc/Brave: use `--chrome-profile-dir`

---

**TL;DR**: Read/search/engage with CLI. Post carefully or use browser.

---

## xapi — X API v2 CLI

**Location:** `Skills/zo-twitter/scripts/xapi.ts`
**Run:** `cd /home/workspace/Skills/zo-twitter/scripts && bun xapi.ts <command> [args]`

### Authentication

Uses environment variables (set in Settings > Advanced > Secrets):
- `x_api_key` — Consumer/API key
- `x_api_secret` — Consumer/API secret
- `x_bearer_token` — Bearer token (app-only auth)
- `x_access_token` — User access token
- `x_access_token_secret` — User access token secret

### Commands

#### Account
```bash
xapi me                           # Authenticated user info + metrics
xapi user <@username>             # Lookup any user
```

#### Tweets
```bash
xapi tweet <id>                   # Get tweet with full metrics
xapi metrics <id>                 # Engagement metrics (impressions, etc.)
xapi search <query> [--max <n>] [--next <token>]   # Search recent (7 days)
xapi mentions [--max <n>]         # Your mentions
xapi timeline [--max <n>]         # Home timeline
```

#### Posting
```bash
xapi post <text>                               # Post a tweet
xapi post <text> --reply-to <id>               # Reply to a tweet
xapi post <text> --quote <id>                  # Quote tweet
xapi post <text> --poll Yes,No --poll-hours 24 # Tweet with poll
xapi delete <tweet-id>                         # Delete a tweet
```

#### Engagement Actions
```bash
xapi like <tweet-id>              # Like
xapi unlike <tweet-id>            # Unlike
xapi retweet <tweet-id>           # Retweet
xapi unretweet <tweet-id>         # Undo retweet
xapi bookmark <tweet-id>          # Bookmark
```

#### Moderation
```bash
xapi block <user-id>              # Block user
xapi unblock <user-id>            # Unblock user
xapi mute <user-id>               # Mute user
xapi unmute <user-id>             # Unmute user
xapi hide-reply <tweet-id>        # Hide a reply to your tweet
xapi unhide-reply <tweet-id>      # Unhide a reply
```

#### Direct Messages
```bash
xapi dm <user-id> <text>          # Send a DM
xapi dm-list [--max <n>]          # List recent DM events
```

#### Social Graph
```bash
xapi followers <@username|id> [--max <n>]   # List followers
xapi following <@username|id> [--max <n>]   # List following
```

### Output

All commands output JSON. Pipe through `jq` for filtering:
```bash
bun xapi.ts me | jq '.data.public_metrics'
bun xapi.ts search "AI" | jq '.data[] | {text, likes: .public_metrics.like_count}'
```

### Rate Limits

X API v2 has per-endpoint rate limits. The Free tier allows:
- 1,500 tweets posted per month
- 10,000 tweet reads per month
- Limited DM access

If rate-limited, the script will show the HTTP 429 error. Wait and retry.

## Related Skills
- **social-content** — draft and optimize social media content before posting via zo-twitter
- **x-monitor** — monitor X for topics and trends that inform posting strategy

