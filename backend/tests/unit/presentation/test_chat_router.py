"""Testes unitários das rotas de objetivos e chat, com erros localizados pt/en."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.presentation.dependencies import get_agent_repository, get_chat_repository
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_chat_repository.cache_clear()
    get_agent_repository.cache_clear()
    yield


class TestChatRoutes:
    def test_goal_creates_session_and_lists(self) -> None:
        response = client.post("/goals", json={"text": "Vender produto digital"})
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "open"
        assert [g["goal_id"] for g in client.get("/goals").json()] == [body["goal_id"]]

    def test_goal_rejects_empty_text(self) -> None:
        assert client.post("/goals", json={"text": ""}).status_code == 422

    def test_goal_unknown_session_is_404_in_both_languages(self) -> None:
        body = {"text": "x", "session_id": str(uuid4())}
        pt = client.post("/goals", json=body, headers={"Accept-Language": "pt-BR"})
        en = client.post("/goals", json=body, headers={"Accept-Language": "en"})
        assert pt.status_code == en.status_code == 404
        assert pt.json()["detail"] != en.json()["detail"]

    def test_message_flow_and_ordering(self) -> None:
        sid = client.post("/goals", json={"text": "meta"}).json()["session_id"]
        agent = client.post(
            "/agents", json={"name": "Ana", "role": "dev_senior", "llm_model": "m"}
        ).json()["agent_id"]
        sent = client.post(
            "/messages", json={"session_id": sid, "content": "olá", "sender_id": agent}
        )
        assert sent.status_code == 201
        messages = client.get(f"/sessions/{sid}/messages").json()
        assert [m["content"] for m in messages] == ["meta", "olá"]
        assert messages[0]["sender_id"] is None

    def test_message_validation_and_unknown_entities(self) -> None:
        sid = client.post("/goals", json={"text": "meta"}).json()["session_id"]
        assert client.post("/messages", json={"session_id": sid, "content": ""}).status_code == 422
        unknown_agent = {"session_id": sid, "content": "x", "sender_id": str(uuid4())}
        assert client.post("/messages", json=unknown_agent).status_code == 404
        unknown_session = {"session_id": str(uuid4()), "content": "x"}
        assert client.post("/messages", json=unknown_session).status_code == 404

    def test_list_messages_unknown_session_and_bad_limit(self) -> None:
        assert client.get(f"/sessions/{uuid4()}/messages").status_code == 404
        assert client.get(f"/sessions/{uuid4()}/messages?limit=0").status_code == 422
