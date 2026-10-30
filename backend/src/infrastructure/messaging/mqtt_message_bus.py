"""Implementação real do ``IMessageBus`` usando MQTT (broker Mosquitto, via ``aiomqtt``).

Esta é a implementação de produção do barramento de mensagens, conforme decidido
em ADR-001. A conexão, publicação e assinatura de tópicos são feitas de forma
assíncrona, nativa ao restante do backend (FastAPI/asyncio).
"""

from __future__ import annotations

import asyncio
import json

import aiomqtt

from src.domain.interfaces.message_bus import IMessageBus, MessageHandler


# Bloco: barramento de mensagens MQTT real.
# A conexão é mantida aberta durante todo o ciclo de vida do serviço (`connect` /
# `disconnect`), e um loop de escuta em segundo plano despacha mensagens
# recebidas para os handlers registrados por tópico.
class MqttMessageBus(IMessageBus):
    def __init__(self, hostname: str, port: int) -> None:
        self._hostname = hostname
        self._port = port
        self._client: aiomqtt.Client | None = None
        self._handlers_by_topic: dict[str, list[MessageHandler]] = {}
        self._listener_task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        """Abre a conexão com o broker MQTT e inicia o loop de escuta em segundo plano."""
        self._client = aiomqtt.Client(hostname=self._hostname, port=self._port)
        await self._client.__aenter__()
        self._listener_task = asyncio.create_task(self._listen_for_messages())

    async def disconnect(self) -> None:
        """Encerra o loop de escuta e a conexão com o broker MQTT."""
        if self._listener_task is not None:
            self._listener_task.cancel()
            self._listener_task = None

        if self._client is not None:
            await self._client.__aexit__(None, None, None)
            self._client = None

    async def publish(
        self,
        topic: str,
        payload: dict[str, object],
        qos: int = 1,
        retain: bool = False,
    ) -> None:
        """Serializa o payload em JSON e publica no tópico informado."""
        if self._client is None:
            raise RuntimeError(
                "MqttMessageBus não está conectado — chame connect() antes de publish()."
            )
        serialized_payload = json.dumps(payload, default=str)
        await self._client.publish(topic, payload=serialized_payload, qos=qos, retain=retain)

    async def subscribe(self, topic: str, handler: MessageHandler) -> None:
        """Registra um handler para o tópico e assina o tópico no broker."""
        if self._client is None:
            raise RuntimeError(
                "MqttMessageBus não está conectado — chame connect() antes de subscribe()."
            )
        self._handlers_by_topic.setdefault(topic, []).append(handler)
        await self._client.subscribe(topic)

    async def _listen_for_messages(self) -> None:
        """Loop de escuta em segundo plano: despacha mensagens MQTT para os handlers."""
        if self._client is None:
            return

        async for message in self._client.messages:
            topic_name = str(message.topic)
            try:
                payload = json.loads(message.payload)
            except (TypeError, ValueError):
                # Payload MQTT recebido não é um JSON válido. O envelope de
                # mensagens definido na RFC-001 exige payload JSON; uma mensagem
                # fora do contrato é descartada de forma explícita (não é um erro
                # silencioso: a decisão de descartar está documentada aqui).
                continue

            for handler in self._handlers_by_topic.get(topic_name, []):
                await handler(topic_name, payload)
