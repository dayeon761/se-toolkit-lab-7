#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"    # Test mode, prints response to stdout
    uv run bot.py --test "what labs are available"  # Natural language query
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
from services.intent_router import handle_natural_query


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


def is_natural_language_query(text: str) -> bool:
    """Check if the input is a natural language query (not a slash command)."""
    return not text.strip().startswith("/")


def run_test_mode(command: str, debug: bool = False) -> None:
    """Run bot in test mode - call handler directly and print result."""
    # Check if this is a natural language query
    if is_natural_language_query(command):
        response = handle_natural_query(command, debug=debug)
        print(response)
        sys.exit(0)

    # Otherwise use command handlers
    handler = get_handler(command)
    if handler:
        response = handler(command)
        print(response)
        sys.exit(0)
    else:
        # Try as natural language query anyway
        response = handle_natural_query(command, debug=debug)
        print(response)
        sys.exit(0)


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

    # Inline keyboard buttons for common queries
    def get_main_keyboard() -> types.InlineKeyboardMarkup:
        """Create inline keyboard with common queries."""
        keyboard = [
            [
                types.InlineKeyboardButton(
                    text="📚 Какие лабы доступны?", callback_data="query_labs"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="📊 Pass rates lab 4", callback_data="query_pass_lab4"
                ),
                types.InlineKeyboardButton(
                    text="🏆 Top 5 студентов", callback_data="query_top5"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="📈 Lowest pass rate", callback_data="query_lowest"
                ),
                types.InlineKeyboardButton(
                    text="👥 Сколько студентов?", callback_data="query_enrolled"
                ),
            ],
        ]
        return types.InlineKeyboardMarkup(
            inline_keyboard=keyboard, one_time_keyboard=True
        )

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        response = handle_start("/start")
        await message.answer(response, reply_markup=get_main_keyboard())

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

    # Handle callback queries from inline buttons
    @dp.callback_query()
    async def process_callback_query(callback_query: types.CallbackQuery):
        await callback_query.answer()  # Acknowledge the callback

        query_map = {
            "query_labs": "what labs are available",
            "query_pass_lab4": "show me scores for lab 4",
            "query_top5": "who are the top 5 students",
            "query_lowest": "which lab has the lowest pass rate",
            "query_enrolled": "how many students are enrolled",
        }

        query = query_map.get(callback_query.data)
        if query:
            # Use debug=False for production
            response = handle_natural_query(query, debug=False)
            await callback_query.message.answer(response)

    # Handle all other messages as natural language queries
    @dp.message()
    async def handle_message(message: types.Message):
        if message.text:
            # Use debug=False for production
            response = handle_natural_query(message.text, debug=False)
            await message.answer(response)

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
