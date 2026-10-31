"""Pesquisa de um tema por um agente, gerando um artefato Markdown (ADR-034)."""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver
from src.domain.interfaces.web_search_adapter import IWebSearchAdapter, WebSearchResult
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId

logger = logging.getLogger(__name__)

_LABELS = {
    Language.PT: {
        "system": "Você é um pesquisador. Escreva um relatório em Markdown, em português, "
        "claro e objetivo, com título, resumo e conclusões. Responda SOMENTE com JSON no formato "
        '{"thought": "<relatório em Markdown>", "action": "idle"}.',
        "topic": "Tema",
        "sources": "Fontes encontradas",
        "no_sources": "Nenhuma fonte web disponível; use apenas o seu conhecimento.",
        "footer": "Fontes",
    },
    Language.EN: {
        "system": "You are a researcher. Write a clear, objective Markdown report in English "
        "with a title, summary and conclusions. Answer ONLY with JSON in the format "
        '{"thought": "<Markdown report>", "action": "idle"}.',
        "topic": "Topic",
        "sources": "Sources found",
        "no_sources": "No web sources available; rely only on your own knowledge.",
        "footer": "Sources",
    },
}


@dataclass(frozen=True, slots=True)
class ResearchInput:
    agent_id: AgentId
    topic: str
    max_results: int = 5


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:60] or "research"


class ResearchTopicUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        llm_resolver: ILlmAdapterResolver,
        web_search: IWebSearchAdapter,
        write_artifact: WriteArtifactUseCase,
        language: Language,
    ) -> None:
        self._agents = agent_repository
        self._llm = llm_resolver
        self._search = web_search
        self._write = write_artifact
        self._labels = _LABELS[language]

    async def execute(self, data: ResearchInput) -> Artifact:
        agent = await self._agents.find_by_id(data.agent_id)
        if agent is None:
            raise AgentNotFoundError("agent.not_found", agent_id=data.agent_id)
        results = await self._safe_search(data)
        response = await self._llm.resolve(agent.role).think(
            self._labels["system"], self._context(data.topic, results)
        )
        content = (response.thought or response.raw_response).rstrip() + self._footer(results)
        return await self._write.execute(
            WriteArtifactInput(
                title=data.topic,
                content=content,
                artifact_type=ArtifactType.ANALYSIS,
                path=f"workspace/research/{slugify(data.topic)}.md",
                author_id=agent.agent_id,
                author_role=agent.role,
            )
        )

    async def _safe_search(self, data: ResearchInput) -> list[WebSearchResult]:
        try:
            return await self._search.search(data.topic, data.max_results)
        except Exception:
            # Bloco: sem busca (chave ausente, rede fora) o relatório segue só com o modelo.
            logger.exception("Falha na busca web sobre '%s'", data.topic)
            return []

    def _context(self, topic: str, results: list[WebSearchResult]) -> str:
        if not results:
            return f"{self._labels['topic']}: {topic}\n\n{self._labels['no_sources']}"
        sources = "\n".join(f"- {r.title} ({r.url}): {r.content}" for r in results)
        return f"{self._labels['topic']}: {topic}\n\n{self._labels['sources']}:\n{sources}"

    def _footer(self, results: list[WebSearchResult]) -> str:
        if not results:
            return ""
        links = "\n".join(f"- [{r.title}]({r.url})" for r in results)
        return f"\n\n## {self._labels['footer']}\n{links}\n"
