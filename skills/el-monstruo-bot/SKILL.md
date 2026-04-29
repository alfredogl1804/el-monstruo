---
name: el-monstruo-bot
description: Development and deployment context for the Monstruo Telegram Bot MVP. Use when the user asks to update, modify, fix, or redeploy the Telegram bot. Contains the current architecture, repository info, deployment status on Railway, and the evolution roadmap.
---

# El Monstruo Bot — Development Context

Activate when updating, fixing, or deploying the Telegram bot for El Monstruo.

## Current Architecture

- **Interface:** Telegram Bot API (via `python-telegram-bot`)
- **Orchestration:** LangGraph (planned/in-progress), currently using custom routing
- **Brains (6):** GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro, Grok 4.20, Perplexity Sonar Pro, DeepSeek R1
- **Memory:** Supabase `monstruo_memory` table (pgvector for semantic search)
- **Database:** Notion API (for Leads DB)
- **Deployment:** Railway (Project ID: `1dcb47ee-6c01-44bb-baff-d89812382fee`)
- **Repository:** `https://github.com/alfredogl1804/el-monstruo-bot.git` (Private)

## Active Features

1. **Task Classification:** Uses GPT-5.4-mini to route tasks to the right brain
2. **Plan Generation:** Shows a plan before execution with approve/modify buttons
3. **Semantic Memory:** Saves and recalls conversation context from Supabase
4. **Lead Research Flow (`/research`):** Specialized Perplexity + GPT flow that saves directly to Notion

## Known Issues (MUST FIX)

1. **Multiple Instances Conflict:** `409 Conflict: terminated by other getUpdates request`. There is a bot instance running locally in the sandbox (`telegram_bot.py`) AND one on Railway. The local one must be killed before deploying.
2. **Railway Build Error:** Previously failed with `no precompiled python found for core:python3.11.0`. Fixed locally by replacing `runtime.txt` with `nixpacks.toml`, but needs to be pushed to GitHub to trigger Railway redeploy.

## Protocol for Updates

When asked to update the bot:

### Step 1: Read the Source Code
The authoritative source code is in `/home/ubuntu/monstruo-deploy/bot.py`. Read it to understand the current implementation.

### Step 2: Implement Changes
Modify the code in `/home/ubuntu/monstruo-deploy/bot.py`. Test locally if possible, but remember to kill the existing local process first: `pkill -f "python.*bot.py"`.

### Step 3: Push and Deploy
1. Commit changes to the local repo: `cd /home/ubuntu/monstruo-deploy && git add . && git commit -m "Update"`
2. Push to GitHub: `git push origin master`
3. Railway will automatically redeploy from the `master` branch.

### Step 4: Update this Skill
If you add new features, endpoints, or environment variables, MUST update this `SKILL.md` to reflect the new state.

## Environment Variables Required

- `TELEGRAM_TOKEN` (or `TELEGRAM_BOT_TOKEN`)
- `OPENAI_API_KEY`
- `SONAR_API_KEY`
- `XAI_API_KEY`
- `OPENROUTER_API_KEY`
- `NOTION_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

## Evolution Roadmap (Next Steps)

1. **True LangGraph Integration:** Replace the custom `classify_task` / `execute_task` router with a real LangGraph implementation
2. **MCP Integration:** Connect the bot to the local MCP servers (Asana, Zapier, etc.)
3. **Audio Support:** Use ElevenLabs to send voice notes instead of text
4. **Proactive Mode (MAOC):** Add a scheduled job that pings the user proactively

## Governance & Runtime Hardening (April 2026)

Before adding new integrations (Asana, Gmail, Zapier), the bot MUST operate under the **First Governed Runtime** contract. This includes 5 pieces:

### 1. Context Packet
The bot must be injected with its identity and rules in the system prompt:
- **Identity:** Meta-Orchestrator of El Monstruo
- **Rules:** Every task is a mini-project. Present a plan and wait for approval. No external DB writes without confirmation (except Leads).

### 2. Decision Record
Every routing decision (`classify_task`, `generate_plan`) must be logged with a structured JSON containing: `decision_id`, `timestamp`, `input`, `classification`, `routing`, `plan`, and `status`.

### 3. Governance Operations Log (GOL)
An audit trail must record key business events (not debug logs): `TASK_RECEIVED`, `PLAN_GENERATED`, `USER_APPROVED/REJECTED`, `EXECUTION_STARTED/COMPLETED`, `MEMORY_STORED`, `EXTERNAL_WRITE`, `POLICY_VIOLATION`.

### 4. Action Classes (Policy Matrix)
Every bot action falls into one of 5 classes:
1. **Autonomous:** Save memory, classify task.
2. **Post-Action Verification:** `/research` command (investigates then notifies).
3. **Human-in-the-loop (Approval):** General tasks calling brains (GPT, Grok, DeepSeek).
4. **Dry-Run:** (Future) Draft emails without sending.
5. **Forbidden:** Delete DBs, run arbitrary code.

### 5. Operational Map (The Flow)
- **Receives:** Text or commands.
- **Recalls:** Last 5 semantic memories from Supabase.
- **Decides:** Classifies and plans (via GPT-5.4-mini).
- **Yields:** Stops and waits for "Aprobar".
- **Executes:** Calls the optimal brain API.
- **Stores:** Saves the interaction to Supabase and structured data to Notion.
- **Returns:** Formatted text and post-action buttons.
