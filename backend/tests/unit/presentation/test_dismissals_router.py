"""Testes das rotas de demissão proposta pelo RH, com erros localizados pt/en."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.presentation.dependencies import (
    get_agent_repository,
    get_dismissal_repository,
    get_task_repository,
)
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    for factory in (get_agent_repository, get_dismissal_repository, get_task_repository):
        factory.cache_clear()
    yield


def _hire(role: str) -> str:
    return client.post("/agents", json={"name": role, "role": role, "llm_model": "m"}).json()[
        "agent_id"
    ]


def _propose(hr: str, target: str, reason: str = "Entregas atrasadas") -> dict[str, object]:
    return {"proposer_id": hr, "agent_id": target, "reason": reason}


class TestDismissalsRoutes:
    def test_propose_list_and_approve_fires_the_agent(self) -> None:
        hr, dev = _hire("hr_manager"), _hire("dev_junior")
        created = client.post("/dismissals", json=_propose(hr, dev))
        assert created.status_code == 201
        proposal_id = created.json()["proposal_id"]

        pending = client.get("/dismissals", params={"pending_only": True}).json()
        assert [p["proposal_id"] for p in pending] == [proposal_id]

        approved = client.post(f"/dismissals/{proposal_id}/approve")
        assert approved.status_code == 200
        assert approved.json()["status"] == "approved"
        agents = {a["agent_id"]: a["status"] for a in client.get("/agents").json()}
        assert agents[dev] == "offline"
        assert client.get("/dismissals", params={"pending_only": True}).json() == []

    def test_reject_keeps_the_agent(self) -> None:
        hr, dev = _hire("hr_manager"), _hire("dev_junior")
        proposal_id = client.post("/dismissals", json=_propose(hr, dev)).json()["proposal_id"]
        rejected = client.post(f"/dismissals/{proposal_id}/reject")
        assert rejected.json()["status"] == "rejected"
        agents = {a["agent_id"]: a["status"] for a in client.get("/agents").json()}
        assert agents[dev] != "offline"

    def test_only_hr_can_propose_and_errors_are_localized(self) -> None:
        po, dev = _hire("product_owner"), _hire("dev_junior")
        denied = client.post(
            "/dismissals", json=_propose(po, dev), headers={"Accept-Language": "pt"}
        )
        assert denied.status_code == 403
        assert "só o RH" in denied.json()["detail"]
        english = client.post(
            "/dismissals", json=_propose(po, dev), headers={"Accept-Language": "en"}
        )
        assert "only HR" in english.json()["detail"]

    def test_decide_twice_is_409_and_unknown_is_404(self) -> None:
        hr, dev = _hire("hr_manager"), _hire("dev_junior")
        proposal_id = client.post("/dismissals", json=_propose(hr, dev)).json()["proposal_id"]
        client.post(f"/dismissals/{proposal_id}/reject")
        assert client.post(f"/dismissals/{proposal_id}/approve").status_code == 409
        assert client.post(f"/dismissals/{uuid4()}/approve").status_code == 404

    def test_duplicate_pending_is_409(self) -> None:
        hr, dev = _hire("hr_manager"), _hire("dev_junior")
        assert client.post("/dismissals", json=_propose(hr, dev)).status_code == 201
        assert client.post("/dismissals", json=_propose(hr, dev)).status_code == 409
