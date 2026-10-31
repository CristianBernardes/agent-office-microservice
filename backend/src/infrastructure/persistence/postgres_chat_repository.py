"""Implementação PostgreSQL do ``IChatRepository`` (ADR-019)."""

from __future__ import annotations

import asyncpg

from src.domain.entities.chat import ChatMessage, Goal, GoalStatus, MessageKind, Session
from src.domain.interfaces.chat_repository import IChatRepository
from src.domain.value_objects.identifiers import AgentId, GoalId, MessageId, SessionId, TaskId

_SESSION_SQL = """
INSERT INTO sessions (session_id, scenario, started_at) VALUES ($1, $2, $3)
ON CONFLICT (session_id) DO NOTHING
"""

_GOAL_SQL = """
INSERT INTO goals (goal_id, session_id, requested_by, text, status, created_at)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (goal_id) DO UPDATE SET status = EXCLUDED.status,
    closed_at = CASE WHEN EXCLUDED.status = 'open' THEN NULL ELSE now() END
"""

_MESSAGE_SQL = """
INSERT INTO messages (message_id, session_id, task_id, sender_id, recipient_id, kind, content,
                      created_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
"""

# Últimas N em ordem cronológica: a subconsulta pega as mais recentes, a externa reordena.
_LIST_MESSAGES_SQL = """
SELECT * FROM (
    SELECT * FROM messages WHERE session_id = $1 ORDER BY created_at DESC LIMIT $2
) recent ORDER BY created_at
"""


# Bloco: repositório de chat sobre uma pool asyncpg injetada.
class PostgresChatRepository(IChatRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save_session(self, session: Session) -> None:
        """Insere a sessão (idempotente)."""
        await self._pool.execute(
            _SESSION_SQL, session.session_id.value, session.scenario, session.started_at
        )

    async def find_session(self, session_id: SessionId) -> Session | None:
        """Busca a sessão pelo ID."""
        row = await self._pool.fetchrow(
            "SELECT * FROM sessions WHERE session_id = $1", session_id.value
        )
        if row is None:
            return None
        return Session(SessionId(row["session_id"]), row["scenario"], row["started_at"])

    async def save_goal(self, goal: Goal) -> None:
        """Insere ou atualiza o objetivo."""
        await self._pool.execute(
            _GOAL_SQL,
            goal.goal_id.value,
            goal.session_id.value,
            goal.requested_by.value if goal.requested_by else None,
            goal.text,
            goal.status.value,
            goal.created_at,
        )

    async def list_goals(self) -> list[Goal]:
        """Objetivos do mais antigo ao mais novo."""
        rows = await self._pool.fetch("SELECT * FROM goals ORDER BY created_at")
        return [_to_goal(row) for row in rows]

    async def add_message(self, message: ChatMessage) -> None:
        """Grava a mensagem."""
        await self._pool.execute(
            _MESSAGE_SQL,
            message.message_id.value,
            message.session_id.value,
            message.task_id.value if message.task_id else None,
            message.sender_id.value if message.sender_id else None,
            message.recipient_id.value if message.recipient_id else None,
            message.kind.value,
            message.content,
            message.created_at,
        )

    async def list_messages(self, session_id: SessionId, limit: int = 100) -> list[ChatMessage]:
        """Últimas ``limit`` mensagens da sessão, em ordem cronológica."""
        rows = await self._pool.fetch(_LIST_MESSAGES_SQL, session_id.value, limit)
        return [_to_message(row) for row in rows]


def _to_goal(row: asyncpg.Record) -> Goal:
    requested_by = row["requested_by"]
    return Goal(
        goal_id=GoalId(row["goal_id"]),
        session_id=SessionId(row["session_id"]),
        text=row["text"],
        requested_by=None if requested_by is None else AgentId(requested_by),
        status=GoalStatus(row["status"]),
        created_at=row["created_at"],
    )


def _to_message(row: asyncpg.Record) -> ChatMessage:
    sender, recipient, task = row["sender_id"], row["recipient_id"], row["task_id"]
    return ChatMessage(
        message_id=MessageId(row["message_id"]),
        session_id=SessionId(row["session_id"]),
        content=row["content"],
        sender_id=None if sender is None else AgentId(sender),
        recipient_id=None if recipient is None else AgentId(recipient),
        task_id=None if task is None else TaskId(task),
        kind=MessageKind(row["kind"]),
        created_at=row["created_at"],
    )
