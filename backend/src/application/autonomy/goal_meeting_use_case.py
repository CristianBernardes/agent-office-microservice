"""Caso de uso: o time se reúne sobre um objetivo e registra a ata (ADR-022)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.application.chat.chat_use_cases import SendMessageInput, SendMessageUseCase
from src.application.memory.memory_use_cases import RememberInput, RememberUseCase
from src.application.relationships.relationship_use_cases import RecordInteractionUseCase
from src.application.tasks.task_use_cases import CreateTaskInput, CreateTaskUseCase
from src.domain.entities.agent import Agent, Role
from src.domain.entities.artifact import ArtifactType
from src.domain.entities.meeting import Meeting, MeetingKind, MeetingStatus
from src.domain.entities.memory import MemoryType
from src.domain.entities.task import Priority
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.meeting_repository import IMeetingRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import GoalId, MeetingId, SessionId

logger = logging.getLogger(__name__)

_GOALS_CREATED_TOPIC = "office/goals/created"

# Bloco: ordem de fala da reunião (quem define o problema fala primeiro; o SM fecha).
MEETING_ORDER: tuple[Role, ...] = (
    Role.PRODUCT_OWNER,
    Role.PRODUCT_CONSULTANT,
    Role.DATA_ANALYST,
    Role.TECH_LEAD,
    Role.DEV_SENIOR,
    Role.QA_ENGINEER,
    Role.SCRUM_MASTER,
)

# Bloco: rótulos localizados do contexto e da ata.
_LABELS = {
    Language.PT: {
        "goal": "Objetivo do time",
        "minutes": "Ata da reunião até agora",
        "turn": "Sua vez de falar, como {role}. Contribua com o seu papel.",
        "debate": "Rodada {round} de debate, como {role}. Responda aos colegas, concorde ou "
        "discorde com argumentos e refine a proposta.",
        "title": "Ata da reunião — {goal}",
    },
    Language.EN: {
        "goal": "Team goal",
        "minutes": "Meeting minutes so far",
        "turn": "Your turn to speak, as {role}. Contribute from your role.",
        "debate": "Debate round {round}, as {role}. Reply to your colleagues, agree or "
        "disagree with arguments and refine the proposal.",
        "title": "Meeting minutes — {goal}",
    },
}


# Bloco: nomes de cargo localizados para os cabeçalhos da ata.
_ROLE_NAMES: dict[Language, dict[Role, str]] = {
    Language.PT: {
        Role.PRODUCT_OWNER: "Product Owner",
        Role.SCRUM_MASTER: "Scrum Master",
        Role.TECH_LEAD: "Tech Lead",
        Role.DEV_SENIOR: "Desenvolvedor Sênior",
        Role.DEV_JUNIOR: "Desenvolvedor Júnior",
        Role.QA_ENGINEER: "Engenheiro de QA",
        Role.DATA_ANALYST: "Analista de Dados",
        Role.HR_MANAGER: "Gerente de RH",
        Role.PRODUCT_CONSULTANT: "Consultor de Produto",
    },
    Language.EN: {
        Role.PRODUCT_OWNER: "Product Owner",
        Role.SCRUM_MASTER: "Scrum Master",
        Role.TECH_LEAD: "Tech Lead",
        Role.DEV_SENIOR: "Senior Developer",
        Role.DEV_JUNIOR: "Junior Developer",
        Role.QA_ENGINEER: "QA Engineer",
        Role.DATA_ANALYST: "Data Analyst",
        Role.HR_MANAGER: "HR Manager",
        Role.PRODUCT_CONSULTANT: "Product Consultant",
    },
}


@dataclass(frozen=True, slots=True)
class GoalMeetingInput:
    goal_id: GoalId
    session_id: SessionId
    text: str
    language: Language | None = None


@dataclass(frozen=True, slots=True)
class MeetingTurn:
    agent: Agent
    thought: str


class GoalMeetingUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        dispatch_goal: DispatchGoalUseCase,
        send_message: SendMessageUseCase,
        remember: RememberUseCase,
        write_artifact: WriteArtifactUseCase,
        language: Language,
        create_task: CreateTaskUseCase | None = None,
        record_interaction: RecordInteractionUseCase | None = None,
        meeting_repository: IMeetingRepository | None = None,
        rounds: int = 1,
    ) -> None:
        self._rounds = max(1, rounds)
        self._meeting_repository = meeting_repository
        self._record_interaction = record_interaction
        self._create_task = create_task
        self._agents = agent_repository
        self._dispatch = dispatch_goal
        self._send_message = send_message
        self._remember = remember
        self._write_artifact = write_artifact
        self._language = language

    async def execute(self, data: GoalMeetingInput) -> list[MeetingTurn]:
        participants = await self._participants()
        if not participants:
            logger.warning("Nenhum agente disponível para a reunião do objetivo %s", data.goal_id)
            return []
        turns: list[MeetingTurn] = []
        for round_number in range(1, self._rounds + 1):
            for agent in participants:
                turn = await self._take_turn(agent, data, turns, round_number)
                if turn is not None:
                    turns.append(turn)
        if turns:
            await self._write_minutes(data, turns)
            await self._create_backlog(turns, data.goal_id)
            await self._bond(turns)
            await self._register_meeting(data, turns)
        return turns

    async def _participants(self) -> list[Agent]:
        agents = await self._agents.list_all()
        by_role: dict[Role, Agent] = {}
        for agent in agents:
            by_role.setdefault(agent.role, agent)
        return [by_role[role] for role in MEETING_ORDER if role in by_role]

    async def _take_turn(
        self, agent: Agent, data: GoalMeetingInput, turns: list[MeetingTurn], round_number: int = 1
    ) -> MeetingTurn | None:
        try:
            response = await self._dispatch.execute(
                agent.agent_id, self._context(agent, data, turns, round_number), data.language
            )
            await self._send_message.execute(
                SendMessageInput(
                    session_id=data.session_id, content=response.thought, sender_id=agent.agent_id
                )
            )
            await self._remember.execute(
                RememberInput(
                    agent_id=agent.agent_id,
                    content=response.thought,
                    memory_type=MemoryType.CONVERSATION,
                    session_id=data.session_id,
                )
            )
        except Exception:
            # Um agente com falha (ex.: LLM fora do ar) não pode derrubar a reunião inteira.
            logger.exception("Falha na fala de %s na reunião", agent.name)
            return None
        return MeetingTurn(agent, response.thought)

    def _context(
        self, agent: Agent, data: GoalMeetingInput, turns: list[MeetingTurn], round_number: int = 1
    ) -> str:
        labels = _LABELS[data.language or self._language]
        minutes = "\n".join(f"- {t.agent.name} ({t.agent.role.value}): {t.thought}" for t in turns)
        parts = [f"{labels['goal']}: {data.text}"]
        if minutes:
            parts.append(f"{labels['minutes']}:\n{minutes}")
        key = "turn" if round_number == 1 else "debate"
        parts.append(labels[key].format(role=agent.role.value, round=round_number))
        return "\n\n".join(parts)

    # Bloco: guarda a reunião como `Meeting` concluída (ADR-028); falha aqui não derruba o fluxo.
    async def _register_meeting(self, data: GoalMeetingInput, turns: list[MeetingTurn]) -> None:
        if self._meeting_repository is None:
            return
        try:
            now = datetime.now(UTC)
            ids = tuple(dict.fromkeys(t.agent.agent_id for t in turns))
            await self._meeting_repository.save(
                Meeting(
                    meeting_id=MeetingId.generate(),
                    kind=MeetingKind.PLANNING,
                    title=data.text[:120],
                    organizer_id=ids[0],
                    participants=ids,
                    goal_id=data.goal_id,
                    status=MeetingStatus.DONE,
                    summary="\n".join(f"{t.agent.name}: {t.thought}" for t in turns),
                    started_at=now,
                    ended_at=now,
                )
            )
        except Exception:
            logger.exception("Falha ao registrar a reunião do objetivo %s", data.goal_id)

    async def _bond(self, turns: list[MeetingTurn]) -> None:
        if self._record_interaction is None:
            return
        try:
            await self._record_interaction.record_group(
                list(dict.fromkeys(t.agent.agent_id for t in turns))
            )
        except Exception:
            logger.exception("Falha ao registrar relacionamentos da reunião")

    async def _create_backlog(self, turns: list[MeetingTurn], goal_id: GoalId) -> None:
        owner = next((t.agent for t in turns if t.agent.role == Role.PRODUCT_OWNER), None)
        if owner is None or self._create_task is None:
            return
        # Com várias rodadas, cada agente vira uma tarefa só: a sua última fala (a mais refinada).
        final_turns = {t.agent.agent_id: t for t in turns}.values()
        for turn in final_turns:
            if turn.agent.role == Role.PRODUCT_OWNER:
                continue
            first_line = turn.thought.strip().splitlines()[0] if turn.thought.strip() else ""
            try:
                await self._create_task.execute(
                    CreateTaskInput(
                        title=f"[{turn.agent.role.value}] {first_line}"[:120],
                        description=turn.thought,
                        priority=Priority.MEDIUM,
                        creator_id=owner.agent_id,
                        creator_role=owner.role,
                        goal_id=goal_id,
                    )
                )
            except Exception:
                logger.exception("Falha ao criar tarefa de %s", turn.agent.name)

    async def _write_minutes(self, data: GoalMeetingInput, turns: list[MeetingTurn]) -> None:
        title = _LABELS[data.language or self._language]["title"].format(goal=data.text)
        names = _ROLE_NAMES[data.language or self._language]
        body = "\n\n".join(
            f"## {t.agent.name} — {names[t.agent.role]}\n\n{t.thought}" for t in turns
        )
        author = turns[0].agent
        await self._write_artifact.execute(
            WriteArtifactInput(
                title=title,
                content=f"# {title}\n\n{body}\n",
                artifact_type=ArtifactType.ANALYSIS,
                path=f"projects/{data.goal_id.value}/meeting.md",
                author_id=author.agent_id,
                author_role=author.role,
            )
        )


# Bloco: assina o tópico de objetivos e dispara a reunião em background (não bloqueia o listener).
_background_tasks: set[asyncio.Task[object]] = set()


def register_goal_autonomy(
    bus: IMessageBus, use_case_factory: Callable[[], GoalMeetingUseCase]
) -> Callable[[], Awaitable[None]]:
    """Devolve a corrotina de registro da assinatura de `office/goals/created`."""

    async def handler(_topic: str, envelope: dict[str, object]) -> None:
        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            return
        try:
            raw_language = payload.get("language")
            data = GoalMeetingInput(
                goal_id=GoalId(value=UUID(str(payload["goal_id"]))),
                session_id=SessionId(value=UUID(str(payload["session_id"]))),
                text=str(payload["text"]),
                language=Language.parse(str(raw_language)) if raw_language else None,
            )
        except (KeyError, ValueError):
            logger.warning("Evento de objetivo inválido descartado")
            return
        task = asyncio.create_task(use_case_factory().execute(data))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

    async def register() -> None:
        await bus.subscribe(_GOALS_CREATED_TOPIC, handler)

    return register
