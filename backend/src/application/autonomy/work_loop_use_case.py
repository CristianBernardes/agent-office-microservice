"""Caso de uso: ciclo de trabalho autônomo que move as tarefas do Kanban (ADR-048)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable
from uuid import NAMESPACE_URL, uuid4, uuid5

from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.application.chat.chat_use_cases import SendMessageInput, SendMessageUseCase
from src.application.common.agent_status_publisher import publish_agent_status
from src.application.tasks.task_use_cases import AssignTaskUseCase, MoveTaskUseCase, open_load
from src.domain.entities.agent import Agent, AgentStatus, Role
from src.domain.entities.artifact import ArtifactType
from src.domain.entities.chat import Session
from src.domain.entities.task import Task, TaskStatus
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.chat_repository import IChatRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.localization.language import Language, OfficeLanguage
from src.domain.services.task_routing import EXECUTOR_ROLES, select_owner
from src.domain.services.task_splitter import (
    distribute_extra_parts,
    parse_subtasks,
    split_task,
)
from src.domain.value_objects.identifiers import SessionId, TaskId

logger = logging.getLogger(__name__)

_PLANNERS = (Role.PRODUCT_OWNER, Role.SCRUM_MASTER)
_COORDINATORS = (Role.SCRUM_MASTER, Role.TECH_LEAD, Role.PRODUCT_OWNER)
_TESTERS = (Role.QA_ENGINEER,)
_REVIEWERS = (Role.TECH_LEAD, Role.QA_ENGINEER)

# Bloco: sessão fixa do "chão do escritório", onde o ciclo registra as falas.
_FLOOR_SESSION = SessionId(value=uuid5(NAMESPACE_URL, "agent-office/floor"))

_PROMPTS = {
    Language.PT: {
        "planning": "Você conduz a cerimônia de planejamento (sprint planning) do time.\n"
        "Tarefas: {tasks}\nTime: {team}\n"
        "A sprint dura no máximo {days} dias fictícios; defina a duração dentro desse limite.\n"
        "Explique em poucas linhas como o trabalho será dividido para que ninguém fique ocioso.",
        "planning_title": "Planejamento da sprint",
        "sprint_length": "Duração máxima da sprint: {days} dias fictícios.",
        "breakdown": "Divida a tarefa «{title}» em {count} subtarefas distintas.\n"
        "Descrição: {description}\n"
        "Responda SOMENTE com {count} linhas no formato: Título curto | O que deve ser entregue.",
        "part": "Parte {index} de {total} da tarefa «{title}».",
        "work": "Você está trabalhando na tarefa «{title}».\nDetalhes: {description}\n"
        "Escreva o resultado do seu trabalho em poucas linhas (um rascunho em markdown).",
        "review": "Revise o trabalho entregue na tarefa «{title}».\nResultado: {result}\n"
        "Dê seu parecer curto e diga se aprova.",
        "test": "Você é o testador da tarefa «{title}».\nResultado entregue: {result}\n"
        "Escreva em poucas linhas o plano de testes e o resultado dos testes (markdown).",
        "test_title": "Testes",
    },
    Language.EN: {
        "planning": "You lead the team's sprint planning ceremony.\n"
        "Tasks: {tasks}\nTeam: {team}\n"
        "The sprint lasts at most {days} fictional days; set its duration within that limit.\n"
        "Explain in a few lines how the work will be split so nobody stays idle.",
        "planning_title": "Sprint planning",
        "sprint_length": "Maximum sprint length: {days} fictional days.",
        "breakdown": "Split the task «{title}» into {count} distinct, non-overlapping subtasks.\n"
        "Description: {description}\n"
        "Answer ONLY with {count} lines in the format: Short title | What must be delivered.",
        "part": "Part {index} of {total} of the task «{title}».",
        "work": "You are working on the task «{title}».\nDetails: {description}\n"
        "Write the outcome of your work in a few lines (a markdown draft).",
        "review": "Review the work delivered on the task «{title}».\nResult: {result}\n"
        "Give a short opinion and say whether you approve.",
        "test": "You are the tester for the task «{title}».\nDelivered result: {result}\n"
        "Write the test plan and the test results in a few lines (markdown).",
        "test_title": "Tests",
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
        language: Language | OfficeLanguage,
        chat_repository: IChatRepository,
        sprint_max_days: int = 15,
    ) -> None:
        self._agents = agent_repository
        self._tasks = task_repository
        self._assign = assign_task
        self._move = move_task
        self._dispatch = dispatch_goal
        self._send = send_message
        self._write = write_artifact
        self._bus = message_bus
        self._office_language = (
            language if isinstance(language, OfficeLanguage) else OfficeLanguage(language)
        )
        self._chat = chat_repository
        self._sprint_max_days = sprint_max_days

    @property
    def _language(self) -> Language:
        return self._office_language.current

    async def tick(self) -> int:
        """Executa um passo por estágio; devolve quantas tarefas avançaram."""
        moved = 0
        for step in (self._review, self._test, self._work, self._assign_todo, self._plan):
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

    # Bloco: cerimônia de planejamento — conduzida pelo cargo mais alto (PO, depois SM),
    # divide as tarefas para que todo profissional tenha trabalho e só então libera o fluxo.
    async def _plan(self) -> int:
        planner = await self._first(_PLANNERS)
        if planner is None:
            return 0
        backlog = await self._tasks_in(TaskStatus.BACKLOG)
        if not backlog:
            return 0
        workers = [
            a
            for a in await self._agents.list_all()
            if a.role in EXECUTOR_ROLES and a.status != AgentStatus.OFFLINE
        ]
        open_count = len([t for t in await self._tasks.list_all() if t.status != TaskStatus.DONE])
        backlog = await self._split_for_team(backlog, max(0, len(workers) - open_count))
        await self._hold_planning(planner, backlog, workers)
        for task in backlog:
            await self._move.execute(task.task_id, TaskStatus.TODO, planner.agent_id, planner.role)
        return len(backlog)

    async def _split_for_team(self, backlog: list[Task], missing: int) -> list[Task]:
        """Divide tarefas em partes até haver trabalho para todos."""
        note = _PROMPTS[self._language]["part"]
        result: list[Task] = []
        for task, more in zip(backlog, distribute_extra_parts(len(backlog), missing), strict=True):
            subtasks = await self._breakdown(task, more + 1) if more else None
            for part in split_task(task, more + 1, note, subtasks):
                if more:
                    await self._tasks.save(part)
                result.append(part)
        return result

    async def _breakdown(self, task: Task, count: int) -> list[tuple[str, str]]:
        """Pede ao planejador subtarefas distintas; vazio se o LLM falhar."""
        planner = await self._first(_PLANNERS)
        if planner is None:
            return []
        prompt = _PROMPTS[self._language]["breakdown"].format(
            title=task.title, description=task.description, count=count
        )
        try:
            text = await self._speak(planner, prompt, task.task_id)
        except Exception:
            logger.exception("Falha ao detalhar a tarefa %s", task.title)
            return []
        return parse_subtasks(text, count)

    async def _speak(self, speaker: Agent, prompt: str, task_id: TaskId | None = None) -> str:
        """Pede ao agente uma fala via LLM e a publica no chão do escritório."""
        text = (await self._dispatch.execute(speaker.agent_id, prompt, self._language)).thought
        if await self._chat.find_session(_FLOOR_SESSION) is None:
            await self._chat.save_session(Session(_FLOOR_SESSION))
        await self._send.execute(
            SendMessageInput(
                session_id=_FLOOR_SESSION,
                content=text,
                sender_id=speaker.agent_id,
                task_id=task_id,
            )
        )
        return text

    async def _hold_planning(self, planner: Agent, tasks: list[Task], workers: list[Agent]) -> None:
        prompt = _PROMPTS[self._language]["planning"].format(
            tasks="; ".join(t.title for t in tasks),
            team=", ".join(f"{w.name} ({w.role.value})" for w in workers),
            days=self._sprint_max_days,
        )
        plan = await self._speak(planner, prompt)
        title = _PROMPTS[self._language]["planning_title"]
        length = _PROMPTS[self._language]["sprint_length"].format(days=self._sprint_max_days)
        await self._write.execute(
            WriteArtifactInput(
                title=title,
                content=f"# {title}\n\n{length}\n\n{plan}\n",
                artifact_type=ArtifactType.SPRINT_PLANNING,
                path=f"planning/{uuid4()}.md",
                author_id=planner.agent_id,
                author_role=planner.role,
            )
        )

    async def _assign_todo(self) -> int:
        coordinator = await self._first(_COORDINATORS)
        if coordinator is None:
            return 0
        moved = 0
        for task in await self._tasks_in(TaskStatus.TODO):
            worker = await self._owner_or_idle(task)
            if worker is None:
                continue
            await self._assign.execute(
                task.task_id, worker.agent_id, coordinator.agent_id, coordinator.role
            )
            await self._announce(worker.agent_id)
            moved += 1
        return moved

    # Bloco: respeita o responsável já definido; se sumiu ou está offline, usa um ocioso da área.
    async def _owner_or_idle(self, task: Task) -> Agent | None:
        owner = await self._assignee(task)
        if owner is not None and owner.status != AgentStatus.OFFLINE:
            return owner if owner.status == AgentStatus.IDLE else None
        return select_owner(
            task, await self._agents.list_all(), await open_load(self._tasks), idle_only=True
        )

    async def _work(self) -> int:
        for task in await self._tasks_in(TaskStatus.IN_PROGRESS):
            worker = await self._assignee(task)
            if worker is None or worker.role not in EXECUTOR_ROLES:
                continue
            prompt = _PROMPTS[self._language]["work"].format(
                title=task.title, description=task.description
            )
            result = await self._speak(worker, prompt, task.task_id)
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
            await self._move.execute(task.task_id, TaskStatus.TESTING, worker.agent_id, worker.role)
            return 1
        return 0

    # Bloco: o QA pega a entrega e a testa; só depois ela segue para a revisão (ADR-050).
    async def _test(self) -> int:
        for task in await self._tasks_in(TaskStatus.TESTING):
            tester = await self._first_tester(task)
            if tester is None:
                continue
            prompt = _PROMPTS[self._language]["test"].format(
                title=task.title, result=task.result or ""
            )
            report = await self._speak(tester, prompt, task.task_id)
            label = _PROMPTS[self._language]["test_title"]
            await self._write.execute(
                WriteArtifactInput(
                    title=f"{label}: {task.title}",
                    content=f"# {label}: {task.title}\n\n{report}\n",
                    artifact_type=ArtifactType.TEST_PLAN,
                    path=f"tests/{task.task_id.value}.md",
                    author_id=tester.agent_id,
                    author_role=tester.role,
                )
            )
            await self._move.execute(
                task.task_id, TaskStatus.IN_REVIEW, tester.agent_id, tester.role
            )
            return 1
        return 0

    async def _first_tester(self, task: Task) -> Agent | None:
        for agent in await self._agents.list_all():
            if (
                agent.role in _TESTERS
                and agent.status == AgentStatus.IDLE
                and agent.agent_id != task.assigned_to
            ):
                return agent
        return None

    async def _review(self) -> int:
        for task in await self._tasks_in(TaskStatus.IN_REVIEW):
            reviewer = await self._first_reviewer(task)
            if reviewer is None:
                continue
            prompt = _PROMPTS[self._language]["review"].format(
                title=task.title, result=task.result or ""
            )
            opinion = await self._speak(reviewer, prompt, task.task_id)
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
