# Bot Development Plan

## Overview
Telegram bot for LMS interaction with testable handlers and CLI test mode.

## Architecture
- **bot/bot.py**: Entry point with --test mode support
- **bot/handlers/**: Pure functions (no Telegram dependency) for commands
- **bot/services/**: API client for backend communication
- **bot/config.py**: Environment variable loading

## Implementation Strategy

### Phase 1: Scaffold (Task 1)
- Create bot directory structure
- Implement handlers with placeholder responses
- Add --test mode that calls handlers directly
- Configure dependencies via pyproject.toml

### Phase 2: Backend Integration (Task 2)
- Implement actual API calls to LMS backend
- Connect handlers to services
- Handle errors gracefully

### Phase 3: LLM Integration (Task 3)
- Add intent routing for natural language questions
- Integrate with Qwen/OpenRouter for AI responses
- Fallback to command matching

## Key Design Decisions
- **Separation of concerns**: Handlers don't know about Telegram
- **Testability**: --test mode verifies handlers without network
- **Configuration**: Single .env.bot.secret file
- **Dependencies**: Use uv for package management

## File Structure
bot/
├── bot.py # Entry point
├── config.py # Config loading
├── handlers/ # Command handlers
│ ├── init.py
│ ├── start.py
│ ├── help.py
│ ├── health.py
│ └── labs.py
├── services/ # API clients
│ └── lms_client.py
├── pyproject.toml # Dependencies
└── PLAN.md # This file
