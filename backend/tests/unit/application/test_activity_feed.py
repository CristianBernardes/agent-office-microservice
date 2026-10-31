"""Testes unitários do feed de atividades."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.application.activity.activity_feed import (
    FEED_TOPICS,
    ListActivityUseCase,
    register_activity_feed,
)
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_activity_repository import (
    InMemoryActivityRepository,
)
from src.presentation.dependencies import get_activity_repository
from src.presentation.main import app

pytestmark = pytest.mark.unit


class _Boom(InMemoryActivityRepository):
    async def add(self, event):  # type: ignore[no-untyped-def]
        raise RuntimeError("db down")


class TestActivityFeed:
    async def test_records_every_feed_topic(self) -> None:
        bus, repo = InMemoryMessageBus(), InMemoryActivityRepository()
        await register_activity_feed(bus, lambda: repo)()
        agent = uuid4()

        for topic in FEED_TOPICS:
            await bus.publish(topic, {"payload": {"agent_id": str(agent), "n": 1}})

        events = await ListActivityUseCase(repo).execute(limit=3)
        assert len(await ListActivityUseCase(repo).execute(limit=50)) == len(FEED_TOPICS)
        assert len(events) == 3
        assert events[0].agent_id == agent

    async def test_invalid_payload_and_failure_are_tolerated(self) -> None:
        bus = InMemoryMessageBus()
        await register_activity_feed(bus, _Boom)()
        await bus.publish("office/chat/message", {"payload": "x"})

        repo = InMemoryActivityRepository()
        bus2 = InMemoryMessageBus()
        await register_activity_feed(bus2, lambda: repo)()
        await bus2.publish("office/chat/message", {"payload": "x"})
        [event] = await repo.recent(5)
        assert event.payload == {} and event.agent_id is None


class TestActivityRoute:
    async def test_lists_recent_first(self) -> None:
        get_activity_repository.cache_clear()
        repo = get_activity_repository()
        bus = InMemoryMessageBus()
        await register_activity_feed(bus, lambda: repo)()
        await bus.publish("office/goals/created", {"payload": {"text": "a"}})
        await bus.publish("office/tasks/updated", {"payload": {"text": "b"}})

        client = TestClient(app)
        body = client.get("/activity?limit=1").json()

        assert [e["kind"] for e in body] == ["office/tasks/updated"]
        assert client.get("/activity?limit=0").status_code == 422
