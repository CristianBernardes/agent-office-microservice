"""Caso de uso: cerimônias automáticas disparadas pelo ciclo de trabalho.

Daily e refinamento rodam por intervalo de tempo; review e retrospectiva rodam ao fim da sprint
(todas as tarefas concluídas). Cada cerimônia vira uma ``Meeting`` concluída e uma ata em Markdown.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.domain.entities.agent import Agent, AgentStatus, Role
from src.domain.entities.artifact import ArtifactType
from src.domain.entities.meeting import Meeting, MeetingKind, MeetingStatus
from src.domain.entities.task import Task, TaskStatus
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.meeting_repository import IMeetingRepository
from src.domain.interfaces.task_repository import ITaskRepository
from src.domain.localization.language import Language
from src.domain.services.task_routing import EXECUTOR_ROLES
from src.domain.value_objects.identifiers import MeetingId

logger = logging.getLogger(__name__)

# Bloco: quem conduz a cerimônia (o primeiro disponível, nesta ordem).
_FACILITATORS = (
    Role.SCRUM_MASTER,
    Role.ENGINEERING_MANAGER,
    Role.PRODUCT_OWNER,
    Role.TECH_LEAD,
    Role.HR_MANAGER,
)

# Bloco: tipos de cerimônia automática e o rótulo do artefato de ata.
_TITLES = {
    Language.PT: {
        MeetingKind.DAILY: "Daily",
        MeetingKind.REFINEMENT: "Refinamento do backlog",
        MeetingKind.REVIEW: "Review da sprint",
        MeetingKind.RETROSPECTIVE: "Retrospectiva da sprint",
    },
    Language.EN: {
        MeetingKind.DAILY: "Daily",
        MeetingKind.REFINEMENT: "Backlog refinement",
        MeetingKind.REVIEW: "Sprint review",
        MeetingKind.RETROSPECTIVE: "Sprint retrospective",
    },
}

_PROMPTS = {
    Language.PT: {
        MeetingKind.DAILY: "Você participa da daily do time. Tarefas abertas: {tasks}.\n"
        "Em poucas linhas, diga: o que andou, o que fará a seguir e o que está bloqueado.",
        MeetingKind.REFINEMENT: "Você participa do refinamento do backlog. Tarefas a refinar: "
        "{tasks}.\nEm poucas linhas, aponte o que está vago, riscos, dependências e critérios "
        "de aceite que faltam.",
        MeetingKind.REVIEW: "Você participa da review da sprint. Entregas concluídas: {tasks}.\n"
        "Em poucas linhas, avalie o que foi entregue na sua área e o que ficou a desejar.",
        MeetingKind.RETROSPECTIVE: "Você participa da retrospectiva da sprint. Entregas: "
        "{tasks}.\nEm poucas linhas, diga o que foi bem, o que melhorar e uma ação concreta.",
    },
    Language.EN: {
        MeetingKind.DAILY: "You take part in the team's daily. Open tasks: {tasks}.\n"
        "In a few lines, say what progressed, what you will do next and what is blocked.",
        MeetingKind.REFINEMENT: "You take part in backlog refinement. Tasks to refine: {tasks}.\n"
        "In a few lines, point out what is vague, risks, dependencies and missing acceptance "
        "criteria.",
        MeetingKind.REVIEW: "You take part in the sprint review. Delivered work: {tasks}.\n"
        "In a few lines, assess what was delivered in your area and what fell short.",
        MeetingKind.RETROSPECTIVE: "You take part in the sprint retrospective. Deliveries: "
        "{tasks}.\nIn a few lines, say what went well, what to improve and one concrete action.",
    },
}

Speak = Callable[[Agent, str], Awaitable[str]]


@dataclass(frozen=True, slots=True)
class CeremonyConfig:
    daily_interval: timedelta
    refinement_interval: timedelta


def _names(tasks: list[Task]) -> str:
    return "; ".join(t.title for t in tasks[:10])


class CeremonySchedulerUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        task_repository: ITaskRepository,
        meeting_repository: IMeetingRepository,
        write_artifact: WriteArtifactUseCase,
        config: CeremonyConfig,
    ) -> None:
        self._agents = agent_repository
        self._tasks = task_repository
        self._meetings = meeting_repository
        self._write = write_artifact
        self._config = config

    async def tick(self, speak: Speak, language: Language) -> int:
        """Dispara as cerimônias que estão no ponto; devolve quantas aconteceram."""
        tasks = await self._tasks.list_all()
        meetings = await self._meetings.list_all()
        agents = [a for a in await self._agents.list_all() if a.status != AgentStatus.OFFLINE]
        facilitator = next((a for r in _FACILITATORS for a in agents if a.role == r), None)
        if facilitator is None:
            return 0
        held = 0
        for kind, selected in self._due(tasks, meetings):
            participants = self._participants(kind, selected, agents, facilitator)
            try:
                await self._hold(kind, selected, participants, facilitator, speak, language)
                held += 1
            except Exception:
                logger.exception("Falha na cerimônia automática %s", kind.value)
        return held

    def _due(
        self, tasks: list[Task], meetings: list[Meeting]
    ) -> list[tuple[MeetingKind, list[Task]]]:
        now = datetime.now(UTC)
        open_tasks = [t for t in tasks if t.status != TaskStatus.DONE]
        active = [t for t in open_tasks if t.status != TaskStatus.BACKLOG]
        backlog = [t for t in open_tasks if t.status in (TaskStatus.BACKLOG, TaskStatus.TODO)]
        due: list[tuple[MeetingKind, list[Task]]] = []
        if active and self._elapsed(meetings, MeetingKind.DAILY, now, self._config.daily_interval):
            due.append((MeetingKind.DAILY, active))
        if backlog and self._elapsed(
            meetings, MeetingKind.REFINEMENT, now, self._config.refinement_interval
        ):
            due.append((MeetingKind.REFINEMENT, backlog))
        delivered = self._delivered_since_last_retrospective(tasks, meetings)
        if delivered and not open_tasks:
            due.append((MeetingKind.REVIEW, delivered))
            due.append((MeetingKind.RETROSPECTIVE, delivered))
        return due

    @staticmethod
    def _last(meetings: list[Meeting], kind: MeetingKind) -> datetime | None:
        times = [
            m.ended_at or m.started_at or m.scheduled_at
            for m in meetings
            if m.kind == kind and m.goal_id is None
        ]
        return max(times) if times else None

    def _elapsed(
        self, meetings: list[Meeting], kind: MeetingKind, now: datetime, interval: timedelta
    ) -> bool:
        last = self._last(meetings, kind)
        return last is None or now - last >= interval

    def _delivered_since_last_retrospective(
        self, tasks: list[Task], meetings: list[Meeting]
    ) -> list[Task]:
        last = self._last(meetings, MeetingKind.RETROSPECTIVE)
        return [
            t
            for t in tasks
            if t.status == TaskStatus.DONE
            and t.completed_at is not None
            and (last is None or t.completed_at > last)
        ]

    @staticmethod
    def _participants(
        kind: MeetingKind, selected: list[Task], agents: list[Agent], facilitator: Agent
    ) -> list[Agent]:
        if kind in (MeetingKind.REVIEW, MeetingKind.RETROSPECTIVE):
            owners = {t.assigned_to for t in selected if t.assigned_to is not None}
            members = [a for a in agents if a.agent_id in owners]
        elif kind == MeetingKind.DAILY:
            owners = {t.assigned_to for t in selected if t.assigned_to is not None}
            members = [a for a in agents if a.agent_id in owners and a.role in EXECUTOR_ROLES]
        else:
            members = [a for a in agents if a.role in EXECUTOR_ROLES][:5]
        unique = {a.agent_id: a for a in [facilitator, *members]}
        return list(unique.values())

    async def _hold(
        self,
        kind: MeetingKind,
        selected: list[Task],
        participants: list[Agent],
        facilitator: Agent,
        speak: Speak,
        language: Language,
    ) -> None:
        started = datetime.now(UTC)
        prompt = _PROMPTS[language][kind].format(tasks=_names(selected))
        turns = [(agent, await speak(agent, prompt)) for agent in participants]
        title = _TITLES[language][kind]
        minutes = "\n".join(f"- {a.name} ({a.role.value}): {text}" for a, text in turns)
        await self._meetings.save(
            Meeting(
                meeting_id=MeetingId.generate(),
                kind=kind,
                title=title,
                organizer_id=facilitator.agent_id,
                participants=tuple(a.agent_id for a in participants),
                status=MeetingStatus.DONE,
                summary=minutes,
                scheduled_at=started,
                started_at=started,
                ended_at=datetime.now(UTC),
            )
        )
        body = "\n\n".join(f"## {a.name}\n\n{text}" for a, text in turns)
        await self._write.execute(
            WriteArtifactInput(
                title=title,
                content=f"# {title}\n\n{body}\n",
                artifact_type=ArtifactType.ANALYSIS,
                path=f"ceremonies/{kind.value}/{uuid4()}.md",
                author_id=facilitator.agent_id,
                author_role=facilitator.role,
            )
        )
