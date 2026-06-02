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

    # * MARK: TELEGRAM BOT CONFIG
    BOT_TOKEN: str = ""
    OWNER_ID: str = ""
    REPORT_ERRORS_OWNER: bool = True
    EVERYONE_COMMANDS: list[str] = ["/everyone", "/all", "@everyone", "@all"]
    SENTRY_DSN: str | None = None

    # * MARK: WEBAPP CONFIG
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 5000
    SECRET_KEY: str | None = None
    WEBSERVER_DEBUG: bool = False
    ENABLE_WEBAPP_SERVER: bool = False

    # * MARK: FASTAPI SERVER CONFIG
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    ENABLE_ADMIN_API: bool = False
    BACKEND_CORS_ORIGINS: list[str] = []
    SERVER_RELOAD: bool = False
    IS_BEHIND_PROXY: bool = False
    USE_SSL: bool = False


settings = Settings()  # type: ignore
