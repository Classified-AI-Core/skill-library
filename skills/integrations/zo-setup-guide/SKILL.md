---
name: zo-setup-guide
description: A beginner-friendly guide to setting up a personalized AI computer on Zo. Walk through the core concepts (models, files, skills, agents, hosting, secrets) and a 5-layer strategy for building a real system. Activate when a user wants help understanding or setting up their Zo.
compatibility: Created for Zo Computer
metadata:
  author: zmann.zo.computer
  version: 1
  category: infrastructure
  maturity: stable
  tags:
    - zo
    - setup
    - onboarding
    - documentation
  related:
    - github
    - slack
---
# Building Your Personal AI Computer on Zo

A practical guide for someone who has never used Zo before — written by someone who has been building on it daily.

---

## Table of Contents

 1. [What Is Zo, Actually?](#1-what-is-zo-actually)
 2. [The Chat: Your Main Interface](#2-the-chat-your-main-interface)
 3. [Multi-Model Chat: Pick Your Brain](#3-multi-model-chat-pick-your-brain)
 4. [The File System: Your Stuff Lives Here](#4-the-file-system-your-stuff-lives-here)
 5. [Skills: Teaching Zo New Tricks](#5-skills-teaching-zo-new-tricks)
 6. [Agents: Things That Run While You Sleep](#6-agents-things-that-run-while-you-sleep)
 7. [Rules: Setting Boundaries and Preferences](#7-rules-setting-boundaries-and-preferences)
 8. [Personas: Giving Zo a Different Voice](#8-personas-giving-zo-a-different-voice)
 9. [Hosting and Live Services](#9-hosting-and-live-services)
10. [zo.space: Your Personal Corner of the Internet](#10-zospace-your-personal-corner-of-the-internet)
11. [APIs: How Software Talks to Software](#11-apis-how-software-talks-to-software)
12. [APIs vs. Zo Integrations: When to Use Which](#12-apis-vs-zo-integrations-when-to-use-which)
13. [Bring Your Own AI: Claude Code and GPT](#13-bring-your-own-ai-claude-code-and-gpt)
14. [Secrets: Keeping Your Keys Safe](#14-secrets-keeping-your-keys-safe)
15. [Billing and the Pro Plan](#15-billing-and-the-pro-plan)
16. [The 5-Layer Setup Strategy](#16-the-5-layer-setup-strategy)
17. [Key Terms Glossary](#17-key-terms-glossary)

---

## 1. What Is Zo, Actually?

Zo is a personal computer that lives in the cloud. It's a real Linux server — yours — with an AI assistant built into it. Think of it as a mashup of:

- **Cloud storage** (like Dropbox or Google Drive — your files live on your server)
- **An AI chat** (like ChatGPT — but it can actually *do* things on your computer)
- **A web host** (like Vercel or Netlify — you can publish sites and run services)
- **An automation platform** (like Zapier — you can schedule tasks that run on their own)

The key difference from other AI tools: **Zo can act.** It doesn't just answer questions — it reads your files, writes code, runs programs, sends texts, checks your email, builds websites, and remembers things across conversations. It has hands.

Your Zo lives at `https://yourhandle.zo.computer`. Everything you build, store, or create is on your server. You own it.

**First thing to do:** Open your Zo and just chat. Say hi. Ask it to do something — make a note, search the web, summarize an article. Get a feel for the conversation before you start configuring.

---

## 2. The Chat: Your Main Interface

The chat is where you talk to Zo. It's the center of the whole experience. But it's not just a chatbot — it's a command line in plain English.

Things you can do right from the chat:

- "Search the web for X" — Zo has web search, image search, X/Twitter search, and Google Maps built in
- "Read this URL" — paste a link and Zo saves and summarizes it
- "Make me a website about X" — Zo will code it and host it, live, in minutes
- "Text me tomorrow at 9am to call the dentist" — Zo sends you a real SMS
- "What's on my calendar today?" — if you connect Google Calendar, Zo reads it directly
- "Check my email for anything from Amazon" — with Gmail connected, it searches your inbox

The chat is also where you activate **skills** (more on those below) and interact with **agents**. It's the hub.

**Tip:** You can also reach Zo by text message or email. Text your Zo number or email `yourhandle@zo.computer` from your registered address, and you're in a conversation.

---

## 3. Multi-Model Chat: Pick Your Brain

One of Zo's most powerful features is that you're not locked into one AI model. You can switch between different AI "brains" depending on the task.

### What does "model" mean?

An AI model is the engine behind the chat. Different models are made by different companies and have different strengths:

| Model Family | Made By | Good For |
| --- | --- | --- |
| **Claude** (Sonnet, Opus, Haiku) | Anthropic | Deep reasoning, writing, coding, long documents |
| **GPT-4o, o1, o3** | OpenAI | General tasks, vision, quick answers |
| **Gemini** | Google | Large context, multimodal tasks |
| **Others** (Mistral, Llama, etc.) | Various | Specialized tasks, cost savings |

### How to switch models

Go to [Settings &gt; AI &gt; Models](/?t=settings&s=ai&d=models) and pick your default. You can also set different models for different **channels** (chat vs. text vs. email).

### Why this matters

Some tasks need a heavy-duty model (like writing complex code or analyzing a 100-page document). Others just need a quick answer. Being able to swap models means you can match the tool to the job — and manage your costs.

### Bringing your own keys

If you have your own subscriptions to Anthropic (Claude) or OpenAI (GPT), you can plug your API keys into Zo at [Settings &gt; AI &gt; Providers](/?t=settings&s=ai&d=providers). This lets you use your own quota instead of Zo credits. More on this in [Section 13](#13-bring-your-own-ai-claude-code-and-gpt).

---

## 4. The File System: Your Stuff Lives Here

Your Zo has a real file system, just like your laptop. The main workspace is at `/home/workspace/` — this is where your files, projects, documents, and media live.

### How to organize it

There's no forced structure — set it up however makes sense for you. Here's a pattern that works well:

```markdown
/home/workspace/
├── Documents/          ← Notes, PDFs, reports
├── Images/             ← Photos, screenshots, generated images
├── Articles/           ← Saved web articles
├── Projects/           ← Code projects, apps
├── Research/           ← Research data and analysis
├── Skills/             ← Your custom Zo skills (see Section 5)
├── Health Data/        ← Personal data (health, finance, etc.)
├── User Context/       ← Info about yourself for Zo to reference
│   ├── About Me/
│   ├── Preferences/
│   └── Goals/
├── AGENTS.md           ← Zo's long-term memory file
└── Getting Started.md  ← The default welcome doc
```

### Key concepts

- **AGENTS.md** — This file is Zo's long-term memory for your workspace. Zo reads it at the start of conversations to remember context about your setup, integrations, and preferences. You can edit it directly or ask Zo to update it.
- **User Context folder** — Create a folder with info about yourself (your role, preferences, goals). Zo can reference it to give you more personalized answers.
- **Files are real files** — They're stored in open formats (Markdown, JSON, SQLite, etc.), not locked in a proprietary system. You can sync them with the Zo desktop app.

### Working with files in chat

You can reference any file in your workspace from the chat. Zo can read, edit, create, and delete files. You can drag and drop files from files window into the chat. Just describe what you want:

- "Create a note called meeting-notes.md with today's agenda"
- "Read my resume and suggest improvements"
- "Find all PDFs in my Documents folder"

---

## 5. Skills: Teaching Zo New Tricks

A **skill** is a reusable set of instructions that teaches Zo how to do something specific. Think of skills like apps on your phone — each one gives Zo a new ability.

### What's inside a skill?

A skill lives in a folder under `Skills/` and has:

- **SKILL.md** — The instruction manual. This tells Zo *what the skill does* and *how to run it*. It's written in plain English with some structured metadata at the top.
- **scripts/** — Small programs that do the actual work (written in TypeScript or Python). These are the skill's "hands."
- **references/** — Extra documentation or context the skill might need.
- **assets/** — Static files like templates or images.

### How do you use a skill?

Just talk about it in chat. If you have a skill called `notion-add-task`, you can say:

> "Add a task: finish the proposal, due Friday, project: Work"

Zo recognizes this matches the skill and runs it automatically. Some skills are also triggered by **rules** (see Section 7).

### Example skills (from a real setup)

| Skill | What It Does |
| --- | --- |
| `notion-add-task` | Adds tasks to your Notion to-do list with dates, projects, and status |
| `notion-tasks` | Queries your task list — "what's due today?", "what's overdue?" |
| `reminders` | Parses "remind me to X in 2 hours" and sends you an SMS at the right time |
| `notebook` | Captures your thoughts from a conversation and organizes them into organized journals |
| `github` | Interacts with GitHub repos — issues, PRs, CI status |
| `zo-twitter` | Reads and posts to X/Twitter using your account |
|  |  |
| `pdf` | Extracts text, merges, splits, and fills PDF forms |
| `social-content` | Helps create and optimize social media posts |

### How to create a skill

Ask Zo: "Create a skill called X that does Y." Zo will scaffold the folder, write the SKILL.md, and create any necessary scripts. You can also install community skills from the [skills registry](https://agentskills.io).

### Why skills matter

Skills are what make Zo *yours*. Out of the box, Zo is a general-purpose AI. With skills, it becomes a specialist in your specific workflows. Over time, you build up a library of skills that makes Zo more capable the longer you use it.

---

## 6. Agents: Things That Run While You Sleep

An **agent** is a task that Zo runs on a schedule, without you being there. You set it up once, and Zo handles it on autopilot.

### Examples

- "Every morning at 8am, check the news about AI and text me a summary"
- "Every Friday at 5pm, review my tasks for next week and email me a plan"
- "Once a day, back up my X bookmarks"
- "Every 6 hours, check if a specific product is back in stock — text me only if it is"

### How to create one

Just ask Zo in the chat:

> "Every day at 9am, check my overdue tasks in Notion and text me a summary"

Zo will create the agent with the right schedule, instructions, and delivery method (chat, SMS, or email). You can manage all your agents at [Agents](/?t=agents).

### Key details

- Agents run as **non-interactive** sessions — Zo does the work and delivers the result, it doesn't wait for your input mid-run.
- You choose a **delivery method**: the result can go to chat (visible next time you open Zo), SMS (text to your phone), or email.
- The schedule uses **rrule** format under the hood (like calendar recurring events), but you just describe it in plain English — Zo handles the formatting.

### **Agents vs. Skills**

**Skills are *abilities* — they define what Zo can do. Agents are *schedules* — they define when Zo does it.** An agent might run a skill ("every morning, run the notion-tasks skill and text me the results"), but agents can also do anything Zo can do in chat.

---

## 7. Rules: Setting Boundaries and Preferences

**Rules** tell Zo how to behave. They're persistent preferences that carry across every conversation.

### Two types

1. **Always-applied rules** — These are active in every conversation. Example:

   - "My name is Dan. Address me by name when appropriate."

2. **Conditional rules** — These activate only when a condition is met. Example:

   - *Condition:* User says "remind me to..."
   - *Rule:* Parse the reminder, schedule an SMS, and confirm.

### How to create them

Just tell Zo what you want it to remember:

> "From now on, when I say 'add a task', use my Notion tasks database"

> "Always keep your responses short and skip the pleasantries"

> "When I ask to push to GitHub, remind me to check the architecture diagram"

Zo creates the rule and follows it in future conversations. You can view and manage all rules at [Settings &gt; AI &gt; Rules](/?t=settings&s=ai&d=rules).

### Why rules matter



Rules prevent you from having to repeat yourself. Without them, every conversation starts from zero. With them, Zo remembers your preferences, your workflows, and your pet peeves — permanently.

---

## 8. Personas: Giving Zo a Different Voice

A **persona** is a custom personality and instruction set you can apply to Zo. It changes how Zo talks, what model it uses, and how it approaches tasks.

### Example

You could create a persona called **J.A.R.V.I.S.** — a composed, British-accented AI assistant modeled after the Iron Man character. It speaks formally, anticipates your needs, and uses dry wit. Or you could make a casual coding buddy, a strict editor, or a creative brainstorming partner.

### How to set one up

Go to [Settings &gt; AI &gt; Personas](/?t=settings&s=ai&d=personas), or just ask Zo:

> "Create a persona called 'Coach' that motivates me, keeps me accountable, and speaks like a personal trainer"

Each persona can use a different AI model, so your creative persona might use a different brain than your coding persona.

---

## 9. Hosting and Live Services

Because Zo is a real server, you can **run software on it** — not just chat about software. This is one of the biggest differences from other AI tools.

### What is a "service"?

A service is a program that runs continuously on your Zo, with a public URL. Examples:

| Service | What It Is |
| --- | --- |
| A Next.js app | A full web application with a dashboard, database, and API |
| An API server | A backend that other apps or services can call |
| A health dashboard | A personal data visualization tool |
| An SSH server | Remote terminal access to your Zo |
| A bookmark analyzer | A tool that processes and categorizes your saved links |

### How services work

1. You build something (or ask Zo to build it)
2. You register it as a service — Zo assigns it a public HTTPS URL like `https://myservice-yourhandle.zocomputer.io`
3. It runs in the background, restarts if it crashes, and stays live

You manage services at [Hosting &gt; Services](/?t=sites&s=services).

### Zo Sites

For simpler web projects, Zo has a built-in site hosting system. Ask Zo to "create a site" and it scaffolds a project, builds it, and deploys it — all from the chat. You manage them at [Hosting &gt; Sites](/?t=sites&s=sites).

### Why this matters

Most AI tools can generate code. Zo can generate code *and run it, live, on your server, with a URL*. That's the difference between "here's some code" and "here's a working product."

---

## 10. zo.space: Your Personal Corner of the Internet

Every Zo user gets a **zo.space** — a personal website at `https://yourhandle.zo.space`. Think of it as your own little internet real estate.

### What can you put there?

- **Pages** — React-based web pages (a portfolio, a dashboard, a tool, a landing page, a link-in-bio page)
- **APIs** — Backend endpoints that accept and return data (webhooks, data feeds, integrations)
- **Assets** — Images, files, and media served from your space

### How it works

Ask Zo to create a page or API route:

> "Create a page on my zo.space at /about with my bio and links to my projects"

> "Create an API at /api/status that returns whether my services are running"

Zo writes the code and deploys it instantly. Pages can be **public** (anyone can see) or **private** (only you).

### Why zo.space matters

It's a zero-friction way to put things on the internet. No GitHub repos, no deployment pipelines, no hosting configuration. Just say what you want, and it's live.

---

## 11. APIs: How Software Talks to Software

You'll see the word **API** come up a lot in this guide — and everywhere else in the Zo world. It's worth understanding what it actually means, because APIs are the backbone of everything Zo does behind the scenes.

### The simple version

An **API** (Application Programming Interface) is a way for one piece of software to talk to another. Think of it like a waiter at a restaurant: you (the customer) don't go into the kitchen — you tell the waiter what you want, the waiter tells the kitchen, and the kitchen sends back your food. The waiter is the API.

When Zo checks your calendar, it doesn't log into Google and click around like a human. It sends a request to Google's Calendar API — "give me today's events for this user" — and Google sends back the data. Clean, fast, no UI needed.

### Why Zo needs APIs

Zo is powerful because it can connect to almost anything. But it can only connect to services that have APIs. Here's what APIs let Zo do:

- **Read and write to Notion** — The Notion API lets Zo create tasks, query databases, and update pages
- **Post to X/Twitter** — The X API lets Zo read timelines, post tweets, and search conversations
- **Send you texts** — Zo uses a messaging API to deliver SMS to your phone
- **Search the web** — Zo calls search APIs to find information in real time
- **Use AI models** — When Zo talks to Claude or GPT, it's calling their APIs

Without APIs, Zo would just be a chatbot with no hands. APIs are the hands.

### How you interact with APIs on Zo

You usually don't need to think about APIs directly. When you say "check my email," Zo handles the API call behind the scenes. But as you build more advanced setups, you'll start working with APIs directly:

- **Getting an API key** — You sign up for a service's developer portal, create an "app" or "project," and they give you a key (a long secret string). This key authenticates your requests.
- **Storing the key** — You put it in Zo's Secrets ([Settings > Advanced](/?t=settings&s=advanced)) so your skills and services can use it securely.
- **Building skills that call APIs** — When you ask Zo to "create a skill that pulls data from [some service]," Zo writes code that calls that service's API.

### The pattern is always the same

1. Find the service's API documentation (usually at `docs.service.com` or `developer.service.com`)
2. Get an API key
3. Store the key in Zo Secrets
4. Ask Zo to build a skill or service that uses it

Once you've done this two or three times, it becomes second nature. And the payoff is huge — you can connect Zo to virtually any service on the internet.

---

## 12. APIs vs. Zo Integrations: When to Use Which

Zo has two ways to connect to external services: **built-in integrations** (the ones you toggle on at [Settings > Integrations](/?t=settings&s=integrations)) and **direct API connections** (where you get an API key and build a skill).

### Built-in integrations

These are pre-built connections that Zo maintains for popular services:

- Gmail
- Google Calendar
- Google Drive
- Spotify
- Notion
- Linear
- Dropbox
- Airtable
- OneDrive

You click "Connect," authorize your account, and you're done. Zo can immediately read your email, check your calendar, play music, etc.

### Direct API connections

These are custom connections where you get an API key from the service, store it in Zo Secrets, and build (or ask Zo to build) a skill that talks to the API directly.

### Which should you use?

**Direct APIs are almost always better.** Here's why:

| | Built-in Integration | Direct API |
|---|---|---|
| **Setup** | One click | Get key + create skill |
| **Flexibility** | Limited to what Zo pre-built | Full access to everything the service offers |
| **Customization** | Can't change how it works | You control the exact behavior |
| **Depth** | Basic operations (read, list, search) | Advanced operations, custom queries, bulk actions |
| **Reliability** | Depends on Zo's integration layer | Direct connection — fewer things to break |
| **Updates** | Waits for Zo team to update | You update when you want |

### The recommendation

- **Use built-in integrations for:** Gmail, Google Calendar, and Spotify. These cover the basics well — reading email, checking your schedule, controlling music. They work out of the box and you won't need much more depth for everyday use.

- **Use direct APIs for everything else** — especially Notion, X/Twitter, and any service central to your workflow. The API gives you full control. For example:
  - The Notion built-in integration gives you basic read access. The Notion API (with a custom skill) lets you create tasks, update databases, build complex queries, and automate workflows.
  - The X/Twitter built-in tools let you search. The X API lets you post, read DMs, track engagement, manage bookmarks, and build monitoring pipelines.

- **Always use direct APIs for:** Any service that's core to a software project you're building on Zo. If your app needs to talk to Stripe, a database, a weather service, or any external data source — go direct.

### How to set up a direct API connection

1. Go to the service's developer site and create an API key
2. Store it in [Settings > Advanced](/?t=settings&s=advanced) under Secrets
3. Ask Zo: "Create a skill that connects to [service] using my API key in `SERVICE_API_KEY`"
4. Zo will read the API docs, write the skill, and set it up

The first time takes a bit of effort. After that, you have a connection that's more powerful and flexible than any pre-built integration.

---

## 13. Bring Your Own AI: Claude Code and GPT

Zo lets you plug in your **own** AI subscriptions. This is called "Bring Your Own Key" (BYOK).

### Claude Code (Anthropic)

If you have an Anthropic subscription (the company that makes Claude), you can use it as your Zo model. This is especially powerful because:

- **Claude Code** is Anthropic's coding-focused product — it's designed for software engineering
- When you connect it to Zo, you get Claude's full capability running on your personal server
- Your Zo files, skills, and tools become available to Claude directly

To set it up: Go to [Settings &gt; AI &gt; Providers](/?t=settings&s=ai&d=providers) and add your Anthropic API key, or connect your Claude Code subscription.

### OpenAI (GPT)

Same idea — if you have an OpenAI API key, you can use GPT-4o, o1, o3, or any OpenAI model through Zo. Add your key at [Settings &gt; AI &gt; Providers](/?t=settings&s=ai&d=providers).

### Why bring your own key?

1. **Cost control** — Use your own quota instead of Zo credits
2. **Model access** — Get the latest models the day they drop
3. **Flexibility** — Switch between providers depending on the task
4. **Power** — Combine the best AI models with Zo's tools, files, and hosting

### MCP: How it all connects

When external AI tools like Claude Code connect to Zo, they use something called **MCP** (Model Context Protocol). MCP is a standard that lets AI models talk to external tools and services. When Claude Code connects to your Zo via MCP, it gains access to all of Zo's capabilities — file management, web search, media generation, app integrations, and more. You don't need to understand MCP deeply — just know that it's the bridge that lets your external AI subscriptions work *through* Zo.

---

## 14. Secrets: Keeping Your Keys Safe

As you connect more services and build more integrations, you'll accumulate **API keys** — secret passwords that let software talk to other software.

### What are API keys?

When you sign up for a service (like the X/Twitter API, Notion API, or Anthropic API), they give you a unique key — a long string of characters. This key is like a password that proves your identity to that service.

### Where to store them

**Never put API keys directly in your code or files.** Instead, go to [Settings &gt; Advanced](/?t=settings&s=advanced) and add them as **Secrets**. These are stored as secure environment variables that your skills and services can read, but they're never exposed in your workspace.

### How skills and services use them

When a skill needs an API key, it reads it from the environment. For example, a Notion skill reads `NOTION_DZIMM_TOKEN`, a Twitter skill reads `X_API_KEY`, etc. You set the secret once, and everything that needs it can access it securely.

### Access Tokens (the other kind)

There's also an **Access Tokens** section in Advanced settings. These are tokens for *external tools to access your Zo* (not the other way around). If you want Claude Code or another external tool to connect to your Zo via MCP or HTTP API, you generate an access token here.

### The simple rule

- **Secrets** = keys that let Zo talk to other services (outbound)
- **Access Tokens** = keys that let other services talk to Zo (inbound)

---

## 15. Billing and the Pro Plan

### How Zo billing works

Zo has a subscription plan plus **AI credits** that cover your model usage.

- Your plan determines your compute tier (CPU, RAM, storage), the number of custom domains, and included credits
- AI credits are consumed when Zo uses an AI model to respond to you, run agents, or execute skills
- If you bring your own API keys (Section 11), those interactions use your own key's quota instead of Zo credits

### The Pro plan as a starting point

The **Pro plan** is the sweet spot for someone who wants to seriously build on Zo. It gives you:

- More compute power (faster builds, more services running simultaneously)
- More storage for files, databases, and media
- More included AI credits per month
- Custom domain support (connect your own domain to your services and zo.space)
- Priority support

You can view plans and manage billing at [Billing](/?t=billing).

### Cost strategy

1. **Start with Pro** for the compute headroom and credit allotment
2. **Bring your own Claude or GPT key** to avoid burning credits on heavy conversations
3. **Use lighter models** (like Haiku or GPT-4o-mini) for simple tasks, heavier models for deep work
4. **Monitor usage** at [Billing &gt; Usage](/?t=billing&s=usage) to understand your patterns

---

## 16. The DZimm 5-Layer Setup Strategy

Here's a practical playbook for going from "I just signed up" to "I have a fully personalized AI computer." These layers build on each other — start at Layer 1 and add as you go.

---

### Layer 1: Life Operating System (Notion + Zo)

**What:** Connect Notion to Zo and use it as your personal command center.

**Why:** Before you build anything fancy, you need a place to organize your life — tasks, goals, projects, journals. Notion is excellent for this, and Zo can read and write to it directly.

**How to set up:**

1. Go to [Settings &gt; Integrations &gt; Connections](/?t=settings&s=integrations&d=integrations:connections) and connect Notion OR \[dan recommends\] get the paid notion subscription and connect via API. Ask ZO how to connect notion API. you gotta tough it out to find these types of things, but they unlock everything.
2. Set up a **Life OS** template in Notion (or use one of the many free templates available) — include databases for Tasks, Projects, Goals, Habits, and a Journal \[Dan recommends this template <https://chrisnotion.gumroad.com/l/lifeosdashboard?\_gl=1\*1yznw38\*\_ga\*MTcyNTc1MTk1My4xNzY5MTI5NTIy\*\_ga_6LJN6D94N6\*czE3NzMzNzE5NDAkbzYkZzAkdDE3NzMzNzE5NDAkajYwJGwwJGgw>\]
3. Ask Zo to create skills for your most common actions:
   - "Create a skill that adds tasks to my Notion task database"
   - "Create a skill that shows me my tasks due today"
4. Set up **rules** so natural phrases trigger the skills:
   - "When I say 'add a task', use the notion-add-task skill"
   - "When I say 'remind me to...', schedule an SMS reminder and add it to Notion"
5. Update your **AGENTS.md** file with your Notion database IDs and structure — this becomes Zo's persistent memory of your system

**What you get:** A personal AI that manages your to-do list, checks your goals, and texts you reminders — all through natural conversation.

---

### Layer 2: Research and Information Pipelines (X API + Web Tools)

**What:** Set up automated research feeds, bookmark analysis, and social monitoring.

**Why:** Zo has powerful web tools — search, scraping, Twitter/X access, article saving. Layer 2 turns these from one-off actions into persistent research infrastructure.

**How to set up:**

1. Get an **X/Twitter API key** (or use cookie-based auth via the `zo-twitter` skill) and store it in [Settings &gt; Advanced](/?t=settings&s=advanced) as a secret
2. Create a skill (or ask Zo to build one) that pulls and categorizes your X bookmarks
3. Set up a hosted **bookmark analysis service** that runs continuously and categorizes your saved content
4. Create **agents** for automated research:
   - "Every day at 2pm, search X for posts about \[your topic\] and save a summary"
   - "Every morning, search the web for news about \[your industry\] and text me the highlights"
5. Use the `x-monitor` skill to track specific topics or accounts and get notified of developments

**What you get:** A personal research assistant that monitors the internet for you, catalogs what you save, and surfaces what matters.

---

### Layer 3: App Integrations and Browser Access

**What:** Connect your Google workspace, log into key sites through Zo's browser, and wire up external services.

**Why:** The more Zo can see and do across your digital life, the more useful it becomes. This layer connects the dots.

**How to set up:**

1. **Google Workspace** — Connect Gmail, Calendar, and Drive at [Settings &gt; Integrations](/?t=settings&s=integrations). This lets you:
   - "What's on my calendar today?"
   - "Search my email for the contract from last week"
   - "Save this file to my Google Drive"
2. **Browser sessions** — Open [Zo's Browser](/browser) and log into sites you use frequently (Instagram, Substack, Notion web, etc.). Zo can then browse these sites as you — reading content, filling forms, taking screenshots
3. **Spotify** — Connect at [Settings &gt; Integrations](/?t=settings&s=integrations) for music control: "Play my Discover Weekly", "What's currently playing?"
4. **Custom integrations** — For services that don't have built-in connections, ask Zo to create a skill. Zo will research the API, help you get a key, and write the integration code

**What you get:** An AI that can see your calendar, read your email, browse the web as you, play music, and interact with any service that has an API.

---

### Layer 4: Build and Ship Real Software

**What:** Use Zo as a development environment for full-scale software projects.

**Why:** Zo isn't just for notes and tasks — it's a real Linux server with Node.js, Python, and all the tools you need to build production software. Combined with an AI that can write code, run it, and debug it live, you have a complete development platform.

**How to set up:**

1. Start a project in your workspace — either from scratch or by cloning a GitHub repo (connect GitHub via the `github` skill)
2. Ask Zo to help you build — "Set up a Next.js app with a dashboard that shows \[your data\]"
3. **Register it as a service** — Zo gives it a live HTTPS URL: `https://yourproject-yourhandle.zocomputer.io`
4. Set up **dev and prod environments** — register two services on different ports (e.g., prod on 3002, dev on 3003) so you can test changes without breaking the live version
5. Use Zo's built-in tools for the full dev cycle:
   - Database: SQLite or DuckDB files right in your project
   - API routes: Build backends in your framework of choice
   - External data: Zo can fetch from any API, scrape any site, and process any data format
6. For heavy coding sessions, connect **Claude Code** via MCP for the best coding experience — it gets full access to your project files and Zo's tools

**What you get:** A production software platform where your AI pair-programs with you, hosts your app, and keeps it running. No separate hosting, no deployment pipelines, no DevOps.

---

### Layer 5: Build On Top of Everything

**What:** Now that your foundation is in place — organization (Layer 1), research (Layer 2), integrations (Layer 3), and software projects (Layer 4) — Layer 5 is where you combine everything into things that actually make your life better, and potentially make things other people want to use too.

**Why:** The first four layers give Zo capabilities. Layer 5 is about *using those capabilities together* to build things that couldn't exist without the full stack underneath. This is where your personal AI computer starts paying dividends.

**What to build:**

1. **Cross-layer morning briefings** — An agent that checks your Notion tasks, scans your research feeds, reviews your calendar, checks your email, and texts you a single unified summary every morning. This isn't just "read my calendar" — it's pulling from every layer at once.

2. **Personal dashboards** — Build a zo.space page or hosted service that visualizes your life data: tasks completed, research trends, project status, health metrics. Because everything is on one server, you can query across all your databases and APIs in a single view.

3. **Custom automation chains** — Skills that trigger other skills. Example: when you save a bookmark on X (Layer 2), Zo automatically categorizes it, checks if it's relevant to any active project (Layer 1), and if so, adds a task to review it. No human in the loop.

4. **Tools for other people** — Once you've built something useful for yourself, consider making it available. Your zo.space can host public tools, your services can have public APIs, and you can share skills. A research dashboard you built for yourself could become a tool your team uses.

5. **Monetizable products** — Zo can host payment-enabled products via Stripe. That health dashboard from Layer 4? Add a public version with a paywall. That research feed from Layer 2? Package it as a subscription newsletter that sends automatically.

6. **Compound agents** — Agents that don't just check one thing — they orchestrate. "Every Sunday at 6pm, review everything I did this week across all projects, draft a weekly recap, identify the top 3 priorities for next week, and send it to me as a formatted email." This agent is touching Notion, GitHub, your research feeds, your calendar, and your email — all in one run.

**How to approach it:**

- Start by asking: "What do I wish I had a dashboard for?" or "What repetitive thing do I do that touches multiple tools?"
- Build the simplest version first — a single agent or a single zo.space page
- Expand from there. Layer 5 is never "done" — it's the ongoing practice of combining your layers into increasingly useful things

**What you get:** A personal AI computer that doesn't just have capabilities — it *uses them together* to run parts of your life, work, and projects on autopilot. The system becomes greater than the sum of its parts.

---

### How the layers work together

```
Layer 5: Build On Top ──────── Combine everything into products, dashboards, automations
    ↑
Layer 4: Software Projects ─── Build and run real applications
    ↑
Layer 3: App + Browser ──────── Connect to external services
    ↑
Layer 2: Research Pipelines ─── Automated info gathering
    ↑
Layer 1: Life OS (Notion) ───── Personal command center
```

Each layer makes the layers above it more useful. Your Life OS (Layer 1) organizes the research (Layer 2). Your app integrations (Layer 3) feed data into your software projects (Layer 4). Layer 5 ties it all together — combining capabilities from every layer into compound automations, dashboards, and products that couldn't exist without the full stack underneath.

**You don't need to build all 5 layers at once.** Start with Layer 1 and stay there for a week. Add a layer when you feel ready. The system compounds — each layer makes Zo smarter and more useful.

---

## 17. Key Terms Glossary

| Term | What It Means |
| --- | --- |
| **Skill** | A reusable set of instructions + scripts that gives Zo a specific ability (like "add a Notion task" or "search Twitter") |
| **Agent** | A scheduled task that Zo runs automatically on a recurring basis (like a cron job, but in plain English) |
| **Rule** | A persistent preference or behavior that Zo follows across all conversations |
| **Persona** | A custom personality/voice configuration for Zo — changes how it talks and which model it uses |
| **Service** | A program running continuously on your Zo server with a public URL |
| **zo.space** | Your personal website hosted on Zo — pages, APIs, and assets at yourhandle.zo.space |
| **API** | Application Programming Interface — a way for software to talk to other software. When you hear "API key," think "password for a service" |
| **API Key** | A secret token that authenticates you to an external service (like Twitter, Notion, or OpenAI) |
| **MCP** | Model Context Protocol — the standard that lets external AI tools (like Claude Code) connect to and use Zo's capabilities |
| **BYOK** | Bring Your Own Key — using your own AI provider subscription (Anthropic, OpenAI, etc.) through Zo instead of Zo credits |
| **AGENTS.md** | A special file in your workspace that serves as Zo's long-term memory — it reads this at the start of every conversation |
| **Secrets** | Securely stored environment variables (API keys, tokens) that your skills and services can access without them being visible in your files |
| **Access Token** | A key you generate to let external tools connect to your Zo (the reverse of Secrets) |
| **Tool** | A specific action Zo can take — like "web_search," "send_sms," "read_file," or "generate_image." Zo has dozens of built-in tools |
| **rrule** | Recurrence rule — the format used to define agent schedules (you write in English, Zo converts to rrule) |
| **Webhook** | A URL that receives data when something happens in another service (like "Stripe sends payment info to my zo.space API") |

---

## Getting Help

- **In Zo:** Just ask. "How do I set up X?" or "Help me connect Y"
- **Discord:** [Join the Zo community](https://discord.gg/invite/zocomputer) for help from other users and the team
- **Email:** help@zocomputer.com
- **Docs:** [docs.zocomputer.com](https://docs.zocomputer.com)
- **Office hours:** [lu.ma/zocomputer](https://lu.ma/zocomputer)

---

*This guide was written as a Zo Skill. To run it interactively, say: "Run the zo-setup-guide skill" — Zo will walk you through each section and help you set things up step by step.*

## Related Skills
- **github** — set up GitHub integration as part of the development environment (Layer 4)
- **slack** — connect Slack for team communication and notification workflows

