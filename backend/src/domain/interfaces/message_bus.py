"""Contrato (porta) para o barramento de mensagens assíncrono.

Qualquer implementação (MQTT real, barramento em memória para testes) deve
satisfazer esta interface, permitindo que a camada de aplicação publique e assine
eventos sem conhecer o transporte concreto (ver ADR-001, ADR-007 e RFC-001).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

# Bloco: assinatura do handler de mensagens recebidas.
# Recebe o tópico em que a mensagem chegou e o payload já desserializado.
MessageHandler = Callable[[str, dict[str, object]], Awaitable[None]]


# Bloco: contrato único para qualquer barramento de mensagens.
class IMessageBus(ABC):
    @abstractmethod
    async def connect(self) -> None:
        """Estabelece a conexão com o barramento de mensagens."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Encerra a conexão com o barramento de mensagens."""

    @abstractmethod
    async def publish(
        self,
        topic: str,
        payload: dict[str, object],
        qos: int = 1,
        retain: bool = False,
    ) -> None:
        """Publica uma mensagem em um tópico, com nível de QoS e retenção."""

    @abstractmethod
    async def subscribe(self, topic: str, handler: MessageHandler) -> None:
        """Assina um tópico e registra um handler assíncrono para suas mensagens."""
