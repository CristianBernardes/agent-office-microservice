"""Contrato (porta) para adaptadores de busca web.

Qualquer provedor de busca (Tavily, ou um mock de testes) deve implementar esta
interface para ser utilizável pela ferramenta ``web_search`` e pelos casos de uso
que dela dependem, sem que a camada de aplicação precise conhecer detalhes do
provedor concreto (ver ADR-011).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# Bloco: um único resultado de busca web, já estruturado.
# Deliberadamente simples — apenas os campos que os agentes efetivamente
# consomem para raciocinar, sem replicar toda a riqueza de metadados que a API
# de um provedor específico possa oferecer (princípio YAGNI).
@dataclass(frozen=True, slots=True)
class WebSearchResult:
    title: str
    url: str
    content: str
    score: float


# Bloco: contrato único para qualquer provedor de busca web.
class IWebSearchAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[WebSearchResult]:
        """Executa uma busca web e retorna os resultados mais relevantes."""
