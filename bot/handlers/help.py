def handle_help(command: str) -> str:
    """Handle /help command - lists all available commands."""
    return """LMS Bot - Available Commands

Slash Commands:
/start - Welcome message and introduction
/help - This help message
/health - Check if the backend is running
/labs - List all available labs
/scores <lab> - View per-task pass rates for a specific lab

Examples:
/scores lab-04 - Show pass rates for Lab 04

Natural Language Queries:
You can also ask questions in plain English:
- "what labs are available?"
- "show me scores for lab 4"
- "who are the top 5 students?"
- "which lab has the lowest pass rate?"
- "how many students are enrolled?"
"""

