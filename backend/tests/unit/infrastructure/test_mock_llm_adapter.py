"""Testes unitários do ``MockLlmAdapter``."""

from __future__ import annotations

import pytest

from src.domain.interfaces.llm_adapter import LlmThoughtResponse
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter

pytestmark = pytest.mark.unit


class TestMockLlmAdapter:
    async def test_returns_default_response_when_none_configured(self) -> None:
        adapter = MockLlmAdapter()
        response = await adapter.think(system_prompt="system", context="context")
        assert response.action == "idle"

    async def test_returns_configured_responses_in_order(self) -> None:
        first_response = LlmThoughtResponse(
            thought="primeiro",
            action="write_artifact",
            target=None,
            tool_call=None,
            raw_response="{}",
        )
        adapter = MockLlmAdapter(responses=[first_response])

        response = await adapter.think(system_prompt="system", context="context")

        assert response.thought == "primeiro"
        assert response.action == "write_artifact"

    async def test_embed_returns_deterministic_vector_for_same_text(self) -> None:
        adapter = MockLlmAdapter()
        first_embedding = await adapter.embed("mesmo texto")
        second_embedding = await adapter.embed("mesmo texto")
        assert first_embedding.vector == second_embedding.vector
