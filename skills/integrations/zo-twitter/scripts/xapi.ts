#!/usr/bin/env bun
import OAuth from "oauth-1.0a";
import crypto from "crypto";

const BASE = "https://api.x.com/2";

const oauth = new OAuth({
  consumer: {
    key: process.env.x_api_key!,
    secret: process.env.x_api_secret!,
  },
  signature_method: "HMAC-SHA1",
  hash_function(base_string, key) {
    return crypto.createHmac("sha1", key).update(base_string).digest("base64");
  },
});

const token = {
  key: process.env.x_access_token!,
  secret: process.env.x_access_token_secret!,
};

const bearer = process.env.x_bearer_token!;

type AuthMode = "oauth1" | "bearer";

async function request(
  method: string,
  url: string,
  auth: AuthMode,
  body?: any
): Promise<any> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };

  if (auth === "bearer") {
    headers["Authorization"] = `Bearer ${bearer}`;
  } else {
    const authHeader = oauth.toHeader(
      oauth.authorize({ url, method }, token)
    );
    headers["Authorization"] = authHeader.Authorization;
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  if (!res.ok) {
    console.error(`HTTP ${res.status}: ${text}`);
    process.exit(1);
  }
  return text ? JSON.parse(text) : {};
}

function print(data: any) {
  console.log(JSON.stringify(data, null, 2));
}

const commands: Record<string, { desc: string; usage: string; run: (args: string[]) => Promise<void> }> = {

  me: {
    desc: "Get authenticated user info",
    usage: "xapi me",
    async run() {
      const data = await request("GET", `${BASE}/users/me?user.fields=public_metrics,description,created_at,location,verified`, "oauth1");
      print(data);
    },
  },

  user: {
    desc: "Get user by username",
    usage: "xapi user <username>",
    async run(args) {
      const username = args[0]?.replace("@", "");
      if (!username) { console.error("Usage: xapi user <username>"); process.exit(1); }
      const data = await request("GET", `${BASE}/users/by/username/${username}?user.fields=public_metrics,description,created_at,location,verified`, "bearer");
      print(data);
    },
  },

  tweet: {
    desc: "Get tweet by ID with metrics",
    usage: "xapi tweet <id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi tweet <id>"); process.exit(1); }
      const data = await request("GET", `${BASE}/tweets/${id}?tweet.fields=public_metrics,created_at,author_id,conversation_id,in_reply_to_user_id,referenced_tweets,entities&expansions=author_id&user.fields=username,name`, "bearer");
      print(data);
    },
  },

  post: {
    desc: "Post a tweet",
    usage: "xapi post <text> [--reply-to <id>] [--quote <id>] [--poll <opt1,opt2,...> --poll-hours <n>]",
    async run(args) {
      const body: any = {};
      let text = "";
      let i = 0;
      while (i < args.length) {
        if (args[i] === "--reply-to") { body.reply = { in_reply_to_tweet_id: args[++i] }; }
        else if (args[i] === "--quote") { body.quote_tweet_id = args[++i]; }
        else if (args[i] === "--poll") {
          const options = args[++i].split(",").map(o => ({ label: o.trim() }));
          const hours = args[i + 1] === "--poll-hours" ? parseInt(args[i += 2]) : 24;
          body.poll = { options, duration_minutes: hours * 60 };
        }
        else { text += (text ? " " : "") + args[i]; }
        i++;
      }
      body.text = text;
      if (!body.text) { console.error("Usage: xapi post <text>"); process.exit(1); }
      const data = await request("POST", `${BASE}/tweets`, "oauth1", body);
      print(data);
    },
  },

  delete: {
    desc: "Delete a tweet",
    usage: "xapi delete <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi delete <tweet-id>"); process.exit(1); }
      const data = await request("DELETE", `${BASE}/tweets/${id}`, "oauth1");
      print(data);
    },
  },

  like: {
    desc: "Like a tweet",
    usage: "xapi like <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi like <tweet-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("POST", `${BASE}/users/${me.data.id}/likes`, "oauth1", { tweet_id: id });
      print(data);
    },
  },

  unlike: {
    desc: "Unlike a tweet",
    usage: "xapi unlike <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi unlike <tweet-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("DELETE", `${BASE}/users/${me.data.id}/likes/${id}`, "oauth1");
      print(data);
    },
  },

  retweet: {
    desc: "Retweet a tweet",
    usage: "xapi retweet <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi retweet <tweet-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("POST", `${BASE}/users/${me.data.id}/retweets`, "oauth1", { tweet_id: id });
      print(data);
    },
  },

  unretweet: {
    desc: "Undo a retweet",
    usage: "xapi unretweet <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi unretweet <tweet-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("DELETE", `${BASE}/users/${me.data.id}/retweets/${id}`, "oauth1");
      print(data);
    },
  },

  bookmark: {
    desc: "Bookmark a tweet",
    usage: "xapi bookmark <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi bookmark <tweet-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("POST", `${BASE}/users/${me.data.id}/bookmarks`, "oauth1", { tweet_id: id });
      print(data);
    },
  },

  block: {
    desc: "Block a user",
    usage: "xapi block <user-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi block <user-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("POST", `${BASE}/users/${me.data.id}/blocking`, "oauth1", { target_user_id: id });
      print(data);
    },
  },

  unblock: {
    desc: "Unblock a user",
    usage: "xapi unblock <user-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi unblock <user-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("DELETE", `${BASE}/users/${me.data.id}/blocking/${id}`, "oauth1");
      print(data);
    },
  },

  mute: {
    desc: "Mute a user",
    usage: "xapi mute <user-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi mute <user-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("POST", `${BASE}/users/${me.data.id}/muting`, "oauth1", { target_user_id: id });
      print(data);
    },
  },

  unmute: {
    desc: "Unmute a user",
    usage: "xapi unmute <user-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi unmute <user-id>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("DELETE", `${BASE}/users/${me.data.id}/muting/${id}`, "oauth1");
      print(data);
    },
  },

  search: {
    desc: "Search recent tweets (7 days)",
    usage: "xapi search <query> [--max <n>] [--next <token>]",
    async run(args) {
      let query = "";
      let max = 10;
      let nextToken = "";
      let i = 0;
      while (i < args.length) {
        if (args[i] === "--max") max = Math.max(10, parseInt(args[++i]));
        else if (args[i] === "--next") nextToken = args[++i];
        else query += (query ? " " : "") + args[i];
        i++;
      }
      if (!query) { console.error("Usage: xapi search <query>"); process.exit(1); }
      let url = `${BASE}/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=${max}&tweet.fields=public_metrics,created_at,author_id&expansions=author_id&user.fields=username,name`;
      if (nextToken) url += `&next_token=${nextToken}`;
      const data = await request("GET", url, "bearer");
      print(data);
    },
  },

  mentions: {
    desc: "Get your recent mentions",
    usage: "xapi mentions [--max <n>]",
    async run(args) {
      let max = 10;
      if (args[0] === "--max") max = parseInt(args[1]);
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("GET", `${BASE}/users/${me.data.id}/mentions?max_results=${max}&tweet.fields=public_metrics,created_at,author_id&expansions=author_id&user.fields=username,name`, "oauth1");
      print(data);
    },
  },

  timeline: {
    desc: "Get your home timeline",
    usage: "xapi timeline [--max <n>]",
    async run(args) {
      let max = 10;
      if (args[0] === "--max") max = parseInt(args[1]);
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("GET", `${BASE}/users/${me.data.id}/reverse_chronological?max_results=${max}&tweet.fields=public_metrics,created_at,author_id&expansions=author_id&user.fields=username,name`, "oauth1");
      print(data);
    },
  },

  dm: {
    desc: "Send a direct message",
    usage: "xapi dm <user-id> <text>",
    async run(args) {
      const userId = args[0];
      const text = args.slice(1).join(" ");
      if (!userId || !text) { console.error("Usage: xapi dm <user-id> <text>"); process.exit(1); }
      const me = await request("GET", `${BASE}/users/me`, "oauth1");
      const data = await request("POST", `${BASE}/dm_conversations/with/${userId}/messages`, "oauth1", {
        text,
      });
      print(data);
    },
  },

  "dm-list": {
    desc: "List recent DM events",
    usage: "xapi dm-list [--max <n>]",
    async run(args) {
      let max = 10;
      if (args[0] === "--max") max = parseInt(args[1]);
      const data = await request("GET", `${BASE}/dm_events?max_results=${max}&dm_event.fields=created_at,sender_id,text,dm_conversation_id&expansions=sender_id&user.fields=username,name`, "oauth1");
      print(data);
    },
  },

  metrics: {
    desc: "Get engagement metrics for a tweet",
    usage: "xapi metrics <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi metrics <tweet-id>"); process.exit(1); }
      const data = await request("GET", `${BASE}/tweets/${id}?tweet.fields=public_metrics,non_public_metrics,organic_metrics&expansions=author_id&user.fields=username`, "oauth1");
      print(data);
    },
  },

  followers: {
    desc: "List followers of a user",
    usage: "xapi followers <user-id|@username> [--max <n>]",
    async run(args) {
      let target = args[0];
      let max = 100;
      if (args[1] === "--max") max = parseInt(args[2]);
      if (!target) { console.error("Usage: xapi followers <user-id|@username>"); process.exit(1); }
      if (target.startsWith("@")) {
        const u = await request("GET", `${BASE}/users/by/username/${target.slice(1)}`, "bearer");
        target = u.data.id;
      }
      const data = await request("GET", `${BASE}/users/${target}/followers?max_results=${max}&user.fields=public_metrics,description,created_at`, "bearer");
      print(data);
    },
  },

  following: {
    desc: "List who a user follows",
    usage: "xapi following <user-id|@username> [--max <n>]",
    async run(args) {
      let target = args[0];
      let max = 100;
      if (args[1] === "--max") max = parseInt(args[2]);
      if (!target) { console.error("Usage: xapi following <user-id|@username>"); process.exit(1); }
      if (target.startsWith("@")) {
        const u = await request("GET", `${BASE}/users/by/username/${target.slice(1)}`, "bearer");
        target = u.data.id;
      }
      const data = await request("GET", `${BASE}/users/${target}/following?max_results=${max}&user.fields=public_metrics,description,created_at`, "bearer");
      print(data);
    },
  },

  "hide-reply": {
    desc: "Hide a reply to your tweet",
    usage: "xapi hide-reply <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi hide-reply <tweet-id>"); process.exit(1); }
      const data = await request("PUT", `${BASE}/tweets/${id}/hidden`, "oauth1", { hidden: true });
      print(data);
    },
  },

  "unhide-reply": {
    desc: "Unhide a reply",
    usage: "xapi unhide-reply <tweet-id>",
    async run(args) {
      const id = args[0];
      if (!id) { console.error("Usage: xapi unhide-reply <tweet-id>"); process.exit(1); }
      const data = await request("PUT", `${BASE}/tweets/${id}/hidden`, "oauth1", { hidden: false });
      print(data);
    },
  },
};

const cmd = process.argv[2];
const cmdArgs = process.argv.slice(3);

if (!cmd || cmd === "--help" || cmd === "-h") {
  console.log("xapi — X API v2 CLI for Zo\n");
  console.log("Usage: bun xapi.ts <command> [args]\n");
  console.log("Commands:");
  for (const [name, { desc, usage }] of Object.entries(commands)) {
    console.log(`  ${name.padEnd(16)} ${desc}`);
    console.log(`  ${"".padEnd(16)} ${usage}`);
  }
  process.exit(0);
}

if (!commands[cmd]) {
  console.error(`Unknown command: ${cmd}. Run with --help for usage.`);
  process.exit(1);
}

await commands[cmd].run(cmdArgs);
