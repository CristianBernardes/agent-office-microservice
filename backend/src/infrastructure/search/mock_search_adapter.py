"""Implementação mock do ``IWebSearchAdapter``, usada em testes.

Segue exatamente o mesmo padrão do ``MockLlmAdapter``: permite injetar
resultados pré-definidos para validar o comportamento dos casos de uso sem
depender de qualquer chamada de rede real à Tavily (ver ADR-011).
"""

from __future__ import annotations

from src.domain.interfaces.web_search_adapter import IWebSearchAdapter, WebSearchResult


# Bloco: adaptador de busca web mock.
# Se nenhum resultado pré-definido for fornecido, retorna uma lista vazia — uma
# busca "sem resultados" é um cenário legítimo e não deve ser mascarado com
# dados artificiais.
class MockSearchAdapter(IWebSearchAdapter):
    def __init__(self, results: list[WebSearchResult] | None = None) -> None:
        self._results = results or []
        self.received_queries: list[str] = []

    async def search(self, query: str, max_results: int = 5) -> list[WebSearchResult]:
        """Registra a consulta recebida e retorna os resultados pré-configurados."""
        self.received_queries.append(query)
        return self._results[:max_results]
