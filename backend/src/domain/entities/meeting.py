"""Entidade ``Meeting``: reunião ou cerimônia entre agentes (ver ADR-028)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import Enum

from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.value_objects.identifiers import AgentId, GoalId, MeetingId


# Bloco: tipo da cerimônia (espelha o CHECK da tabela meetings).
class MeetingKind(str, Enum):
    PLANNING = "planning"
    REFINEMENT = "refinement"
    DAILY = "daily"
    REVIEW = "review"
    RETROSPECTIVE = "retrospective"
    BRAINSTORM = "brainstorm"


class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Meeting:
    meeting_id: MeetingId
    kind: MeetingKind
    title: str
    organizer_id: AgentId | None
    participants: tuple[AgentId, ...]
    goal_id: GoalId | None = None
    status: MeetingStatus = MeetingStatus.SCHEDULED
    summary: str = ""
    decisions: tuple[str, ...] = field(default_factory=tuple)
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    ended_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.participants:
            raise DomainError("meeting.no_participants")

    def finish(self, summary: str, decisions: tuple[str, ...] = ()) -> Meeting:
        """Encerra a reunião registrando resumo e decisões."""
        if self.status is not MeetingStatus.IN_PROGRESS:
            raise DomainError("meeting.cannot_finish", title=self.title, status=self.status.value)
        return replace(
            self,
            status=MeetingStatus.DONE,
            summary=summary,
            decisions=decisions,
            ended_at=datetime.now(UTC),
        )
