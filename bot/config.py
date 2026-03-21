"""
Configuration loader for the bot.
Reads secrets from .env.bot.secret file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Bot configuration."""

    def __init__(self):
        # Load environment variables from .env.bot.secret
        env_path = Path(__file__).resolve().parent / ".env.bot.secret"
        load_dotenv(env_path)

        self.bot_token = os.getenv("BOT_TOKEN", "")
        self.lms_api_base_url = os.getenv("LMS_API_BASE_URL", "")
        self.lms_api_key = os.getenv("LMS_API_KEY", "")
        self.llm_api_model = os.getenv("LLM_API_MODEL", "coder-model")
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_api_base_url = os.getenv("LLM_API_BASE_URL", "")


def load_config() -> Config:
    """Load and return bot configuration."""
    return Config()
