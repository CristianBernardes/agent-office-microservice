"""Testes unitários do ``InMemoryMessageBus``."""

from __future__ import annotations

import pytest

from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus

pytestmark = pytest.mark.unit


class TestInMemoryMessageBus:
    async def test_subscriber_receives_published_message(self) -> None:
        bus = InMemoryMessageBus()
        await bus.connect()
        received_payloads: list[dict[str, object]] = []

        async def handler(topic: str, payload: dict[str, object]) -> None:
            received_payloads.append(payload)

        await bus.subscribe("office/agents/alice/message", handler)
        await bus.publish("office/agents/alice/message", {"text": "olá"})

        assert received_payloads == [{"text": "olá"}]

    async def test_subscriber_on_different_topic_does_not_receive_message(self) -> None:
        bus = InMemoryMessageBus()
        await bus.connect()
        received_payloads: list[dict[str, object]] = []

        async def handler(topic: str, payload: dict[str, object]) -> None:
            received_payloads.append(payload)

        await bus.subscribe("office/agents/alice/message", handler)
        await bus.publish("office/agents/bob/message", {"text": "olá"})

        assert received_payloads == []

    async def test_get_published_messages_returns_only_matching_topic(self) -> None:
        bus = InMemoryMessageBus()
        await bus.connect()

        await bus.publish("office/tasks/created", {"title": "Tarefa 1"})
        await bus.publish("office/tasks/completed", {"title": "Tarefa 1"})

        created_messages = bus.get_published_messages("office/tasks/created")
        assert created_messages == [{"title": "Tarefa 1"}]
