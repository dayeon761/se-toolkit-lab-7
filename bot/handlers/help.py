def handle_help(command: str) -> str:
    """Handle /help command"""
    return """Available commands:
/start - Welcome message
/help - This help message
/health - Backend status
/labs - List available labs
/scores <lab> - Per-task pass rates"""

