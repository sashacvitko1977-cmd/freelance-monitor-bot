"""Freelance.ru project feed parser with retries and browser fallback."""

from __future__ import annotations

import asyncio
import logging
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag

from config import Settings
from filters import parse_price
from models import Project

log = logging.getLogger(__name__)


class FreelanceParser:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (compatible; FreelanceProjectBot/1.0)"})

    async def close(self) -> None:
        await self.client.aclose()

    async def fetch(self) -> list[Project]:
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries):
            try:
                response = await self.client.get(self.settings.freelance_url)
                response.raise_for_status()
                if self._looks_like_challenge(response.text):
                    raise RuntimeError("Freelance.ru returned a JavaScript/anti-bot challenge")
                return self.parse(response.text)
            except (httpx.HTTPError, RuntimeError) as exc:
                last_error = exc
                log.warning("Feed request failed (attempt %s/%s): %s", attempt + 1, self.settings.max_retries, exc)
                if attempt + 1 < self.settings.max_retries:
                    await asyncio.sleep(min(30, 2**attempt))
        if self.settings.use_playwright_fallback:
            try:
                return await self._fetch_with_playwright()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise RuntimeError(f"Could not fetch Freelance.ru feed: {last_error}")

    @staticmethod
    def _looks_like_challenge(html: str) -> bool:
        text = html.lower()
        return len(html) < 20_000 and any(marker in text for marker in ("cloudflare", "checking your browser", "enable javascript"))

    async def _fetch_with_playwright(self) -> list[Project]:
        from playwright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=self.client.headers["user-agent"])
            await page.goto(self.settings.freelance_url, wait_until="domcontentloaded", timeout=int(self.settings.request_timeout * 1000))
            await page.wait_for_timeout(1500)
            html = await page.content()
            await browser.close()
        return self.parse(html)

    def parse(self, html: str) -> list[Project]:
        soup = BeautifulSoup(html, "html.parser")
        result: list[Project] = []
        seen: set[str] = set()
        for link in soup.select('a[href*="/task/view/"]'):
            url = urljoin(self.settings.freelance_url, link.get("href", "")).split("#", 1)[0]
            if not url or url in seen:
                continue
            card = link.find_parent(class_=re.compile(r"task|project|card|item", re.I)) or link.parent
            text = " ".join(card.stripped_strings if isinstance(card, Tag) else link.stripped_strings)
            title = " ".join(link.stripped_strings).strip() or "\u0411\u0435\u0437 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u044f"
            price = self._field(text, r"(?:\u0413\u043e\u043d\u043e\u0440\u0430\u0440|\u0426\u0435\u043d\u0430)\s*([0-9][0-9\s.,]*\s*(?:\u20bd|\u0440\u0443\u0431\.?|\u0440\.?)?)")
            date = self._field(text, r"(\d+\s+(?:\u043c\u0438\u043d\u0443\u0442|\u0447\u0430\u0441|\u0434\u0435\u043d\u044c|\u0434\u043d|\u043d\u0435\u0434\u0435\u043b)[\u0430-\u044f\u0451]*\s+\u043d\u0430\u0437\u0430\u0434)")
            category = self._category(card, text)
            description = text.replace(title, "", 1).strip()[:1000]
            result.append(Project(url=url, title=title, price=price, category=category, date=date, description=description or "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u0435\u0442", price_value=parse_price(price)))
            seen.add(url)
        return result

    @staticmethod
    def _field(text: str, pattern: str) -> str:
        match = re.search(pattern, text, flags=re.I)
        return match.group(1).strip(" :-") if match else "\u041d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430"

    @staticmethod
    def _category(card: Tag | None, text: str) -> str:
        if isinstance(card, Tag):
            for element in card.select('[class*="category"], [class*="specialization"], [class*="tag"]'):
                value = " ".join(element.stripped_strings)
                if value:
                    return value
        match = re.search(r"(\u0412\u0435\u0431-\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430 \u0438 IT|\u0418\u0441\u043a\u0443\u0441\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442|\u0414\u0438\u0437\u0430\u0439\u043d \u0438 \u0411\u0440\u0435\u043d\u0434\u0438\u043d\u0433|\u0422\u0435\u043a\u0441\u0442\u044b \u0438 \u041f\u0435\u0440\u0435\u0432\u043e\u0434\u044b|\u041c\u0430\u0440\u043a\u0435\u0442\u0438\u043d\u0433 \u0438 \u041f\u0440\u043e\u0434\u0432\u0438\u0436\u0435\u043d\u0438\u0435)", text, re.I)
        return match.group(1) if match else "\u041d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430"
