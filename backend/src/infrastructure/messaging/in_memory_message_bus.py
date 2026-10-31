"""Implementação em memória do ``IMessageBus``.

Usada em testes unitários e como barramento padrão ao executar o backend sem um
broker MQTT configurado. Simplesmente invoca, de forma síncrona dentro do mesmo
processo, os handlers registrados para o tópico publicado — sem qualquer rede
envolvida.
"""

from __future__ import annotations

from src.domain.interfaces.message_bus import IMessageBus, MessageHandler
from src.infrastructure.messaging.topic_matching import topic_matches


# Bloco: barramento de mensagens em memória.
# Mantém handlers por padrão de tópico, com os mesmos curingas MQTT (`+`, `#`) do
# `MqttMessageBus`, via `topic_matches` compartilhado (ADR-039).
class InMemoryMessageBus(IMessageBus):
    def __init__(self) -> None:
        self._handlers_by_topic: dict[str, list[MessageHandler]] = {}
        self._published_messages: list[tuple[str, dict[str, object]]] = []
        self._is_connected = False

    async def connect(self) -> None:
        """Marca o barramento como conectado (não há rede real a estabelecer)."""
        self._is_connected = True

    async def disconnect(self) -> None:
        """Marca o barramento como desconectado."""
        self._is_connected = False

    async def publish(
        self,
        topic: str,
        payload: dict[str, object],
        qos: int = 1,
        retain: bool = False,
    ) -> None:
        """Registra a mensagem publicada e notifica os handlers assinantes do tópico."""
        self._published_messages.append((topic, payload))
        for pattern, handlers in list(self._handlers_by_topic.items()):
            if topic_matches(pattern, topic):
                for handler in handlers:
                    await handler(topic, payload)

    async def subscribe(self, topic: str, handler: MessageHandler) -> None:
        """Registra um handler para um tópico ou padrão com curingas."""
        self._handlers_by_topic.setdefault(topic, []).append(handler)

    def get_published_messages(self, topic: str) -> list[dict[str, object]]:
        """Retorna os payloads publicados em um tópico — utilitário para testes."""
        return [
            payload
            for published_topic, payload in self._published_messages
            if published_topic == topic
        ]
