"""Testes do roteamento de provedor por nome de modelo (ADR-058)."""

import pytest

from src.infrastructure.llm.provider_resolution import is_anthropic_model

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "model",
    ["claude-sonnet-4-5-20250929", "claude-opus-4", "claude-haiku-3-5"],
)
def test_claude_models_are_routed_to_anthropic(model: str) -> None:
    assert is_anthropic_model(model) is True


@pytest.mark.parametrize(
    "model",
    ["qwen3.6:latest", "gpt-oss:20b", "nemotron-3.5-bolt:latest", ""],
)
def test_non_claude_models_are_not_routed_to_anthropic(model: str) -> None:
    assert is_anthropic_model(model) is False
