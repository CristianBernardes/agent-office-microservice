"""Testes dos repositórios de chat (em memória e Postgres com pool falsa)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.domain.entities.chat import ChatMessage, Goal, GoalStatus, MessageKind, Session
from src.domain.value_objects.identifiers import GoalId, MessageId, SessionId
from src.infrastructure.persistence.in_memory_chat_repository import InMemoryChatRepository
from src.infrastructure.persistence.postgres_chat_repository import PostgresChatRepository
from tests.unit.infrastructure.test_postgres_repositories import FakePool

pytestmark = pytest.mark.unit


class TestInMemoryChat:
    async def test_session_goal_messages_roundtrip(self) -> None:
        repo = InMemoryChatRepository()
        session = Session(SessionId.generate())
        await repo.save_session(session)
        await repo.save_goal(Goal(GoalId.generate(), session.session_id, "g"))
        for text in ("a", "b", "c"):
            await repo.add_message(ChatMessage(MessageId.generate(), session.session_id, text))
        assert await repo.find_session(session.session_id) == session
        assert await repo.find_session(SessionId.generate()) is None
        assert [m.content for m in await repo.list_messages(session.session_id)] == ["a", "b", "c"]
        assert [m.content for m in await repo.list_messages(session.session_id, 2)] == ["b", "c"]


class TestPostgresChat:
    async def test_writes_use_expected_arguments(self) -> None:
        pool = FakePool()
        repo = PostgresChatRepository(pool)  # type: ignore[arg-type]
        session = Session(SessionId.generate())
        goal = Goal(GoalId.generate(), session.session_id, "g")
        message = ChatMessage(MessageId.generate(), session.session_id, "oi")
        await repo.save_session(session)
        await repo.save_goal(goal)
        await repo.add_message(message)
        assert [sql.split()[2] for sql, _ in pool.executed] == ["sessions", "goals", "messages"]
        assert pool.executed[1][1][4] == "open"

    async def test_reads_map_rows(self) -> None:
        sid, now = uuid4(), datetime.now(UTC)
        pool = FakePool([{"session_id": sid, "scenario": "default", "started_at": now}])
        repo = PostgresChatRepository(pool)  # type: ignore[arg-type]
        assert (await repo.find_session(SessionId(sid))) is not None
        assert await PostgresChatRepository(FakePool()).find_session(SessionId(sid)) is None  # type: ignore[arg-type]

        goal_row = {
            "goal_id": uuid4(),
            "session_id": sid,
            "requested_by": None,
            "text": "g",
            "status": "done",
            "created_at": now,
        }
        goals = await PostgresChatRepository(FakePool([goal_row])).list_goals()  # type: ignore[arg-type]
        assert goals[0].status is GoalStatus.DONE

        msg_row = {
            "message_id": uuid4(),
            "session_id": sid,
            "sender_id": None,
            "recipient_id": None,
            "task_id": None,
            "kind": "thought",
            "content": "hm",
            "created_at": now,
        }
        msgs = await PostgresChatRepository(FakePool([msg_row])).list_messages(SessionId(sid))  # type: ignore[arg-type]
        assert msgs[0].kind is MessageKind.THOUGHT
