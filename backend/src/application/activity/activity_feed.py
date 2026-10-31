"""Feed de atividades: grava eventos de domínio publicados no barramento (ADR-031)."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from uuid import UUID

from src.domain.entities.activity_event import ActivityEvent
from src.domain.interfaces.activity_repository import IActivityRepository
from src.domain.interfaces.message_bus import IMessageBus

logger = logging.getLogger(__name__)

FEED_TOPICS = (
    "office/goals/created",
    "office/tasks/updated",
    "office/artifacts/created",
    "office/artifacts/updated",
    "office/chat/message",
    "office/agents/+/thought",
    "office/agents/+/action",
)


class ListActivityUseCase:
    def __init__(self, repository: IActivityRepository) -> None:
        self._repository = repository

    async def execute(self, limit: int = 50) -> list[ActivityEvent]:
        return await self._repository.recent(limit)


def _agent_id(payload: dict[str, object]) -> UUID | None:
    for key in ("agent_id", "sender_id"):
        try:
            return UUID(str(payload[key]))
        except (KeyError, ValueError):
            continue
    return None


def register_activity_feed(
    bus: IMessageBus, repository_factory: Callable[[], IActivityRepository]
) -> Callable[[], Awaitable[None]]:
    async def handler(topic: str, envelope: dict[str, object]) -> None:
        raw = envelope.get("payload")
        payload = raw if isinstance(raw, dict) else {}
        try:
            await repository_factory().add(
                ActivityEvent(kind=topic, payload=payload, agent_id=_agent_id(payload))
            )
        except Exception:
            logger.exception("Falha ao gravar evento de atividade %s", topic)

    async def register() -> None:
        for topic in FEED_TOPICS:
            await bus.subscribe(topic, handler)

    return register
