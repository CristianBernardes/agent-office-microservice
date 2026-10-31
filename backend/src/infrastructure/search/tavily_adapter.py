"""Implementação do ``IWebSearchAdapter`` para a API da Tavily.

A Tavily é acessada via HTTP simples, sem SDK proprietário, seguindo a mesma
filosofia de integração já usada para o Ollama (ver ADR-005 e ADR-011). A chave
de API é sempre recebida por injeção de dependência (vinda de `.env`), nunca
fixada neste módulo.
"""

from __future__ import annotations

import httpx

from src.domain.interfaces.web_search_adapter import IWebSearchAdapter, WebSearchResult


# Bloco: adaptador de busca web para a Tavily.
class TavilySearchAdapter(IWebSearchAdapter):
    def __init__(
        self,
        api_key: str,
        search_url: str = "https://api.tavily.com/search",
        timeout_seconds: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._search_url = search_url
        self._http_client = httpx.AsyncClient(timeout=timeout_seconds)

    async def search(self, query: str, max_results: int = 5) -> list[WebSearchResult]:
        """Consulta a API da Tavily e retorna os resultados mais relevantes."""
        if not self._api_key:
            # Falha explícita apenas na primeira chamada de busca, nunca na
            # construção do adaptador: outros fluxos que não usam `web_search`
            # não devem ser impactados pela ausência da chave (ver ADR-011).
            raise RuntimeError(
                "TAVILY_API_KEY não configurada. Defina essa variável no seu "
                "'.env' com uma chave obtida em https://app.tavily.com para usar "
                "a ferramenta de busca web."
            )

        http_response = await self._http_client.post(
            self._search_url,
            json={
                "api_key": self._api_key,
                "query": query,
                "max_results": max_results,
            },
        )
        http_response.raise_for_status()

        raw_results = http_response.json().get("results", [])
        return [
            WebSearchResult(
                title=raw_result.get("title", ""),
                url=raw_result.get("url", ""),
                content=raw_result.get("content", ""),
                score=raw_result.get("score", 0.0),
            )
            for raw_result in raw_results
        ]

    async def close(self) -> None:
        """Libera a conexão HTTP subjacente."""
        await self._http_client.aclose()
