"""Testes unitários das rotas HTTP da camada de apresentação.

Usa o ``TestClient`` do FastAPI (síncrono, mas adequado para testar rotas sem
subir um servidor real). A injeção de dependência padrão do bootstrap da
aplicação é usada tal como está — o repositório em memória garante que o teste
não dependa de nenhum serviço externo.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.application.agents.agent_think_use_case import AgentThinkUseCase
from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.domain.localization.language import Language
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter
from src.infrastructure.llm.role_based_llm_adapter_resolver import RoleBasedLlmAdapterResolver
from src.presentation.dependencies import (
    get_agent_repository,
    get_dispatch_goal_use_case,
    get_message_bus,
    get_prompt_provider,
    get_tool_registry,
)
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


class TestHealthRoute:
    def test_health_check_returns_ok_status(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAgentsRoutes:
    def test_list_agents_returns_hired_agents(self) -> None:
        get_agent_repository.cache_clear()
        assert client.get("/agents").json() == []
        client.post("/agents", json={"name": "Ana", "role": "dev_senior", "llm_model": "m"})
        listed = client.get("/agents").json()
        assert [a["name"] for a in listed] == ["Ana"]

    def test_cors_allows_configured_origin_and_blocks_others(self) -> None:
        allowed = client.get("/health", headers={"Origin": "http://localhost:5173"})
        blocked = client.get("/health", headers={"Origin": "http://evil.example"})
        assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert "access-control-allow-origin" not in blocked.headers
    def test_hire_agent_returns_created_agent(self) -> None:
        response = client.post(
            "/agents",
            json={
                "name": "Alice",
                "role": "dev_senior",
                "llm_model": "mock-model",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Alice"
        assert body["status"] == "idle"

    def test_fire_unknown_agent_returns_not_found(self) -> None:
        unknown_agent_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/agents/{unknown_agent_id}/fire")
        assert response.status_code == 404


class TestAgentsRoutesLanguage:
    _UNKNOWN = "/agents/00000000-0000-0000-0000-000000000000/fire"

    def test_not_found_in_portuguese_with_accept_language(self) -> None:
        response = client.post(self._UNKNOWN, headers={"Accept-Language": "pt-BR"})
        assert "não foi encontrado" in response.json()["detail"]

    def test_not_found_in_english_with_accept_language(self) -> None:
        response = client.post(self._UNKNOWN, headers={"Accept-Language": "en-US"})
        assert "was not found" in response.json()["detail"]


class TestDispatchGoalRoute:
    def _hire(self) -> str:
        body = {"name": "Olivia", "role": "product_owner", "llm_model": "mock-model"}
        return str(client.post("/agents", json=body).json()["agent_id"])

    @pytest.fixture(autouse=True)
    def _mock_llm(self) -> Iterator[None]:
        resolver = RoleBasedLlmAdapterResolver(
            adapter_factory=lambda _model: MockLlmAdapter(),
            default_model="mock-model",
            role_models={},
        )

        def build_use_case() -> DispatchGoalUseCase:
            think = AgentThinkUseCase(
                llm_adapter_resolver=resolver,
                message_bus=get_message_bus(),
                prompt_provider=get_prompt_provider(),
                tool_registry=get_tool_registry(),
                language=Language.EN,
            )
            return DispatchGoalUseCase(get_agent_repository(), think, get_message_bus())

        app.dependency_overrides[get_dispatch_goal_use_case] = build_use_case
        yield
        app.dependency_overrides.clear()

    def test_think_returns_agent_decision(self) -> None:
        agent_id = self._hire()
        response = client.post(f"/agents/{agent_id}/think", json={"context": "Build a todo app"})
        assert response.status_code == 200
        assert response.json()["action"] == "idle"

    def test_think_unknown_agent_returns_404_localized(self) -> None:
        response = client.post(
            "/agents/00000000-0000-0000-0000-000000000000/think",
            json={"context": "x"},
            headers={"Accept-Language": "pt-BR"},
        )
        assert response.status_code == 404
        assert "não foi encontrado" in response.json()["detail"]

    def test_think_offline_agent_returns_409(self) -> None:
        agent_id = self._hire()
        client.post(f"/agents/{agent_id}/fire")
        response = client.post(f"/agents/{agent_id}/think", json={"context": "x"})
        assert response.status_code == 409
        assert "OFFLINE" in response.json()["detail"]

    def test_think_rejects_empty_context(self) -> None:
        agent_id = self._hire()
        response = client.post(f"/agents/{agent_id}/think", json={"context": ""})
        assert response.status_code == 422
