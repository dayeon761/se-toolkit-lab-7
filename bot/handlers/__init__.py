"""
Command handlers for the LMS bot.

Handlers are pure functions that take input and return text.
They don't depend on Telegram - same logic works from --test mode,
unit tests, or Telegram.
"""


def handle_start(text: str) -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help(text: str) -> str:
    """Handle /help command."""
    return "Available commands:\n/start - Welcome message\n/help - This help message\n/health - Backend status\n/labs - List available labs\n/scores <lab> - Per-task pass rates"


def handle_health(text: str) -> str:
    """Handle /health command."""
    return "Backend status: OK (placeholder)"


def handle_labs(text: str) -> str:
    """Handle /labs command."""
    return "Available labs: Lab 01, Lab 02, Lab 03, Lab 04, Lab 05, Lab 06, Lab 07"


def handle_scores(text: str) -> str:
    """Handle /scores command."""
    # Extract lab name from command (e.g., "/scores lab-01" -> "lab-01")
    parts = text.split()
    if len(parts) > 1:
        lab_name = parts[1]
        return f"Scores for {lab_name}: Coming soon (Task 2)"
    return "Scores: Use /scores <lab-name> to see pass rates (placeholder)"


def handle_unknown(text: str) -> str:
    """Handle unknown commands."""
    return "Unknown command. Use /help to see available commands."
