import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv('.env.bot.secret')

@dataclass
class Config:
    bot_token: str
    lms_api_base_url: str
    lms_api_key: str
    llm_api_key: str
    llm_api_base_url: str
    llm_api_model: str

def load_config() -> Config:
    return Config(
        bot_token=os.getenv('BOT_TOKEN', ''),
        lms_api_base_url=os.getenv('LMS_API_BASE_URL', 'http://localhost:42002'),
        lms_api_key=os.getenv('LMS_API_KEY', ''),
        llm_api_key=os.getenv('LLM_API_KEY', ''),
        llm_api_base_url=os.getenv('LLM_API_BASE_URL', ''),
        llm_api_model=os.getenv('LLM_API_MODEL', ''),
    )
