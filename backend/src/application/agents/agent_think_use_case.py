"""Caso de uso: fazer um agente pensar sobre um contexto e agir em consequência.

Liga o `ILlmAdapter` ao `IMessageBus`: publica o status de pensamento, o
pensamento em si e a ação decidida pelo agente, nos tópicos definidos na
RFC-001. Quando a ação envolve uma ferramenta (``tool_call``), delega sua
execução ao ``ToolRegistry``, que valida a permissão do papel antes de
executá-la — este caso de uso nunca decide "quem pode fazer o quê" por conta
própria (ver RFC-003 e Fase 3 do plano de migração).
"""

from __future__ import annotations

from src.application.common.agent_status_publisher import publish_agent_status
from src.application.common.message_envelope import build_message_envelope
from src.application.tools.tool_permissions import ToolName
from src.application.tools.tool_registry import ToolRegistry
from src.domain.entities.agent import Agent
from src.domain.interfaces.llm_adapter import LlmThoughtResponse
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.interfaces.prompt_provider import IPromptProvider
from src.domain.localization.language import Language

# Bloco: templates de tópico por tipo de evento, conforme a RFC-001.
_THOUGHT_TOPIC_TEMPLATE = "office/agents/{agent_id}/thought"
_ACTION_TOPIC_TEMPLATE = "office/agents/{agent_id}/action"


# Bloco: caso de uso de pensamento do agente.
# Depende apenas das portas de domínio (LLM, barramento, prompt) e do registro
# de ferramentas da camada de aplicação — nunca de implementações concretas de
# infraestrutura (Dependency Inversion Principle).
class AgentThinkUseCase:
    def __init__(
        self,
        llm_adapter_resolver: ILlmAdapterResolver,
        message_bus: IMessageBus,
        prompt_provider: IPromptProvider,
        tool_registry: ToolRegistry,
        language: Language,
    ) -> None:
        self._llm_adapter_resolver = llm_adapter_resolver
        self._message_bus = message_bus
        self._prompt_provider = prompt_provider
        self._tool_registry = tool_registry
        self._language = language

    async def execute(self, agent: Agent, context: str) -> LlmThoughtResponse:
        """Move o agente para `THINKING`, consulta o LLM e publica pensamento/ação."""
        agent.start_thinking()
        await publish_agent_status(self._message_bus, agent)

        system_prompt = self._prompt_provider.get_system_prompt(
            agent.role, agent.name, self._language
        )
        llm_adapter = self._llm_adapter_resolver.resolve(agent.role)
        response = await llm_adapter.think(system_prompt=system_prompt, context=context)

        await self._publish_thought(agent, response)
        await self._publish_action(agent, response)

        if response.tool_call is not None:
            await self._execute_tool_call(agent, response)

        return response

    async def _publish_thought(self, agent: Agent, response: LlmThoughtResponse) -> None:
        envelope = build_message_envelope(
            agent_id=str(agent.agent_id),
            agent_role=agent.role.value,
            payload={"thought": response.thought},
        )
        topic = _THOUGHT_TOPIC_TEMPLATE.format(agent_id=agent.agent_id)
        # QoS 0 — pensamentos internos podem ser perdidos sem comprometer a
        # correção do sistema (ver RFC-001).
        await self._message_bus.publish(topic, envelope, qos=0)

    async def _publish_action(self, agent: Agent, response: LlmThoughtResponse) -> None:
        envelope = build_message_envelope(
            agent_id=str(agent.agent_id),
            agent_role=agent.role.value,
            payload={
                "action": response.action,
                "target": response.target,
                "tool_call": response.tool_call,
            },
        )
        topic = _ACTION_TOPIC_TEMPLATE.format(agent_id=agent.agent_id)
        await self._message_bus.publish(topic, envelope, qos=1)

    async def _execute_tool_call(self, agent: Agent, response: LlmThoughtResponse) -> None:
        """Delega a execução da ferramenta solicitada ao ``ToolRegistry``."""
        tool_call = response.tool_call
        assert tool_call is not None  # já verificado pelo chamador

        tool_name = ToolName(str(tool_call["tool"]))
        raw_arguments = tool_call.get("args", {})
        arguments = raw_arguments if isinstance(raw_arguments, dict) else {}

        await self._tool_registry.execute(
            tool_name=tool_name,
            requester_id=agent.agent_id,
            requester_role=agent.role,
            arguments=arguments,
        )
