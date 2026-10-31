"""Testes unitários das rotas de memória (pt/en)."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.presentation.dependencies import get_agent_repository, get_memory_repository
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_memory_repository.cache_clear()
    get_agent_repository.cache_clear()
    yield


def _hire() -> str:
    return client.post(
        "/agents", json={"name": "Ana", "role": "dev_senior", "llm_model": "m"}
    ).json()["agent_id"]


class TestMemoryRoutes:
    def test_remember_list_recall(self) -> None:
        agent = _hire()
        created = client.post(f"/agents/{agent}/memories", json={"content": "preço é 39,90"})
        assert created.status_code == 201
        assert client.get(f"/agents/{agent}/memories").json()[0]["content"] == "preço é 39,90"
        # O LLM real só existe com Ollama; aqui basta validar o 404 e a validação.

    def test_validation(self) -> None:
        agent = _hire()
        assert client.post(f"/agents/{agent}/memories", json={"content": ""}).status_code == 422
        bad = {"content": "x", "importance": 2}
        assert client.post(f"/agents/{agent}/memories", json=bad).status_code == 422
        assert (
            client.post(
                f"/agents/{agent}/memories/recall", json={"query": "x", "limit": 0}
            ).status_code
            == 422
        )

    def test_unknown_agent_is_404_in_both_languages(self) -> None:
        url = f"/agents/{uuid4()}/memories"
        pt = client.post(url, json={"content": "x"}, headers={"Accept-Language": "pt-BR"})
        en = client.post(url, json={"content": "x"}, headers={"Accept-Language": "en"})
        assert pt.status_code == en.status_code == 404
        assert pt.json()["detail"] != en.json()["detail"]
        assert client.post(f"{url}/recall", json={"query": "x"}).status_code == 404
