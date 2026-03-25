from config import load_config


def handle_start(command: str) -> str:
    """Handle /start command - welcome message."""
    config = load_config()
    bot_name = "LMS Bot"  # Default name
    
    # Try to get bot name from config if available
    if config.bot_token:
        # Could extract bot name from token, but keep it simple
        pass
    
    return f"""Welcome to {bot_name}!

I can help you check your LMS data through Telegram.

Available commands:
/start - Welcome message
/help - List all commands
/health - Check backend status
/labs - List available labs
/scores <lab> - View pass rates for a lab

You can also ask questions in plain language like:
- "what labs are available?"
- "show me scores for lab 4"
- "which lab has the lowest pass rate?"
"""
