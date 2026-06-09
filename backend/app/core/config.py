import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://voicebox:voicebox@127.0.0.1:5432/voicebox",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
