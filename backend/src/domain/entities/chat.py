"""Entidades do chat: ``Session``, ``Goal`` e ``ChatMessage`` (ver ADR-019)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from src.domain.value_objects.identifiers import AgentId, GoalId, MessageId, SessionId, TaskId


# Bloco: natureza da mensagem (espelha o CHECK da tabela messages).
class MessageKind(str, Enum):
    CHAT = "chat"
    THOUGHT = "thought"
    SYSTEM = "system"
    QUESTION = "question"
    DECISION = "decision"


# Bloco: estado de um objetivo pedido pelo usuário.
class GoalStatus(str, Enum):
    OPEN = "open"
    DONE = "done"
    CANCELLED = "cancelled"


# Bloco: sessão de trabalho que agrupa objetivos e conversas.
@dataclass(slots=True)
class Session:
    session_id: SessionId
    scenario: str = "default"
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# Bloco: objetivo de negócio; ``requested_by`` nulo significa o usuário.
@dataclass(slots=True)
class Goal:
    goal_id: GoalId
    session_id: SessionId
    text: str
    requested_by: AgentId | None = None
    status: GoalStatus = GoalStatus.OPEN
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# Bloco: mensagem de chat; ``sender_id`` nulo = usuário, ``recipient_id`` nulo = broadcast.
@dataclass(frozen=True, slots=True)
class ChatMessage:
    message_id: MessageId
    session_id: SessionId
    content: str
    sender_id: AgentId | None = None
    recipient_id: AgentId | None = None
    task_id: TaskId | None = None
    kind: MessageKind = MessageKind.CHAT
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
