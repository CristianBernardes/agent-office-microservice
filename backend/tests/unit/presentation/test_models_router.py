"""Testes unitários da listagem de modelos de LLM."""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from src.presentation.api import models_router
from src.presentation.main import app

pytestmark = pytest.mark.unit

client = TestClient(app)


def _patch_transport(monkeypatch: pytest.MonkeyPatch, handler: httpx.MockTransport) -> None:
    real = httpx.AsyncClient
    monkeypatch.setattr(
        models_router.httpx,
        "AsyncClient",
        lambda **kwargs: real(transport=handler, **kwargs),
    )


class TestModelsRoute:
    def test_lists_sorted_models(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {
            "models": [
                {"name": "b:latest"},
                {"name": "nomic-embed-text:latest"},
                {"name": "a:latest"},
            ]
        }
        _patch_transport(
            monkeypatch, httpx.MockTransport(lambda r: httpx.Response(200, json=payload))
        )
        assert client.get("/models").json() == ["a:latest", "b:latest"]

    def test_provider_down_returns_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def boom(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("down")

        _patch_transport(monkeypatch, httpx.MockTransport(boom))
        assert client.get("/models").json() == []
