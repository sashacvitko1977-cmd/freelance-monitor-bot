"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Project:
    url: str
    title: str
    price: str = "\u041d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430"
    price_value: float | None = None
    category: str = "\u041d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430"
    date: str = "\u041d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u0430"
    description: str = "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u0435\u0442"


@dataclass(slots=True)
class StoredProject:
    id: int
    url: str
    created_at: str
    title: str = ""
    price: str = ""
