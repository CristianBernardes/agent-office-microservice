"""Evento do feed de atividades (ADR-031)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ActivityEvent:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    agent_id: UUID | None = None
    event_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
