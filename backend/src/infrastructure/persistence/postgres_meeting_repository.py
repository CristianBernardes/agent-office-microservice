"""Implementação PostgreSQL do ``IMeetingRepository`` (ADR-028)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import asyncpg

from src.domain.entities.meeting import Meeting, MeetingKind, MeetingStatus
from src.domain.interfaces.meeting_repository import IMeetingRepository
from src.domain.value_objects.identifiers import AgentId, GoalId, MeetingId

_UPSERT_SQL = """
INSERT INTO meetings (meeting_id, goal_id, kind, title, organizer_id, status, summary,
                      decisions, scheduled_at, started_at, ended_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11)
ON CONFLICT (meeting_id) DO UPDATE SET
    status = EXCLUDED.status, summary = EXCLUDED.summary, decisions = EXCLUDED.decisions,
    started_at = EXCLUDED.started_at, ended_at = EXCLUDED.ended_at
"""

_PARTICIPANT_SQL = """
INSERT INTO meeting_participants (meeting_id, agent_id) VALUES ($1, $2)
ON CONFLICT DO NOTHING
"""

_SELECT_SQL = """
SELECT m.*, COALESCE(
    (SELECT array_agg(p.agent_id) FROM meeting_participants p WHERE p.meeting_id = m.meeting_id),
    '{}') AS participant_ids
FROM meetings m
"""


def _to_meeting(row: Mapping[str, Any]) -> Meeting:
    decisions = row["decisions"]
    if isinstance(decisions, str):
        decisions = json.loads(decisions)
    return Meeting(
        meeting_id=MeetingId(row["meeting_id"]),
        kind=MeetingKind(row["kind"]),
        title=row["title"],
        organizer_id=AgentId(row["organizer_id"]) if row["organizer_id"] else None,
        participants=tuple(AgentId(p) for p in row["participant_ids"]),
        goal_id=GoalId(row["goal_id"]) if row["goal_id"] else None,
        status=MeetingStatus(row["status"]),
        summary=row["summary"] or "",
        decisions=tuple(decisions),
        scheduled_at=row["scheduled_at"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
    )


class PostgresMeetingRepository(IMeetingRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, meeting: Meeting) -> None:
        async with self._pool.acquire() as connection, connection.transaction():
            await connection.execute(
                _UPSERT_SQL,
                meeting.meeting_id.value,
                meeting.goal_id.value if meeting.goal_id else None,
                meeting.kind.value,
                meeting.title,
                meeting.organizer_id.value if meeting.organizer_id else None,
                meeting.status.value,
                meeting.summary,
                json.dumps(list(meeting.decisions)),
                meeting.scheduled_at,
                meeting.started_at,
                meeting.ended_at,
            )
            for participant in meeting.participants:
                await connection.execute(
                    _PARTICIPANT_SQL, meeting.meeting_id.value, participant.value
                )

    async def get(self, meeting_id: MeetingId) -> Meeting | None:
        row = await self._pool.fetchrow(f"{_SELECT_SQL} WHERE m.meeting_id = $1", meeting_id.value)
        return _to_meeting(row) if row else None

    async def list_by_goal(self, goal_id: GoalId) -> list[Meeting]:
        rows = await self._pool.fetch(
            f"{_SELECT_SQL} WHERE m.goal_id = $1 ORDER BY m.scheduled_at", goal_id.value
        )
        return [_to_meeting(row) for row in rows]
