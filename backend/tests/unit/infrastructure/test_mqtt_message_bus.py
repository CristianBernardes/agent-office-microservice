"""Testes unitários do MqttMessageBus (sem broker real)."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from src.infrastructure.config.settings import Settings
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.messaging.mqtt_message_bus import MqttMessageBus
from src.infrastructure.messaging.topic_matching import topic_matches
from src.presentation import dependencies

pytestmark = pytest.mark.unit


class _FakeClient:
    def __init__(self, messages: list[Any]) -> None:
        self.published: list[tuple[str, str]] = []
        self.messages = self._gen(messages)

    @staticmethod
    async def _gen(messages: list[Any]) -> Any:
        for message in messages:
            yield message

    async def publish(self, topic: str, payload: str, qos: int, retain: bool) -> None:
        self.published.append((topic, payload))


@pytest.mark.parametrize(
    ("pattern", "topic", "expected"),
    [
        ("office/#", "office/tasks/updated", True),
        ("office/agents/+/status", "office/agents/1/status", True),
        ("office/agents/+/status", "office/agents/1/thought", False),
        ("office/tasks", "office/tasks/updated", False),
        ("office/tasks/updated", "office/tasks", False),
        ("a/b", "a/b", True),
    ],
)
def test_topic_matches(pattern: str, topic: str, expected: bool) -> None:
    assert topic_matches(pattern, topic) is expected


class TestMqttBus:
    async def test_publish_requires_connection(self) -> None:
        bus = MqttMessageBus("h", 1)
        with pytest.raises(RuntimeError):
            await bus.publish("t", {})
        with pytest.raises(RuntimeError):
            await bus.subscribe("t", lambda *_: None)  # type: ignore[arg-type,return-value]

    async def test_wildcard_dispatch_and_invalid_json_dropped(self) -> None:
        bus = MqttMessageBus("h", 1)
        received: list[tuple[str, dict[str, object]]] = []

        async def handler(topic: str, payload: dict[str, object]) -> None:
            received.append((topic, payload))

        bus._handlers_by_topic["office/#"] = [handler]
        bus._client = _FakeClient(  # type: ignore[assignment]
            [
                SimpleNamespace(topic="office/x/y", payload=b"not-json"),
                SimpleNamespace(topic="office/x/y", payload=json.dumps({"a": 1}).encode()),
                SimpleNamespace(topic="other/x", payload=b"{}"),
            ]
        )
        await bus._listen_for_messages()
        assert received == [("office/x/y", {"a": 1})]

    async def test_publish_serializes_json(self) -> None:
        bus = MqttMessageBus("h", 1)
        client = _FakeClient([])
        bus._client = client  # type: ignore[assignment]
        await bus.publish("office/a", {"k": 1})
        assert client.published == [("office/a", '{"k": 1}')]


class TestBusSelection:
    def test_backend_selection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dependencies.get_message_bus.cache_clear()
        monkeypatch.setattr(
            dependencies, "get_settings", lambda: Settings(message_bus_backend="mqtt")
        )
        assert isinstance(dependencies.get_message_bus(), MqttMessageBus)
        dependencies.get_message_bus.cache_clear()
        monkeypatch.setattr(dependencies, "get_settings", lambda: Settings())
        assert isinstance(dependencies.get_message_bus(), InMemoryMessageBus)
        dependencies.get_message_bus.cache_clear()
