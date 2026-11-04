"""Testes do roteamento de provedor na factory de resolução de LLM (ADR-058)."""

from __future__ import annotations

from typing import Any

import pytest

from src.domain.entities.agent import Role
from src.infrastructure.config.settings import get_settings
from src.presentation import dependencies as deps

pytestmark = pytest.mark.unit


@pytest.fixture
def claude_tech_lead(monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setenv("AGENT_TECH_LEAD_MODEL", "claude-sonnet-4-5-20250929")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    get_settings.cache_clear()
    deps.get_llm_adapter_resolver.cache_clear()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()
    deps.get_llm_adapter_resolver.cache_clear()


def test_claude_model_resolves_to_anthropic_adapter(claude_tech_lead: Any) -> None:
    resolver = deps.get_llm_adapter_resolver()
    adapter = resolver.resolve(Role.TECH_LEAD)
    assert type(adapter).__name__ == "AnthropicAdapter"
    assert adapter.model_name == "claude-sonnet-4-5-20250929"


def test_default_model_still_resolves_to_ollama_adapter(claude_tech_lead: Any) -> None:
    resolver = deps.get_llm_adapter_resolver()
    adapter = resolver.resolve(Role.PRODUCT_OWNER)
    assert type(adapter).__name__ == "OllamaAdapter"
