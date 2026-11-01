"""Caso de uso: desligar um agente do time ("demitir").

Move o agente para o estado ``OFFLINE``, devolve ao fluxo as tarefas que ele executava e
publica o novo status em tempo real. Mantido focado em uma única responsabilidade (SRP).
"""

from __future__ import annotations

from src.application.common.agent_status_publisher import publish_agent_status
from src.domain.entities.agent import Agent
from src.domain.entities.task import TaskStatus
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.value_objects.identifiers import AgentId


# Bloco: erro específico de aplicação quando o agente buscado não existe.
# Diferenciado de erros de domínio porque representa uma falha de orquestração
# (entrada inválida fornecida ao caso de uso), não uma violação de regra de
# negócio da entidade em si.
class AgentNotFoundError(DomainError):
    """Levantada quando o agente solicitado não é encontrado no repositório."""


# Bloco: caso de uso de desligamento de agente.
class FireAgentUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        task_repository: ITaskRepository | None = None,
        message_bus: IMessageBus | None = None,
    ) -> None:
        self._agent_repository = agent_repository
        self._task_repository = task_repository
        self._message_bus = message_bus

    async def execute(self, agent_id: AgentId) -> Agent:
        """Busca o agente, marca-o como ``OFFLINE``, repassa seu trabalho e persiste."""
        agent = await self._agent_repository.find_by_id(agent_id)
        if agent is None:
            raise AgentNotFoundError("agent.not_found", agent_id=agent_id)

        agent.go_offline()
        await self._agent_repository.save(agent)
        await self._return_work_to_flow(agent_id)
        if self._message_bus is not None:
            await publish_agent_status(self._message_bus, agent)
        return agent

    # Bloco: tarefas "a fazer" ou "em andamento" do demitido voltam sem responsável para
    # "a fazer"; o ciclo de trabalho as repassa a outro profissional da mesma área.
    async def _return_work_to_flow(self, agent_id: AgentId) -> None:
        if self._task_repository is None:
            return
        for task in await self._task_repository.list_all():
            if task.assigned_to != agent_id:
                continue
            if task.status in (TaskStatus.TODO, TaskStatus.IN_PROGRESS):
                task.assigned_to = None
                task.status = TaskStatus.TODO
                await self._task_repository.save(task)
