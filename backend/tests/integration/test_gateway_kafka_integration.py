"""Integração MQTT → gateway Go → Kafka (ADR-024).

Requer `docker compose up -d mosquitto redis kafka kafka-init gateway`.
Pula sozinho se o Kafka não estiver no ar.
"""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest

from src.infrastructure.messaging.mqtt_message_bus import MqttMessageBus

pytestmark = pytest.mark.integration

_ROOT = Path(__file__).resolve().parents[3]
_DELIVERY_WAIT_SECONDS = 3


def _consume(topic: str) -> str:
    result = subprocess.run(
        [
            "docker", "compose", "exec", "-T", "kafka",
            "/opt/kafka/bin/kafka-console-consumer.sh",
            "--bootstrap-server", "kafka:9092", "--topic", topic,
            "--from-beginning", "--timeout-ms", "5000",
        ],
        cwd=_ROOT, capture_output=True, text=True, check=False,
    )  # fmt: skip
    return result.stdout


def _kafka_up() -> bool:
    ps = subprocess.run(
        ["docker", "compose", "ps", "--status", "running", "--services"],
        cwd=_ROOT, capture_output=True, text=True, check=False,
    )  # fmt: skip
    return "kafka" in ps.stdout.split() and "gateway" in ps.stdout.split()


@pytest.fixture(autouse=True)
def _require_stack() -> None:
    if not _kafka_up():
        pytest.skip("kafka/gateway não estão em execução")


async def _publish(payload: dict[str, object]) -> None:
    bus = MqttMessageBus(hostname="localhost", port=7083)
    await bus.connect()
    await bus.publish(f"office/test/{uuid4().hex}", payload)
    await asyncio.sleep(_DELIVERY_WAIT_SECONDS)
    await bus.disconnect()


class TestGatewayKafka:
    async def test_valid_envelope_reaches_office_events(self) -> None:
        event_id = uuid4().hex
        await _publish(
            {
                "event_id": event_id,
                "timestamp": "2026-01-01T00:00:00Z",
                "version": "1",
                "agent_id": "a1",
                "agent_role": "dev",
                "payload": {"x": 1},
            }
        )

        assert event_id in await asyncio.to_thread(_consume, "office.events")

    async def test_invalid_envelope_goes_to_dlq(self) -> None:
        marker = uuid4().hex
        await _publish({"marker": marker})

        assert marker in await asyncio.to_thread(_consume, "office.events.dlq")
