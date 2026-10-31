"""Repositório do feed de atividades em memória."""

from __future__ import annotations

from src.domain.entities.activity_event import ActivityEvent
from src.domain.interfaces.activity_repository import IActivityRepository


class InMemoryActivityRepository(IActivityRepository):
    def __init__(self) -> None:
        self._items: list[ActivityEvent] = []

    async def add(self, event: ActivityEvent) -> None:
        self._items.append(event)

    async def recent(self, limit: int) -> list[ActivityEvent]:
        return sorted(self._items, key=lambda e: e.created_at, reverse=True)[:limit]
