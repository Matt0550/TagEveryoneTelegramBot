import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import (
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

# Find the root directory of the project (two levels up from src/utils/config.py)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,  # Allows environment variables to be uppercase or lowercase
    )

    # * MARK: GENERAL CONFIG
    ENVIRONMENT: Literal["local", "development", "production"] = "local"
    API_VERSION: str = "v1"
    SENTRY_DSN: str | None = None
    SECRET_KEY: str

    # * MARK: DATABASE CONFIG
    DB_TYPE: Literal["sqlite", "mysql"] = "sqlite"

    # * MARK: MYSQL CONFIG
    MYSQL_SERVER: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "tageveryone_bot"
    MYSQL_PASSWORD: str = "tageveryone_bot_password"
    MYSQL_DB: str = "tageveryone_bot"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DB_TYPE == "mysql":
            return MultiHostUrl.build(
                scheme="mysql+pymysql",
                username=self.MYSQL_USER,
                password=self.MYSQL_PASSWORD,
                host=self.MYSQL_SERVER,
                port=self.MYSQL_PORT,
                path=self.MYSQL_DB,
            ).unicode_string()
        else:
            # Default to SQLite
            db_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../db/input/database-new.db")
            )
            # ensure dir exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return f"sqlite:///{db_path}"

    # * MARK: REDIS / CELERY CONFIG
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_CELERY_DB: int = 0  # Same DB for both Celery Broker and Result Backend
    REDIS_CACHE_DB: int = 1  # Different DB for internal cache

    @property
    def _redis_auth_prefix(self) -> str:
        if self.REDIS_PASSWORD:
            return f":{self.REDIS_PASSWORD}@"
        return ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self._redis_auth_prefix}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_CELERY_DB}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self._redis_auth_prefix}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_CELERY_DB}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_CACHE_URL(self) -> str:
        return f"redis://{self._redis_auth_prefix}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_CACHE_DB}"

    # * MARK: CACHE CONFIG
    CACHE_ENABLED: bool = False
    CACHE_KEY_PREFIX: str = "tetb"
    CACHE_DEFAULT_TTL: int = 3600
    CACHE_USERNAME_TTL: int = 86400
    CACHE_GROUP_ADMINS_TTL: int = 300
    CACHE_LIST_MEMBERS_TTL: int = 300
    CACHE_MEMBER_TAG_TTL: int = 300
    CACHE_LIST_RULES_TTL: int = 300
    CACHE_KNOWN_TAGS_TTL: int = 86400

    # * MARK: TELEGRAM BOT CONFIG
    BOT_TOKEN: str = ""
    OWNER_ID: str = ""
    REPORT_ERRORS_OWNER: bool = True
    SEND_DETAILED_ERRORS_TO_OWNER: bool = False
    WEBAPP_SHORTNAME: str = "app"

    # * MARK: FASTAPI SERVER CONFIG
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1
    API_ENABLE_ADMIN_API: bool = False
    API_BACKEND_CORS_ORIGINS: list[str] = []
    API_SERVER_RELOAD: bool = False
    API_IS_BEHIND_PROXY: bool = False
    API_USE_SSL: bool = False


settings = Settings()  # type: ignore

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}"


def _get_telegram_api_url(method: str) -> str:
    """Build the full Telegram API URL for a given method."""
    return f"{TELEGRAM_API_BASE.format(token=settings.BOT_TOKEN)}/{method}"
