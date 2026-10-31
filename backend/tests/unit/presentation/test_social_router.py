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

    def test_record_interaction_accumulates(self) -> None:
        a, b = uuid4(), uuid4()
        client.post("/relationships/interactions", json={"first": str(a), "second": str(b)})
        response = client.post(
            "/relationships/interactions", json={"first": str(b), "second": str(a), "delta": 0.5}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["interactions"] == 2
        assert body["score"] == pytest.approx(0.55)

    def test_record_interaction_rejects_self_and_bad_delta(self) -> None:
        a = str(uuid4())
        assert (
            client.post("/relationships/interactions", json={"first": a, "second": a}).status_code
            == 422
        )
        other = str(uuid4())
        bad = {"first": a, "second": other, "delta": 5}
        assert client.post("/relationships/interactions", json=bad).status_code == 422

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


class TestMeetingWriteRoutes:
    def _start(self) -> dict:
        organizer = uuid4()
        response = client.post(
            "/meetings", json={"kind": "daily", "title": "Daily", "organizer_id": str(organizer)}
        )
        assert response.status_code == 201
        return response.json()

    def test_start_includes_organizer(self) -> None:
        body = self._start()
        assert body["status"] == "in_progress"
        assert body["participants"] == [body["organizer_id"]]

    def test_invalid_kind(self) -> None:
        response = client.post(
            "/meetings", json={"kind": "nope", "title": "x", "organizer_id": str(uuid4())}
        )
        assert response.status_code == 422

    def test_finish_and_conflict(self) -> None:
        meeting = self._start()
        url = f"/meetings/{meeting['meeting_id']}/finish"
        ok = client.post(url, json={"summary": "ok", "decisions": ["a"]})
        assert ok.status_code == 200
        assert ok.json()["decisions"] == ["a"]
        assert client.post(url, json={"summary": "again"}).status_code == 409

    def test_finish_not_found_localized(self) -> None:
        response = client.post(
            f"/meetings/{uuid4()}/finish",
            json={"summary": "x"},
            headers={"Accept-Language": "pt"},
        )
        assert response.status_code == 404
        assert "Reunião" in response.json()["detail"]
