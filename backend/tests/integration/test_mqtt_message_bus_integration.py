"""Teste de integração do ``MqttMessageBus`` contra um broker Mosquitto real.

Requer o serviço `mosquitto` do `docker-compose.yml` em execução
(`make up` neste repositório). Marcado com `@pytest.mark.integration` para que
não seja executado por padrão em ambientes sem o broker disponível — ver
`make test-unit` versus `make test-integration` no Makefile.
"""

from __future__ import annotations

import asyncio

import pytest

from src.infrastructure.messaging.mqtt_message_bus import MqttMessageBus

pytestmark = pytest.mark.integration

# Bloco: tempo de espera para a entrega assíncrona de mensagens via MQTT.
_MESSAGE_DELIVERY_WAIT_SECONDS = 0.5


class TestMqttMessageBusIntegration:
    async def test_subscriber_receives_message_published_by_another_connection(self) -> None:
        publisher_bus = MqttMessageBus(hostname="localhost", port=7083)
        subscriber_bus = MqttMessageBus(hostname="localhost", port=7083)

        await publisher_bus.connect()
        await subscriber_bus.connect()

        received_payloads: list[dict[str, object]] = []

        async def handler(topic: str, payload: dict[str, object]) -> None:
            received_payloads.append(payload)

        await subscriber_bus.subscribe("office/agents/alice/message", handler)
        await asyncio.sleep(_MESSAGE_DELIVERY_WAIT_SECONDS)

        await publisher_bus.publish(
            "office/agents/alice/message",
            {"text": "mensagem de teste de integração"},
            qos=1,
        )
        await asyncio.sleep(_MESSAGE_DELIVERY_WAIT_SECONDS)

        assert received_payloads == [{"text": "mensagem de teste de integração"}]

        await publisher_bus.disconnect()
        await subscriber_bus.disconnect()
