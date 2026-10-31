"""Testes unitários das rotas de relacionamentos e reuniões."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.domain.entities.meeting import Meeting, MeetingKind
from src.domain.value_objects.identifiers import AgentId, GoalId, MeetingId
from src.presentation.dependencies import (
    get_meeting_repository,
    get_record_interaction_use_case,
    get_relationship_repository,
)
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_meeting_repository.cache_clear()
    get_relationship_repository.cache_clear()
    yield


class TestSocialRoutes:
    async def test_relationships_of_agent(self) -> None:
        a, b = AgentId(UUID(int=1)), AgentId(UUID(int=2))
        await get_record_interaction_use_case().record_group([a, b])

        response = client.get(f"/agents/{a.value}/relationships")

        assert response.status_code == 200
        [item] = response.json()
        assert item["interactions"] == 1
        assert item["status"] == "acquaintance"

    def test_unknown_agent_has_no_relationships(self) -> None:
        assert client.get(f"/agents/{uuid4()}/relationships").json() == []

    async def test_goal_meetings(self) -> None:
        goal = GoalId.generate()
        organizer = AgentId.generate()
        await get_meeting_repository().save(
            Meeting(MeetingId.generate(), MeetingKind.DAILY, "Daily", organizer, (organizer,), goal)
        )

        body = client.get(f"/goals/{goal.value}/meetings").json()

        assert [m["title"] for m in body] == ["Daily"]
        assert client.get(f"/goals/{uuid4()}/meetings").json() == []
