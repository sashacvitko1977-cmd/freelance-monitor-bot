"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

KEYWORDS = [
    "python",
    "telegram",
    "ai",
    "\u0431\u043e\u0442",
    "\u043f\u0430\u0440\u0441\u0435\u0440",
    "it",
    "web",
    "backend",
    "back-end",
    "frontend",
    "front-end",
    "api",
    "\u0441\u0430\u0439\u0442",
    "\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430",
    "\u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435",
    "\u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0430\u0446\u0438\u044f",
    "\u0447\u0430\u0442-\u0431\u043e\u0442",
]
BLACKLIST = ["\u0434\u0438\u0437\u0430\u0439\u043d", "\u043b\u043e\u0433\u043e\u0442\u0438\u043f"]
MIN_PRICE = 1000


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Environment variable {name} is required")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    chat_id: int
    freelance_login: str
    freelance_password: str
    check_interval: int = 10
    freelance_url: str = "https://freelance.ru/task"
    request_timeout: float = 20.0
    max_retries: int = 3
    database_path: str = "data/projects.sqlite3"
    use_playwright_fallback: bool = True


def load_settings() -> Settings:
    return Settings(
        bot_token=_required("BOT_TOKEN"),
        chat_id=int(_required("CHAT_ID")),
        freelance_login=os.getenv("FREELANCE_LOGIN", "").strip(),
        freelance_password=os.getenv("FREELANCE_PASSWORD", "").strip(),
        check_interval=max(1, int(os.getenv("CHECK_INTERVAL", "10"))),
        freelance_url=os.getenv("FREELANCE_URL", "https://freelance.ru/task").strip(),
        request_timeout=max(5.0, float(os.getenv("REQUEST_TIMEOUT", "20"))),
        max_retries=max(1, int(os.getenv("MAX_RETRIES", "3"))),
        database_path=os.getenv("DATABASE_PATH", "data/projects.sqlite3").strip(),
        use_playwright_fallback=os.getenv("USE_PLAYWRIGHT_FALLBACK", "true").lower() in {"1", "true", "yes"},
    )
