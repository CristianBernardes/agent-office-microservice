"""Publicação do status de um agente no barramento (RFC-001)."""

from __future__ import annotations

from src.application.common.message_envelope import build_message_envelope
from src.domain.entities.agent import Agent
from src.domain.interfaces.message_bus import IMessageBus

_STATUS_TOPIC_TEMPLATE = "office/agents/{agent_id}/status"


# Bloco: status é retido (QoS 1) para que novos assinantes vejam o estado atual.
async def publish_agent_status(message_bus: IMessageBus, agent: Agent) -> None:
    envelope = build_message_envelope(
        agent_id=str(agent.agent_id),
        agent_role=agent.role.value,
        payload={"status": agent.status.value},
    )
    topic = _STATUS_TOPIC_TEMPLATE.format(agent_id=agent.agent_id)
    await message_bus.publish(topic, envelope, qos=1, retain=True)
