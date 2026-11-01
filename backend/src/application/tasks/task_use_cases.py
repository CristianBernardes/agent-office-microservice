"""Casos de uso de tarefas: criar, atribuir e concluir (ver ADR-016)."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.common.message_envelope import build_message_envelope
from src.application.tasks.task_errors import TaskNotFoundError
from src.domain.entities.agent import AgentStatus, Role
from src.domain.entities.task import Priority, Task, TaskStatus, TaskTransition
from src.domain.exceptions.domain_exceptions import (
    InvalidStateTransitionError,
    PermissionDeniedError,
)
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.policies.task_workflow import can_assign, can_complete, can_move, is_valid_move
from src.domain.services.task_routing import select_owner
from src.domain.value_objects.identifiers import AgentId, GoalId, TaskId

# Bloco: tópico de notificação de atualização de tarefa, conforme a RFC-001.
_TASK_UPDATED_TOPIC = "office/tasks/updated"


# Bloco: publicação compartilhada do evento de tarefa atualizada (DRY).
async def _publish_task_updated(
    message_bus: IMessageBus, task: Task, actor_id: AgentId, actor_role: Role
) -> None:
    envelope = build_message_envelope(
        agent_id=str(actor_id),
        agent_role=actor_role.value,
        payload={
            "task_id": str(task.task_id),
            "title": task.title,
            "status": task.status.value,
            "assigned_to": str(task.assigned_to) if task.assigned_to else None,
        },
    )
    await message_bus.publish(_TASK_UPDATED_TOPIC, envelope, qos=1)


# Bloco: registro do histórico de movimentos (DRY entre todos os casos de uso).
async def _record_transition(
    repository: ITaskRepository,
    task: Task,
    from_status: TaskStatus | None,
    actor_id: AgentId,
    actor_role: Role,
    note: str = "",
) -> None:
    await repository.add_transition(
        TaskTransition(task.task_id, from_status, task.status, actor_id, actor_role, note)
    )


# Bloco: entrada de criação de tarefa.
@dataclass(frozen=True, slots=True)
class CreateTaskInput:
    title: str
    description: str
    priority: Priority
    creator_id: AgentId
    creator_role: Role
    goal_id: GoalId | None = None


# Bloco: caso de uso de criação de tarefa (nasce no backlog).
class CreateTaskUseCase:
    def __init__(self, task_repository: ITaskRepository, message_bus: IMessageBus) -> None:
        self._task_repository = task_repository
        self._message_bus = message_bus

    async def execute(self, data: CreateTaskInput) -> Task:
        task = Task(
            task_id=TaskId.generate(),
            title=data.title,
            description=data.description,
            priority=data.priority,
            goal_id=data.goal_id,
        )
        await self._task_repository.save(task)
        await _record_transition(
            self._task_repository, task, None, data.creator_id, data.creator_role
        )
        await _publish_task_updated(self._message_bus, task, data.creator_id, data.creator_role)
        return task


# Bloco: caso de uso de atribuição de tarefa a um agente.
class AssignTaskUseCase:
    def __init__(
        self,
        task_repository: ITaskRepository,
        agent_repository: IAgentRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._task_repository = task_repository
        self._agent_repository = agent_repository
        self._message_bus = message_bus

    async def execute(
        self, task_id: TaskId, assignee_id: AgentId, actor_id: AgentId, actor_role: Role
    ) -> Task:
        if not can_assign(actor_role):
            raise PermissionDeniedError("task.assign_forbidden", role=actor_role.value)
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)
        agent = await self._agent_repository.find_by_id(assignee_id)
        if agent is None:
            raise AgentNotFoundError("agent.not_found", agent_id=assignee_id)

        # Valida o agente primeiro: se ele estiver ocupado, a tarefa não muda.
        previous = task.status
        agent.assign_task(task.task_id)
        task.assign(assignee_id)
        await self._agent_repository.save(agent)
        await self._task_repository.save(task)
        await _record_transition(
            self._task_repository, task, previous, actor_id, actor_role, f"assigned:{assignee_id}"
        )
        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task


# Bloco: caso de uso de conclusão de tarefa; devolve o agente a IDLE.
class CompleteTaskUseCase:
    def __init__(
        self,
        task_repository: ITaskRepository,
        agent_repository: IAgentRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._task_repository = task_repository
        self._agent_repository = agent_repository
        self._message_bus = message_bus

    async def execute(
        self, task_id: TaskId, result: str, actor_id: AgentId, actor_role: Role
    ) -> Task:
        if not can_complete(actor_role):
            raise PermissionDeniedError("task.complete_forbidden", role=actor_role.value)
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)

        previous = task.status
        task.complete(result)
        await self._task_repository.save(task)
        await _record_transition(self._task_repository, task, previous, actor_id, actor_role)

        if task.assigned_to is not None:
            agent = await self._agent_repository.find_by_id(task.assigned_to)
            if agent is not None and agent.current_task_id == task.task_id:
                agent.complete_task()
                await self._agent_repository.save(agent)

        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task


# Bloco: soma de tarefas abertas por responsável (base do balanceamento de carga).
async def open_load(task_repository: ITaskRepository) -> dict[AgentId, int]:
    load: dict[AgentId, int] = {}
    for other in await task_repository.list_all():
        if other.assigned_to is not None and other.status != TaskStatus.DONE:
            load[other.assigned_to] = load.get(other.assigned_to, 0) + 1
    return load


# Bloco: caso de uso de movimento de cartão, regido pela matriz papel × estágio.
# ``owner_override`` é o poder do dono do produto (usuário): ignora a matriz e move para qualquer
# estágio (ADR-054).
_RELEASING_STAGES = (TaskStatus.BACKLOG, TaskStatus.TODO, TaskStatus.DONE, TaskStatus.BLOCKED)


class MoveTaskUseCase:
    def __init__(
        self,
        task_repository: ITaskRepository,
        message_bus: IMessageBus,
        agent_repository: IAgentRepository,
    ) -> None:
        self._task_repository = task_repository
        self._message_bus = message_bus
        self._agent_repository = agent_repository

    # Bloco: fora do backlog toda tarefa tem responsável — o profissional da área da tarefa
    # (RH para contratar, Analista de Dados para dados...) e, sem área, o menos carregado.
    async def _ensure_owner(self, task: Task) -> None:
        if task.assigned_to is not None:
            owner = await self._agent_repository.find_by_id(task.assigned_to)
            if owner is not None and owner.status != AgentStatus.OFFLINE:
                return
        owner = select_owner(
            task, await self._agent_repository.list_all(), await open_load(self._task_repository)
        )
        if owner is None:
            raise InvalidStateTransitionError("task.no_owner_available", title=task.title)
        task.assigned_to = owner.agent_id

    # Bloco: ao sair de "em andamento" para um estágio sem execução, o responsável é liberado.
    async def _release_owner(self, task: Task) -> None:
        if task.assigned_to is None:
            return
        agent = await self._agent_repository.find_by_id(task.assigned_to)
        if agent is not None and agent.current_task_id == task.task_id:
            agent.complete_task()
            await self._agent_repository.save(agent)

    async def execute(
        self,
        task_id: TaskId,
        target: TaskStatus,
        actor_id: AgentId,
        actor_role: Role,
        note: str = "",
        owner_override: bool = False,
    ) -> Task:
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)
        previous = task.status
        if not owner_override:
            params = {
                "title": task.title,
                "from_status": previous.value,
                "to_status": target.value,
            }
            if not is_valid_move(previous, target):
                raise InvalidStateTransitionError("task.invalid_move", **params)
            if not can_move(actor_role, previous, target):
                raise PermissionDeniedError("task.move_forbidden", role=actor_role.value, **params)

        if target != TaskStatus.BACKLOG:
            await self._ensure_owner(task)
        task.move_to(target)
        if owner_override and target in _RELEASING_STAGES:
            await self._release_owner(task)
        await self._task_repository.save(task)
        await _record_transition(
            self._task_repository,
            task,
            previous,
            actor_id,
            actor_role,
            note or ("owner_override" if owner_override else ""),
        )
        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task


# Bloco: o dono do produto define o responsável sem mudar o estágio (ADR-054).
class SetTaskOwnerUseCase:
    def __init__(
        self,
        task_repository: ITaskRepository,
        agent_repository: IAgentRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._task_repository = task_repository
        self._agent_repository = agent_repository
        self._message_bus = message_bus

    async def execute(
        self, task_id: TaskId, owner_id: AgentId, actor_id: AgentId, actor_role: Role
    ) -> Task:
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)
        owner = await self._agent_repository.find_by_id(owner_id)
        if owner is None:
            raise AgentNotFoundError("agent.not_found", agent_id=owner_id)
        if owner.status == AgentStatus.OFFLINE:
            raise InvalidStateTransitionError("agent.offline_cannot_own", name=owner.name)
        previous = task.status
        task.assigned_to = owner_id
        await self._task_repository.save(task)
        await _record_transition(
            self._task_repository, task, previous, actor_id, actor_role, f"owner:{owner_id}"
        )
        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task


# Bloco: o dono do produto redefine a prioridade de uma tarefa (ADR-054).
class SetTaskPriorityUseCase:
    def __init__(self, task_repository: ITaskRepository, message_bus: IMessageBus) -> None:
        self._task_repository = task_repository
        self._message_bus = message_bus

    async def execute(
        self, task_id: TaskId, priority: Priority, actor_id: AgentId, actor_role: Role
    ) -> Task:
        task = await self._task_repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError("task.not_found", task_id=task_id)
        task.priority = priority
        await self._task_repository.save(task)
        await _record_transition(
            self._task_repository,
            task,
            task.status,
            actor_id,
            actor_role,
            f"priority:{priority.value}",
        )
        await _publish_task_updated(self._message_bus, task, actor_id, actor_role)
        return task
