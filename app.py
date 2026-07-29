"""Application entrypoint."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot import configure, is_monitoring, router, send_project
from config import load_settings
from database import Database
from filters import matches
from parser import FreelanceParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger(__name__)


async def monitor(bot: Bot, database: Database, parser: FreelanceParser, chat_id: int, interval: int) -> None:
    while True:
        if is_monitoring():
            try:
                projects = await parser.fetch()
                new_count = 0
                for project in reversed(projects):
                    if await database.contains(project.url) or not matches(project):
                        continue
                    await send_project(bot, chat_id, project)
                    await database.add(project)
                    new_count += 1
                log.info("Check complete: found=%s new=%s", len(projects), new_count)
            except Exception:  # noqa: BLE001
                log.exception("Monitoring check failed")
        await asyncio.sleep(interval)


async def main() -> None:
    settings = load_settings()
    database = Database(settings.database_path)
    await database.connect()
    parser = FreelanceParser(settings)
    bot = Bot(settings.bot_token)
    dispatcher = Dispatcher()
    configure(database)
    dispatcher.include_router(router)
    monitor_task = asyncio.create_task(monitor(bot, database, parser, settings.chat_id, settings.check_interval))
    try:
        await dispatcher.start_polling(bot)
    finally:
        monitor_task.cancel()
        await parser.close()
        await database.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
