# LMS Telegram Bot — Implementation Plan

## Overview

This document describes the implementation plan for the LMS Telegram bot across four tasks. The bot allows users to interact with the Learning Management System backend through Telegram chat, using slash commands and natural language queries powered by an LLM.

---

## Task 1: Plan and Scaffold

**Goal:** Create project structure with testable handler architecture.

### Architecture

- **`bot.py`** — Entry point with `--test` mode and Telegram polling
- **`handlers/`** — Command handlers as pure functions (no Telegram dependency)
- **`config.py`** — Environment variable loading from `.env.bot.secret`
- **`services/`** — API and LLM clients (for Tasks 2–3)

### Key Design Decisions

1. **Separation of Concerns:** Handlers are pure functions that take text input and return text output. They work identically in `--test` mode, unit tests, and Telegram.

2. **Test Mode:** The `--test` flag allows offline testing without Telegram connection. This speeds up development and enables CI/CD.

3. **Configuration:** Secrets (bot token, API keys) are loaded from `.env.bot.secret` which is gitignored.

### Deliverables

- [x] `bot/bot.py` — Entry point with `--test` mode
- [x] `bot/handlers/__init__.py` — Command handlers
- [x] `bot/config.py` — Configuration loader
- [x] `bot/pyproject.toml` — Dependencies
- [ ] `bot/PLAN.md` — This file

---

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

### Implementation Plan

1. **Create `services/api_client.py`:**
   - HTTP client using `httpx`
   - Bearer token authentication with `LMS_API_KEY`
   - Methods: `get_health()`, `get_labs()`, `get_scores(lab_id)`

2. **Update handlers:**
   - `/health` — Call `GET /health`, report up/down status
   - `/labs` — Call `GET /labs/`, format list of available labs
   - `/scores <lab>` — Call `GET /analytics/<lab_id>`, show pass rates

3. **Error handling:**
   - Backend down → friendly message, not crash
   - API errors → log details, show user-friendly message

### Dependencies

- `httpx` — Async HTTP client (already in `pyproject.toml`)

---

## Task 3: Intent-Based Natural Language Routing

**Goal:** Allow users to ask questions in plain language.

### Architecture

```
User message → Intent Router → LLM → Tool Call → API → Response
```

### Implementation Plan

1. **Create `services/llm_client.py`:**
   - OpenAI-compatible API client
   - Tool calling support (9 backend endpoints as tools)

2. **Create `handlers/intent_router.py`:**
   - System prompt with tool descriptions
   - LLM decides which tool to call based on user intent
   - Execute tool, format response

3. **Tool descriptions:**
   - `get_labs()` — List available labs
   - `get_scores(lab_id)` — Get pass rates for a lab
   - `get_health()` — Check backend status
   - ... (all 9 backend endpoints)

### Key Insight

The LLM reads tool descriptions to decide which to call. **Description quality > prompt engineering.** Clear, specific descriptions are essential.

---

## Task 4: Containerize and Document

**Goal:** Deploy bot on VM with Docker.

### Implementation Plan

1. **Create `bot/Dockerfile`:**
   - Multi-stage build (build → runtime)
   - Non-root user for security
   - Copy `.env.bot.secret` at runtime (not build time)

2. **Update `docker-compose.yml`:**
   - Add `bot` service
   - Network: `lms-network` (same as backend)
   - Depends on: `backend`

3. **Documentation:**
   - Update README with deployment instructions
   - Document environment variables
   - Troubleshooting guide

### Deployment Checklist

- [ ] Bot Dockerfile created
- [ ] Added to docker-compose.yml
- [ ] Deployed on VM
- [ ] Bot responds in Telegram
- [ ] README updated

---

## Testing Strategy

### Unit Tests

- Test handlers with mock input
- Test API client with mocked responses
- Test intent router with sample queries

### Integration Tests

- `--test` mode for manual testing
- End-to-end test via Telegram

### Acceptance Criteria

See `lab/tasks/required/task-*.md` for detailed criteria.

---

## Timeline

| Task | Description | Estimated Effort |
|------|-------------|------------------|
| 1 | Scaffold + test mode | 1–2 hours |
| 2 | Backend integration | 2–3 hours |
| 3 | LLM intent routing | 3–4 hours |
| 4 | Containerize + deploy | 1–2 hours |

---

## Notes

- This plan was created with the help of Qwen Code AI assistant.
- The bot builds on patterns from Lab 6 (tool calling) but inside a Telegram bot.
- All secrets must be kept out of git — use `.env.bot.secret`.
