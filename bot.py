"""Telegram bot handlers and message formatting."""

from __future__ import annotations

import html
import logging

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from database import Database
from models import Project

log = logging.getLogger(__name__)
router = Router()
_monitoring = True
_database: Database | None = None


def configure(database: Database) -> None:
    global _database
    _database = database


def is_monitoring() -> bool:
    return _monitoring


def format_project(project: Project) -> str:
    return ("\U0001f4cc <b>\u041d\u043e\u0432\u044b\u0439 \u0437\u0430\u043a\u0430\u0437</b>\n\n"
            f"<b>\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:</b> {html.escape(project.title)}\n\n"
            f"<b>\u0426\u0435\u043d\u0430:</b> {html.escape(project.price)}\n\n"
            f"<b>\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f:</b> {html.escape(project.category)}\n\n"
            f"<b>\u0414\u0430\u0442\u0430:</b> {html.escape(project.date)}\n\n"
            f"<b>\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435:</b> {html.escape(project.description[:700])}\n\n"
            f"<b>\u0421\u0441\u044b\u043b\u043a\u0430:</b> {html.escape(project.url)}\n\n---")


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("\u0411\u043e\u0442 \u0437\u0430\u043f\u0443\u0449\u0435\u043d. \u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433: " + ("\u0430\u043a\u0442\u0438\u0432\u0435\u043d" if _monitoring else "\u043d\u0430 \u043f\u0430\u0443\u0437\u0435"))


@router.message(Command("pause"))
async def pause(message: Message) -> None:
    global _monitoring
    _monitoring = False
    await message.answer("\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u043e\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d.")


@router.message(Command("resume"))
async def resume(message: Message) -> None:
    global _monitoring
    _monitoring = True
    await message.answer("\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0435\u043d.")


@router.message(Command("stats"))
async def stats(message: Message) -> None:
    assert _database
    await message.answer(f"\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043e \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u0432: {await _database.count()}")


@router.message(Command("last"))
async def last(message: Message) -> None:
    assert _database
    projects = await _database.last()
    if not projects:
        await message.answer("\u0418\u0441\u0442\u043e\u0440\u0438\u044f \u043f\u043e\u043a\u0430 \u043f\u0443\u0441\u0442\u0430.")
        return
    unknown_price = "\u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430"
    await message.answer("\n".join(f"{index}. {item.title or item.url} — {item.price or unknown_price}\n{item.url}" for index, item in enumerate(projects, 1)))


async def send_project(bot: Bot, chat_id: int, project: Project) -> None:
    await bot.send_message(chat_id, format_project(project), disable_web_page_preview=False)
