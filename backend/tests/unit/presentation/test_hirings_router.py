"""Testes das rotas de contratação proposta pelo RH e decidida pelo dono do produto."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.application.hiring.hiring_use_cases import ProposeHiringInput
from src.domain.entities.agent import Role
from src.domain.value_objects.identifiers import AgentId
from src.presentation.dependencies import (
    get_agent_repository,
    get_hiring_repository,
    get_propose_hiring_use_case,
)
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    for factory in (get_agent_repository, get_hiring_repository):
        factory.cache_clear()
    yield


def _hire(role: str) -> str:
    return client.post("/agents", json={"name": role, "role": role, "llm_model": "m"}).json()[
        "agent_id"
    ]


def _propose(hr: str, role: Role = Role.DEV_MID) -> str:
    proposal = asyncio.run(
        get_propose_hiring_use_case().execute(
            ProposeHiringInput(AgentId(value=UUID(hr)), role, "Falta capacidade")
        )
    )
    return str(proposal.proposal_id)


class TestHiringsRoutes:
    def test_approve_hires_with_the_chosen_name_and_model(self) -> None:
        proposal_id = _propose(_hire("hr_manager"))
        pending = client.get("/hirings", params={"pending_only": True}).json()
        assert [p["proposal_id"] for p in pending] == [proposal_id]

        approved = client.post(
            f"/hirings/{proposal_id}/approve", json={"name": "Bruno", "llm_model": "qwen"}
        )

        assert approved.status_code == 200
        body = approved.json()
        assert body["status"] == "approved"
        hired = next(
            a for a in client.get("/agents").json() if a["agent_id"] == body["hired_agent_id"]
        )
        assert (hired["name"], hired["role"], hired["llm_model"]) == ("Bruno", "dev_mid", "qwen")
        assert client.get("/hirings", params={"pending_only": True}).json() == []

    def test_reject_hires_nobody(self) -> None:
        proposal_id = _propose(_hire("hr_manager"))
        before = len(client.get("/agents").json())
        rejected = client.post(f"/hirings/{proposal_id}/reject")
        assert rejected.json()["status"] == "rejected"
        assert len(client.get("/agents").json()) == before

    def test_blank_name_and_double_decision_are_rejected(self) -> None:
        proposal_id = _propose(_hire("hr_manager"))
        blank = client.post(
            f"/hirings/{proposal_id}/approve", json={"name": "  ", "llm_model": "m"}
        )
        assert blank.status_code == 422
        client.post(f"/hirings/{proposal_id}/reject")
        again = client.post(
            f"/hirings/{proposal_id}/approve", json={"name": "Ana", "llm_model": "m"}
        )
        assert again.status_code == 409

    def test_unknown_proposal_is_404(self) -> None:
        response = client.post(f"/hirings/{uuid4()}/reject", headers={"Accept-Language": "pt"})
        assert response.status_code == 404
        assert "não foi encontrada" in response.json()["detail"]

    def test_errors_are_localized_in_english(self) -> None:
        proposal_id = _propose(_hire("hr_manager"))
        blank = client.post(
            f"/hirings/{proposal_id}/approve",
            json={"name": " ", "llm_model": "m"},
            headers={"Accept-Language": "en"},
        )
        assert blank.status_code == 422
        assert "name" in blank.json()["detail"].lower()
        missing = client.post(f"/hirings/{uuid4()}/reject", headers={"Accept-Language": "en"})
        assert "was not found" in missing.json()["detail"]

    def test_duplicate_name_is_a_localized_conflict(self) -> None:
        hr = _hire("hr_manager")
        proposal_id = _propose(hr)
        taken = client.post(
            f"/hirings/{proposal_id}/approve",
            json={"name": "HR_MANAGER", "llm_model": "m"},
            headers={"Accept-Language": "pt"},
        )
        assert taken.status_code == 409
        assert "Já existe" in taken.json()["detail"]
