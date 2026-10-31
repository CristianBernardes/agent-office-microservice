"""Porta de persistência do feed de atividades."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.activity_event import ActivityEvent


class IActivityRepository(ABC):
    @abstractmethod
    async def add(self, event: ActivityEvent) -> None: ...

    @abstractmethod
    async def recent(self, limit: int) -> list[ActivityEvent]: ...
