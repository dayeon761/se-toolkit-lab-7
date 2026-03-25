# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

### Prerequisites

Before deploying the bot, ensure you have:

1. **VM access** with Docker and Docker Compose installed
2. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
3. **LMS API credentials** (`LMS_API_KEY`, `LMS_API_BASE_URL`)
4. **LLM credentials** (`LLM_API_KEY`, `LLM_API_BASE_URL`, `LLM_API_MODEL`)

### Environment Setup

1. Clone the repository on your VM:

   ```bash
   cd ~
   git clone <your-repo-url>
   cd se-toolkit-lab-7
   ```

2. Create `.env.bot.secret` in the project root:

   ```bash
   cp .env.bot.example .env.bot.secret
   ```

3. Edit `.env.bot.secret` and fill in:

   ```env
   BOT_TOKEN=your-telegram-bot-token-from-botfather
   LMS_API_BASE_URL=http://backend:8000
   LMS_API_KEY=your-lms-api-key
   LLM_API_KEY=your-llm-api-key
   LLM_API_BASE_URL=http://host.docker.internal:42005
   LLM_API_MODEL=qwen-2.5-7b
   ```

   > **Note**: `LMS_API_BASE_URL` uses `backend` (Docker service name), not `localhost`.
   > For `LLM_API_BASE_URL`, use `host.docker.internal` to reach the host machine from the container.

4. Ensure `.env.docker.secret` exists with backend credentials (for the backend service).

### Deploy with Docker Compose

1. Build and start all services:

   ```bash
   docker compose --env-file .env.docker.secret up --build -d
   ```

2. Check that all services are running:

   ```bash
   docker compose --env-file .env.docker.secret ps
   ```

   You should see `bot`, `backend`, `postgres`, `caddy`, and `pgadmin`.

3. Check bot logs for errors:

   ```bash
   docker compose --env-file .env.docker.secret logs bot --tail 20
   ```

   Look for "Bot is running..." or "Application started" messages.

### Verify Deployment

1. **Test mode** (on VM, before deploying):

   ```bash
   cd bot
   uv sync
   uv run bot.py --test "/start"
   uv run bot.py --test "/health"
   uv run bot.py --test "what labs are available"
   ```

2. **Telegram** (after deploying):
   - Open your bot in Telegram
   - Send `/start` — should see welcome message
   - Send `/health` — should see backend status
   - Send "what labs are available?" — should list labs

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot container keeps restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error. |
| `/health` fails in container | `LMS_API_BASE_URL` must be `http://backend:8000` (not `localhost`). |
| LLM queries fail | `LLM_API_BASE_URL` must use `host.docker.internal` (not `localhost`). |
| "BOT_TOKEN is required" | Ensure `BOT_TOKEN` is in `.env.docker.secret` or passed to container. |
| Backend not reachable | Ensure backend is running: `curl -sf http://localhost:42002/docs` |

### Stopping the Bot

```bash
# Stop only the bot
docker compose --env-file .env.docker.secret stop bot

# Stop all services
docker compose --env-file .env.docker.secret down
```
