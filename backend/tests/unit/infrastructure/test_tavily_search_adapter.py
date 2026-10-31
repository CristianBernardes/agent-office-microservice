"""Testes unitários do ``TavilySearchAdapter``."""

from __future__ import annotations

from unittest.mock import AsyncMock

import httpx
import pytest
from pytest_mock import MockerFixture

from src.infrastructure.search.tavily_adapter import TavilySearchAdapter

pytestmark = pytest.mark.unit


class TestTavilySearchAdapter:
    async def test_raises_when_api_key_is_missing(self) -> None:
        adapter = TavilySearchAdapter(api_key="")

        with pytest.raises(RuntimeError, match="TAVILY_API_KEY"):
            await adapter.search("mercado de nicho SaaS Brasil")

    async def test_search_returns_structured_results(self, mocker: MockerFixture) -> None:
        adapter = TavilySearchAdapter(api_key="fake-key")

        fake_http_response = httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "title": "Mercado de SaaS de nicho no Brasil",
                        "url": "https://example.com/saas-nicho",
                        "content": "Resumo do artigo sobre nichos de SaaS.",
                        "score": 0.92,
                    }
                ]
            },
            request=httpx.Request("POST", "https://api.tavily.com/search"),
        )
        mocker.patch.object(
            adapter._http_client, "post", AsyncMock(return_value=fake_http_response)
        )

        results = await adapter.search("mercado de nicho SaaS Brasil", max_results=1)

        assert len(results) == 1
        assert results[0].title == "Mercado de SaaS de nicho no Brasil"
        assert results[0].url == "https://example.com/saas-nicho"
        assert results[0].score == 0.92

    async def test_search_raises_on_http_error(self, mocker: MockerFixture) -> None:
        adapter = TavilySearchAdapter(api_key="fake-key")

        failing_response = httpx.Response(
            status_code=401,
            request=httpx.Request("POST", "https://api.tavily.com/search"),
        )
        mocker.patch.object(adapter._http_client, "post", AsyncMock(return_value=failing_response))

        with pytest.raises(httpx.HTTPStatusError):
            await adapter.search("qualquer consulta")

    async def test_close_closes_http_client(self) -> None:
        adapter = TavilySearchAdapter(api_key="k")
        await adapter.close()
        assert adapter._http_client.is_closed
