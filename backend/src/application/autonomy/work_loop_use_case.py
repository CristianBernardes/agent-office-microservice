"""Caso de uso: ciclo de trabalho autônomo que move as tarefas do Kanban (ADR-048)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable
from uuid import NAMESPACE_URL, uuid5

from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.application.chat.chat_use_cases import SendMessageInput, SendMessageUseCase
from src.application.common.agent_status_publisher import publish_agent_status
from src.application.tasks.task_use_cases import AssignTaskUseCase, MoveTaskUseCase
from src.domain.entities.agent import Agent, AgentStatus, Role
from src.domain.entities.artifact import ArtifactType
from src.domain.entities.task import Task, TaskStatus
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import SessionId

logger = logging.getLogger(__name__)

_PLANNERS = (Role.PRODUCT_OWNER, Role.SCRUM_MASTER)
_COORDINATORS = (Role.SCRUM_MASTER, Role.TECH_LEAD, Role.PRODUCT_OWNER)
_WORKERS = (Role.DEV_SENIOR, Role.DEV_JUNIOR, Role.TECH_LEAD)
_REVIEWERS = (Role.QA_ENGINEER, Role.TECH_LEAD)

# Bloco: sessão fixa do "chão do escritório", onde o ciclo registra as falas.
_FLOOR_SESSION = SessionId(value=uuid5(NAMESPACE_URL, "agent-office/floor"))

_PROMPTS = {
    Language.PT: {
        "work": "Você está trabalhando na tarefa «{title}».\nDetalhes: {description}\n"
        "Escreva o resultado do seu trabalho em poucas linhas (um rascunho em markdown).",
        "review": "Revise o trabalho entregue na tarefa «{title}».\nResultado: {result}\n"
        "Dê seu parecer curto e diga se aprova.",
    },
    Language.EN: {
        "work": "You are working on the task «{title}».\nDetails: {description}\n"
        "Write the outcome of your work in a few lines (a markdown draft).",
        "review": "Review the work delivered on the task «{title}».\nResult: {result}\n"
        "Give a short opinion and say whether you approve.",
    },
}


class WorkLoopUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        task_repository: ITaskRepository,
        assign_task: AssignTaskUseCase,
        move_task: MoveTaskUseCase,
        dispatch_goal: DispatchGoalUseCase,
        send_message: SendMessageUseCase,
        write_artifact: WriteArtifactUseCase,
        message_bus: IMessageBus,
        language: Language,
    ) -> None:
        self._agents = agent_repository
        self._tasks = task_repository
        self._assign = assign_task
        self._move = move_task
        self._dispatch = dispatch_goal
        self._send = send_message
        self._write = write_artifact
        self._bus = message_bus
        self._language = language

    async def tick(self) -> int:
        """Executa um passo por estágio; devolve quantas tarefas avançaram."""
        moved = 0
        for step in (self._review, self._work, self._assign_todo, self._plan):
            try:
                moved += await step()
            except Exception:
                logger.exception("Falha em um passo do ciclo de trabalho")
        return moved

    async def _tasks_in(self, status: TaskStatus) -> list[Task]:
        return [t for t in await self._tasks.list_all() if t.status == status]

    async def _first(self, roles: tuple[Role, ...], *, idle: bool = False) -> Agent | None:
        for role in roles:
            for agent in await self._agents.list_all():
                if agent.role == role and (not idle or agent.status == AgentStatus.IDLE):
                    return agent
        return None

    async def _plan(self) -> int:
        planner = await self._first(_PLANNERS)
        if planner is None:
            return 0
        backlog = await self._tasks_in(TaskStatus.BACKLOG)
        for task in backlog:
            await self._move.execute(task.task_id, TaskStatus.TODO, planner.agent_id, planner.role)
        return len(backlog)

    async def _assign_todo(self) -> int:
        coordinator = await self._first(_COORDINATORS)
        if coordinator is None:
            return 0
        moved = 0
        for task in await self._tasks_in(TaskStatus.TODO):
            worker = await self._first(_WORKERS, idle=True)
            if worker is None:
                break
            await self._assign.execute(
                task.task_id, worker.agent_id, coordinator.agent_id, coordinator.role
            )
            await self._announce(worker.agent_id)
            moved += 1
        return moved

    async def _work(self) -> int:
        for task in await self._tasks_in(TaskStatus.IN_PROGRESS):
            worker = await self._assignee(task)
            if worker is None or worker.role not in _WORKERS:
                continue
            prompt = _PROMPTS[self._language]["work"].format(
                title=task.title, description=task.description
            )
            result = (await self._dispatch.execute(worker.agent_id, prompt, self._language)).thought
            await self._send.execute(
                SendMessageInput(
                    session_id=_FLOOR_SESSION,
                    content=result,
                    sender_id=worker.agent_id,
                    task_id=task.task_id,
                )
            )
            await self._write.execute(
                WriteArtifactInput(
                    title=task.title,
                    content=f"# {task.title}\n\n{result}\n",
                    artifact_type=ArtifactType.IMPLEMENTATION,
                    path=f"tasks/{task.task_id.value}.md",
                    author_id=worker.agent_id,
                    author_role=worker.role,
                )
            )
            task.result = result
            await self._tasks.save(task)
            await self._move.execute(
                task.task_id, TaskStatus.IN_REVIEW, worker.agent_id, worker.role
            )
            return 1
        return 0

    async def _review(self) -> int:
        for task in await self._tasks_in(TaskStatus.IN_REVIEW):
            reviewer = await self._first_reviewer(task)
            if reviewer is None:
                continue
            prompt = _PROMPTS[self._language]["review"].format(
                title=task.title, result=task.result or ""
            )
            opinion = (
                await self._dispatch.execute(reviewer.agent_id, prompt, self._language)
            ).thought
            await self._send.execute(
                SendMessageInput(
                    session_id=_FLOOR_SESSION,
                    content=opinion,
                    sender_id=reviewer.agent_id,
                    task_id=task.task_id,
                )
            )
            await self._move.execute(
                task.task_id, TaskStatus.DONE, reviewer.agent_id, reviewer.role, note=opinion[:200]
            )
            await self._release(task)
            return 1
        return 0

    async def _first_reviewer(self, task: Task) -> Agent | None:
        for role in _REVIEWERS:
            for agent in await self._agents.list_all():
                if (
                    agent.role == role
                    and agent.status == AgentStatus.IDLE
                    and agent.agent_id != task.assigned_to
                ):
                    return agent
        return None

    async def _assignee(self, task: Task) -> Agent | None:
        if task.assigned_to is None:
            return None
        return await self._agents.find_by_id(task.assigned_to)

    async def _release(self, task: Task) -> None:
        worker = await self._assignee(task)
        if worker is not None and worker.current_task_id == task.task_id:
            worker.complete_task()
            await self._agents.save(worker)
            await publish_agent_status(self._bus, worker)

    async def _announce(self, agent_id: object) -> None:
        agent = await self._agents.find_by_id(agent_id)  # type: ignore[arg-type]
        if agent is not None:
            await publish_agent_status(self._bus, agent)


# Bloco: laço de fundo; devolve a task para o lifespan cancelar no desligamento.
def start_work_loop(
    factory: Callable[[], WorkLoopUseCase], interval_seconds: float
) -> asyncio.Task[None]:
    async def run() -> None:
        while True:
            await asyncio.sleep(interval_seconds)
            try:
                await factory().tick()
            except Exception:
                logger.exception("Falha no ciclo de trabalho")

    return asyncio.create_task(run())


async def stop_work_loop(task: asyncio.Task[None]) -> None:
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task
