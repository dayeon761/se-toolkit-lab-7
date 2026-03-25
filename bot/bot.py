#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"    # Test mode, prints response to stdout
    uv run bot.py                     # Run Telegram bot
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


def get_handler(command: str):
    """Get handler function for a command."""
    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }
    # Extract command from text (e.g., "/scores lab-01" -> "/scores")
    cmd = command.split()[0] if command else ""
    return handlers.get(cmd, None)


def run_test_mode(command: str) -> None:
    """Run bot in test mode - call handler directly and print result."""
    handler = get_handler(command)
    if handler:
        response = handler(command)
        print(response)
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


async def run_telegram_bot() -> None:
    """Run the Telegram bot."""
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
        from config import load_config
    except ImportError as e:
        print(f"Error: aiogram not installed. Run: uv sync")
        print(f"Details: {e}")
        sys.exit(1)

    config = load_config()

    if not config.bot_token or config.bot_token.startswith("<"):
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        print("Get a token from @BotFather on Telegram")
        sys.exit(1)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(handle_start("/start"))

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(handle_help("/help"))

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        await message.answer(handle_health("/health"))

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        await message.answer(handle_labs("/labs"))

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        await message.answer(handle_scores(f"/scores {lab_name}"))

    print("Bot is running...")
    await dp.start_polling(bot)


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: run handler and print response (e.g., --test '/start')",
    )
    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
