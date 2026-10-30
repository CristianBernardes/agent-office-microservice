"""Testes unitários do ``MockSearchAdapter``."""

from __future__ import annotations

import pytest

from src.domain.interfaces.web_search_adapter import WebSearchResult
from src.infrastructure.search.mock_search_adapter import MockSearchAdapter

pytestmark = pytest.mark.unit


class TestMockSearchAdapter:
    async def test_returns_empty_list_when_no_results_configured(self) -> None:
        adapter = MockSearchAdapter()
        results = await adapter.search("qualquer consulta")
        assert results == []

    async def test_returns_configured_results_up_to_max_results(self) -> None:
        configured_results = [
            WebSearchResult(title="A", url="https://a.example", content="conteúdo a", score=0.9),
            WebSearchResult(title="B", url="https://b.example", content="conteúdo b", score=0.8),
        ]
        adapter = MockSearchAdapter(results=configured_results)

        results = await adapter.search("consulta qualquer", max_results=1)

        assert results == [configured_results[0]]

    async def test_records_received_queries(self) -> None:
        adapter = MockSearchAdapter()
        await adapter.search("primeira consulta")
        await adapter.search("segunda consulta")

        assert adapter.received_queries == ["primeira consulta", "segunda consulta"]
