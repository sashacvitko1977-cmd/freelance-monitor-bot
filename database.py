"""SQLite persistence for deduplication and history."""

from __future__ import annotations

import os
from pathlib import Path

import aiosqlite

from models import Project, StoredProject


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self.connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        Path(os.path.dirname(self.path) or ".").mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.path)
        self.connection.row_factory = aiosqlite.Row
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                title TEXT NOT NULL DEFAULT '',
                price TEXT NOT NULL DEFAULT ''
            )
        """)
        await self.connection.commit()

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()

    async def contains(self, url: str) -> bool:
        assert self.connection
        cursor = await self.connection.execute("SELECT 1 FROM projects WHERE url = ?", (url,))
        return await cursor.fetchone() is not None

    async def add(self, project: Project) -> bool:
        assert self.connection
        cursor = await self.connection.execute(
            "INSERT OR IGNORE INTO projects(url, title, price) VALUES (?, ?, ?)",
            (project.url, project.title, project.price),
        )
        await self.connection.commit()
        return cursor.rowcount == 1

    async def last(self, limit: int = 10) -> list[StoredProject]:
        assert self.connection
        cursor = await self.connection.execute(
            "SELECT id, url, created_at, title, price FROM projects ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [StoredProject(**dict(row)) for row in await cursor.fetchall()]

    async def count(self) -> int:
        assert self.connection
        cursor = await self.connection.execute("SELECT COUNT(*) AS total FROM projects")
        row = await cursor.fetchone()
        return int(row["total"])
