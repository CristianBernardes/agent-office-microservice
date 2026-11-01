"""Testes unitários das rotas de tarefas, incluindo erros localizados pt/en."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.presentation.dependencies import get_agent_repository, get_task_repository
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)
ACTOR = {"actor_id": str(uuid4()), "actor_role": "product_owner"}
DEV = {"actor_id": str(uuid4()), "actor_role": "dev_senior"}


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_task_repository.cache_clear()
    get_agent_repository.cache_clear()
    yield


def _hire() -> str:
    return client.post(
        "/agents", json={"name": "Ana", "role": "dev_senior", "llm_model": "m"}
    ).json()["agent_id"]


def _create(title: str = "Landing") -> str:
    return client.post("/tasks", json={"title": title, **ACTOR}).json()["task_id"]


class TestTasksRoutes:
    def test_create_and_list(self) -> None:
        response = client.post("/tasks", json={"title": "Landing", "priority": "high", **ACTOR})
        assert response.status_code == 201
        assert response.json()["status"] == "backlog"
        assert [t["title"] for t in client.get("/tasks").json()] == ["Landing"]

    def test_create_rejects_empty_title_and_bad_priority(self) -> None:
        assert client.post("/tasks", json={"title": "", **ACTOR}).status_code == 422
        assert (
            client.post("/tasks", json={"title": "x", "priority": "zzz", **ACTOR}).status_code
            == 422
        )

    def test_assign_then_complete_flow(self) -> None:
        agent_id, task_id = _hire(), _create()
        assigned = client.post(f"/tasks/{task_id}/assign", json={"agent_id": agent_id, **ACTOR})
        assert assigned.json()["status"] == "in_progress"
        done = client.post(f"/tasks/{task_id}/complete", json={"result": "ok", **DEV})
        assert done.json()["status"] == "done"
        assert done.json()["result"] == "ok"

    def test_unknown_task_is_404_in_both_languages(self) -> None:
        url = f"/tasks/{uuid4()}/complete"
        pt = client.post(url, json={"result": "x", **DEV}, headers={"Accept-Language": "pt-BR"})
        en = client.post(url, json={"result": "x", **DEV}, headers={"Accept-Language": "en"})
        assert pt.status_code == en.status_code == 404
        assert "não foi encontrada" in pt.json()["detail"]
        assert "was not found" in en.json()["detail"]

    def test_unknown_agent_is_404(self) -> None:
        response = client.post(
            f"/tasks/{_create()}/assign", json={"agent_id": str(uuid4()), **ACTOR}
        )
        assert response.status_code == 404

    def test_complete_backlog_task_is_409_localized(self) -> None:
        task_id = _create()
        pt = client.post(
            f"/tasks/{task_id}/complete",
            json={"result": "x", **DEV},
            headers={"Accept-Language": "pt"},
        )
        en = client.post(
            f"/tasks/{task_id}/complete",
            json={"result": "x", **DEV},
            headers={"Accept-Language": "en"},
        )
        assert pt.status_code == en.status_code == 409
        assert "apenas tarefas" in pt.json()["detail"]
        assert "only 'in_progress'" in en.json()["detail"]

    def test_dev_assign_is_403(self) -> None:
        response = client.post(f"/tasks/{_create()}/assign", json={"agent_id": _hire(), **DEV})
        assert response.status_code == 403

    def test_busy_agent_is_409(self) -> None:
        agent_id = _hire()
        client.post(f"/tasks/{_create()}/assign", json={"agent_id": agent_id, **ACTOR})
        response = client.post(
            f"/tasks/{_create('Outra')}/assign", json={"agent_id": agent_id, **ACTOR}
        )
        assert response.status_code == 409


class TestMoveRoute:
    def _move(self, task_id: str, to: str, role: str, lang: str = "en"):  # type: ignore[no-untyped-def]
        return client.post(
            f"/tasks/{task_id}/move",
            json={"to_status": to, "actor_id": ACTOR["actor_id"], "actor_role": role},
            headers={"Accept-Language": lang},
        )

    def test_planner_moves_and_history_is_exposed(self) -> None:
        _hire()
        task_id = _create()
        assert self._move(task_id, "todo", "scrum_master").json()["status"] == "todo"
        history = client.get(f"/tasks/{task_id}/transitions").json()
        assert [h["to_status"] for h in history] == ["backlog", "todo"]
        assert history[-1]["actor_role"] == "scrum_master"

    def test_forbidden_role_is_403_localized(self) -> None:
        task_id = _create()
        pt = self._move(task_id, "todo", "dev_junior", "pt")
        en = self._move(task_id, "todo", "dev_junior", "en")
        assert pt.status_code == en.status_code == 403
        assert "não pode mover" in pt.json()["detail"]
        assert "not allowed to move" in en.json()["detail"]

    def test_invalid_move_is_409_and_unknown_is_404(self) -> None:
        assert self._move(_create(), "done", "product_owner").status_code == 409
        assert self._move(str(uuid4()), "todo", "product_owner").status_code == 404

    def test_unknown_status_is_422(self) -> None:
        assert self._move(_create(), "nope", "product_owner").status_code == 422


class TestOwnerPowers:
    def test_owner_override_moves_to_any_column(self) -> None:
        _hire()
        task_id = _create()
        denied = client.post(f"/tasks/{task_id}/move", json={"to_status": "done", **ACTOR})
        assert denied.status_code == 409
        moved = client.post(
            f"/tasks/{task_id}/move", json={"to_status": "done", "owner_override": True, **ACTOR}
        )
        assert moved.status_code == 200
        assert moved.json()["status"] == "done"

    def test_set_owner_and_priority(self) -> None:
        agent_id, task_id = _hire(), _create()
        owner = client.put(f"/tasks/{task_id}/owner", json={"agent_id": agent_id, **ACTOR})
        assert owner.json()["assigned_to"] == agent_id
        assert owner.json()["status"] == "backlog"
        priority = client.put(f"/tasks/{task_id}/priority", json={"priority": "urgent", **ACTOR})
        assert priority.json()["priority"] == "urgent"

    def test_set_owner_unknown_task_is_404(self) -> None:
        response = client.put(
            f"/tasks/{uuid4()}/priority",
            json={"priority": "low", **ACTOR},
            headers={"Accept-Language": "en"},
        )
        assert response.status_code == 404


def test_delete_task_removes_it_and_404_when_missing() -> None:
    created = client.post("/tasks", json={"title": "Alucinada", "description": "", **ACTOR}).json()
    url = f"/tasks/{created['task_id']}"
    params = {"actor_id": ACTOR["actor_id"], "actor_role": ACTOR["actor_role"]}
    assert client.delete(url, params=params).status_code == 204
    assert client.get("/tasks").json() == []
    assert client.delete(url, params=params).status_code == 404
