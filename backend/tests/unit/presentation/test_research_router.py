"""Testes unitários da rota de pesquisa."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.domain.entities.agent import Agent, Personality, Role
from src.domain.interfaces.llm_adapter import ILlmAdapter
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter
from src.infrastructure.search.mock_search_adapter import MockSearchAdapter
from src.presentation.dependencies import (
    get_agent_repository,
    get_artifact_repository,
    get_llm_adapter_resolver,
    get_web_search_adapter,
)
from src.presentation.main import app

pytestmark = pytest.mark.unit


class _Resolver(ILlmAdapterResolver):
    def resolve(self, role: Role) -> ILlmAdapter:
        return MockLlmAdapter()


client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_agent_repository.cache_clear()
    get_artifact_repository.cache_clear()
    app.dependency_overrides[get_web_search_adapter] = lambda: MockSearchAdapter()
    app.dependency_overrides[get_llm_adapter_resolver] = lambda: _Resolver()
    yield
    app.dependency_overrides.clear()


class TestResearchRoute:
    async def test_creates_artifact(self) -> None:
        agent = Agent(
            AgentId.generate(), "Ana", Role.DATA_ANALYST, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m"
        )
        await get_agent_repository().save(agent)

        response = client.post(
            "/research", json={"agent_id": str(agent.agent_id.value), "topic": "Kafka"}
        )

        assert response.status_code == 201
        assert response.json()["path"] == "workspace/research/kafka.md"

    def test_unknown_agent_localized(self) -> None:
        response = client.post(
            "/research",
            json={"agent_id": str(uuid4()), "topic": "x"},
            headers={"Accept-Language": "pt"},
        )
        assert response.status_code == 404
        assert "Agente" in response.json()["detail"]
