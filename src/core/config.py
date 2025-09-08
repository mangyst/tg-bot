import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Подключение к базе данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./testbase.db')

# Токен bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
