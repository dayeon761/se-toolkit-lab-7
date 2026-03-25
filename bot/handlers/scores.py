def handle_scores(command: str) -> str:
    """Handle /scores command"""
    parts = command.split()
    if len(parts) > 1:
        lab = parts[1]
        return f"Scores for {lab}: Not implemented yet (Task 2)"
    return "Usage: /scores <lab>"
