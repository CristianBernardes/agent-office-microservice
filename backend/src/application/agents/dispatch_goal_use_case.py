"""Caso de uso: despachar um objetivo a um agente e fazê-lo pensar sobre ele."""

from __future__ import annotations

from src.application.agents.agent_think_use_case import AgentThinkUseCase
from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.common.agent_status_publisher import publish_agent_status
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.llm_adapter import LlmThoughtResponse
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.value_objects.identifiers import AgentId


# Bloco: orquestra busca do agente, pensamento e retorno ao estado IDLE.
class DispatchGoalUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        agent_think_use_case: AgentThinkUseCase,
        message_bus: IMessageBus,
    ) -> None:
        self._agent_repository = agent_repository
        self._agent_think_use_case = agent_think_use_case
        self._message_bus = message_bus

    async def execute(self, agent_id: AgentId, goal: str) -> LlmThoughtResponse:
        agent = await self._agent_repository.find_by_id(agent_id)
        if agent is None:
            raise AgentNotFoundError("agent.not_found", agent_id=agent_id)

        try:
            return await self._agent_think_use_case.execute(agent, goal)
        finally:
            # Falhas do LLM não podem deixar o agente preso em THINKING.
            if agent.is_thinking():
                agent.finish_thinking()
            await self._agent_repository.save(agent)
            await publish_agent_status(self._message_bus, agent)
