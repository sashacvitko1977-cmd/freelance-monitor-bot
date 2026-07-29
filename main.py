import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env")

KEYWORDS = [
    "тг бот", "телеграм бот", "бот", "tg bot", "tgbot",
    "сайт", "лендинг", "landing", "веб-разработка", "web development",
    "веб дизайн", "сайт под ключ", "интернет-магазин", "программирование", "IT"
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def check_freelance_orders():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        url = "https://freelance.ru/task"
        r = requests.get(url, headers=headers, timeout=15)
        
        if not r.ok:
            logging.error("Не удалось загрузить страницу")
            return
        
        soup = BeautifulSoup(r.text, "html.parser")
        orders = []
        
        # Более надёжный парсинг (можно доработать)
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "project/" in href or "task/" in href or "offer/" in href:
                text = link.get_text(strip=True)
                if any(kw.lower() in text.lower() for kw in KEYWORDS):
                    orders.append({
                        "title": text,
                        "link": "https://freelance.ru" + href
                    })
        
        for order in orders:
            text = (
                f"🛒 <b>Новый заказ на freelance.ru</b>\n\n"
                f"📋 {order['title']}\n"
                f"🔗 {order['link']}\n\n"
                f"Присылаем уведомления о заказах по запросу."
            )
            # Отправляем админам (можно изменить на chat_id)
            for admin_id in ADMIN_IDS:  # ADMIN_IDS будет из .env
                try:
                    await bot.send_message(admin_id, text, parse_mode="HTML")
                except:
                    pass
        logging.info(f"Проверено заказов: {len(orders)} новых")
    except Exception as e:
        logging.exception("Ошибка мониторинга")

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("🤖 Мониторинг заказов freelance.ru запущен!\n"
                         "Я буду присылать тебе новые заказы по категории веб-разработки, ТГ-ботов, сайтов и лендингов.\n\n"
                         "Напиши /stop чтобы остановить мониторинг.")

async def main():
    # Загружаем админов
    global ADMIN_IDS
    raw = os.getenv("ADMIN_IDS", "")
    ADMIN_IDS = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
    
    logging.info("Бот запущен...")
    
    # Первичная проверка
    await check_freelance_orders()
    
    # Фоновый цикл каждые 5 минут
    while True:
        try:
            await check_freelance_orders()
            await asyncio.sleep(300)
        except Exception as e:
            logging.exception("Ошибка в мониторинге")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
