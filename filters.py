"""Configurable project filtering."""

from __future__ import annotations

import re

from config import BLACKLIST, KEYWORDS, MIN_PRICE
from models import Project


def matches(project: Project) -> bool:
    haystack = " ".join((project.title, project.category, project.description)).lower()
    if KEYWORDS and not any(word.lower() in haystack for word in KEYWORDS):
        return False
    if any(word.lower() in haystack for word in BLACKLIST):
        return False
    if project.price_value is not None and project.price_value < MIN_PRICE:
        return False
    return project.price_value is not None or MIN_PRICE <= 0


def parse_price(value: str) -> float | None:
    if not value:
        return None
    numbers = re.findall(r"\d[\d\s.,]*", value.replace("\u00a0", " "))
    if not numbers:
        return None
    raw = numbers[0].replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None
