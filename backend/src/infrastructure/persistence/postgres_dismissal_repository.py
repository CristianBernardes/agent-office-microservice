"""Implementação PostgreSQL do ``IDismissalRepository`` (ADR-056)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import asyncpg

from src.domain.entities.dismissal import DismissalProposal, DismissalStatus
from src.domain.interfaces.dismissal_repository import IDismissalRepository
from src.domain.value_objects.identifiers import AgentId, DismissalId

_UPSERT_SQL = """
INSERT INTO dismissal_proposals (proposal_id, agent_id, proposed_by, reason, status,
                                 created_at, decided_at)
VALUES ($1, $2, $3, $4, $5, $6, $7)
ON CONFLICT (proposal_id) DO UPDATE SET
    status = EXCLUDED.status, decided_at = EXCLUDED.decided_at
"""


def _to_proposal(row: Mapping[str, Any]) -> DismissalProposal:
    return DismissalProposal(
        proposal_id=DismissalId(row["proposal_id"]),
        agent_id=AgentId(row["agent_id"]),
        proposed_by=AgentId(row["proposed_by"]),
        reason=row["reason"],
        status=DismissalStatus(row["status"]),
        created_at=row["created_at"],
        decided_at=row["decided_at"],
    )


class PostgresDismissalRepository(IDismissalRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, proposal: DismissalProposal) -> None:
        await self._pool.execute(
            _UPSERT_SQL,
            proposal.proposal_id.value,
            proposal.agent_id.value,
            proposal.proposed_by.value,
            proposal.reason,
            proposal.status.value,
            proposal.created_at,
            proposal.decided_at,
        )

    async def get(self, proposal_id: DismissalId) -> DismissalProposal | None:
        row = await self._pool.fetchrow(
            "SELECT * FROM dismissal_proposals WHERE proposal_id = $1", proposal_id.value
        )
        return _to_proposal(row) if row else None

    async def list_all(self) -> list[DismissalProposal]:
        rows = await self._pool.fetch("SELECT * FROM dismissal_proposals ORDER BY created_at")
        return [_to_proposal(row) for row in rows]
