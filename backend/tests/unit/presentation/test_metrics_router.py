"""Testes unitários do endpoint /metrics (ADR-052)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.presentation.dependencies import get_agent_repository, get_task_repository
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean() -> Iterator[None]:
    get_agent_repository.cache_clear()
    get_task_repository.cache_clear()
    yield


class TestMetrics:
    def test_exposes_prometheus_format(self) -> None:
        client.get("/health")
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert 'office_http_requests_total{method="GET",route="/health"' in response.text

    def test_agents_gauge_reflects_hired_agents(self) -> None:
        client.post("/agents", json={"name": "Ana", "role": "dev_senior", "llm_model": "m"})
        body = client.get("/metrics").text
        assert 'office_agents{role="dev_senior"} 1.0' in body
