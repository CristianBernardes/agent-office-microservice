"""Entidade ``Memory``: lembrança de um agente (ver ADR-020)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from src.domain.value_objects.identifiers import AgentId, MemoryId, SessionId


# Bloco: tipo da lembrança (espelha o CHECK da tabela memories).
class MemoryType(str, Enum):
    OBSERVATION = "observation"
    REFLECTION = "reflection"
    CONVERSATION = "conversation"
    DECISION = "decision"
    FACT = "fact"


# Bloco: lembrança imutável; ``embedding`` vazio significa ainda não vetorizada.
@dataclass(frozen=True, slots=True)
class Memory:
    memory_id: MemoryId
    agent_id: AgentId
    content: str
    memory_type: MemoryType = MemoryType.OBSERVATION
    importance: float = 0.5
    embedding: tuple[float, ...] = ()
    session_id: SessionId | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0 and 1")
