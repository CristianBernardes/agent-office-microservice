"""E2E (em memória): fluxo completo PO → Dev → QA pela API HTTP, ponta a ponta."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.presentation.dependencies import get_agent_repository, get_task_repository
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_task_repository.cache_clear()
    get_agent_repository.cache_clear()
    client.post("/agents", json={"name": "Ana", "role": "dev_senior", "llm_model": "m"})
    yield


def _actor(role: str) -> dict[str, str]:
    return {"actor_id": str(uuid4()), "actor_role": role}


def _create(role: str, title: str) -> str:
    return client.post("/tasks", json={"title": title, **_actor(role)}).json()["task_id"]  # type: ignore[no-any-return]


def _move(task_id: str, to: str, role: str) -> dict[str, object]:
    response = client.post(f"/tasks/{task_id}/move", json={"to_status": to, **_actor(role)})
    assert response.status_code == 200, response.text
    return response.json()  # type: ignore[no-any-return]


class TestProductOwnerDevQaFlow:
    def test_task_travels_from_backlog_to_done_with_full_history(self) -> None:
        task_id = _create("product_owner", "Landing page")

        assert _move(task_id, "todo", "product_owner")["status"] == "todo"
        assert _move(task_id, "in_progress", "dev_senior")["status"] == "in_progress"
        assert _move(task_id, "testing", "dev_senior")["status"] == "testing"
        assert _move(task_id, "in_review", "qa_engineer")["status"] == "in_review"
        assert _move(task_id, "done", "qa_engineer")["status"] == "done"

        history = client.get(f"/tasks/{task_id}/transitions").json()
        assert [item["to_status"] for item in history][-5:] == [
            "todo",
            "in_progress",
            "testing",
            "in_review",
            "done",
        ]

    def test_qa_rejection_sends_task_back_to_dev(self) -> None:
        task_id = _create("scrum_master", "Bug")
        _move(task_id, "todo", "scrum_master")
        _move(task_id, "in_progress", "dev_junior")
        _move(task_id, "testing", "dev_junior")

        assert _move(task_id, "in_progress", "qa_engineer")["status"] == "in_progress"

    def test_dev_cannot_approve_own_work(self) -> None:
        task_id = _create("product_owner", "X")
        _move(task_id, "todo", "product_owner")
        _move(task_id, "in_progress", "dev_senior")
        _move(task_id, "testing", "dev_senior")
        _move(task_id, "in_review", "qa_engineer")

        response = client.post(
            f"/tasks/{task_id}/move", json={"to_status": "done", **_actor("dev_senior")}
        )
        assert response.status_code == 403
