"""Implementação PostgreSQL do ``IHiringRepository``."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import asyncpg

from src.domain.entities.agent import Role
from src.domain.entities.hiring import HiringProposal, HiringStatus
from src.domain.interfaces.hiring_repository import IHiringRepository
from src.domain.value_objects.identifiers import AgentId, HiringId, TaskId

_UPSERT_SQL = """
INSERT INTO hiring_proposals (proposal_id, role, proposed_by, reason, task_id, status,
                              hired_agent_id, created_at, decided_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
ON CONFLICT (proposal_id) DO UPDATE SET
    status = EXCLUDED.status, hired_agent_id = EXCLUDED.hired_agent_id,
    decided_at = EXCLUDED.decided_at
"""


def _to_proposal(row: Mapping[str, Any]) -> HiringProposal:
    return HiringProposal(
        proposal_id=HiringId(row["proposal_id"]),
        role=Role(row["role"]),
        proposed_by=AgentId(row["proposed_by"]),
        reason=row["reason"],
        task_id=TaskId(row["task_id"]) if row["task_id"] else None,
        status=HiringStatus(row["status"]),
        hired_agent_id=AgentId(row["hired_agent_id"]) if row["hired_agent_id"] else None,
        created_at=row["created_at"],
        decided_at=row["decided_at"],
    )


class PostgresHiringRepository(IHiringRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, proposal: HiringProposal) -> None:
        await self._pool.execute(
            _UPSERT_SQL,
            proposal.proposal_id.value,
            proposal.role.value,
            proposal.proposed_by.value,
            proposal.reason,
            proposal.task_id.value if proposal.task_id else None,
            proposal.status.value,
            proposal.hired_agent_id.value if proposal.hired_agent_id else None,
            proposal.created_at,
            proposal.decided_at,
        )

    async def get(self, proposal_id: HiringId) -> HiringProposal | None:
        row = await self._pool.fetchrow(
            "SELECT * FROM hiring_proposals WHERE proposal_id = $1", proposal_id.value
        )
        return _to_proposal(row) if row else None

    async def list_all(self) -> list[HiringProposal]:
        rows = await self._pool.fetch("SELECT * FROM hiring_proposals ORDER BY created_at")
        return [_to_proposal(row) for row in rows]
