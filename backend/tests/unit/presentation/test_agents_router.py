"""Testes unitários das rotas HTTP da camada de apresentação.

Usa o ``TestClient`` do FastAPI (síncrono, mas adequado para testar rotas sem
subir um servidor real). A injeção de dependência padrão do bootstrap da
aplicação é usada tal como está — o repositório em memória garante que o teste
não dependa de nenhum serviço externo.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


class TestHealthRoute:
    def test_health_check_returns_ok_status(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAgentsRoutes:
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
