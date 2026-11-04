"""Testes unitários da listagem de modelos de LLM."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from src.infrastructure.config.settings import get_settings
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


class TestAnthropicModelsInList:
    @pytest.fixture
    def anthropic_configured(self, monkeypatch: pytest.MonkeyPatch) -> Any:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
        get_settings.cache_clear()
        yield
        monkeypatch.undo()
        get_settings.cache_clear()

    def test_claude_models_are_merged_when_key_is_configured(
        self, anthropic_configured: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if "anthropic.com" in str(request.url):
                return httpx.Response(200, json={"data": [{"id": "claude-sonnet-4-5-20250929"}]})
            return httpx.Response(200, json={"models": [{"name": "a:latest"}]})

        _patch_transport(monkeypatch, httpx.MockTransport(handler))
        assert client.get("/models").json() == ["a:latest", "claude-sonnet-4-5-20250929"]

    def test_claude_models_are_absent_without_api_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Força a ausência da chave mesmo que o `.env` local do desenvolvedor tenha uma
        # configurada, para que este teste não dependa do ambiente de quem o executa.
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        get_settings.cache_clear()

        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(str(request.url))
            return httpx.Response(200, json={"models": [{"name": "a:latest"}]})

        _patch_transport(monkeypatch, httpx.MockTransport(handler))
        try:
            assert client.get("/models").json() == ["a:latest"]
            assert not any("anthropic.com" in url for url in calls)
        finally:
            get_settings.cache_clear()

    def test_anthropic_down_falls_back_to_ollama_models(
        self, anthropic_configured: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if "anthropic.com" in str(request.url):
                raise httpx.ConnectError("down")
            return httpx.Response(200, json={"models": [{"name": "a:latest"}]})

        _patch_transport(monkeypatch, httpx.MockTransport(handler))
        assert client.get("/models").json() == ["a:latest"]
