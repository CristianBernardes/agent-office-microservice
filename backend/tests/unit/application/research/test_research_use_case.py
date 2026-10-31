"""Testes unitários da pesquisa de agentes (ADR-034)."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.artifacts.write_artifact_use_case import WriteArtifactUseCase
from src.application.research.research_use_case import (
    ResearchInput,
    ResearchTopicUseCase,
    slugify,
)
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.interfaces.llm_adapter import ILlmAdapter
from src.domain.interfaces.llm_adapter_resolver import ILlmAdapterResolver
from src.domain.interfaces.web_search_adapter import IWebSearchAdapter, WebSearchResult
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)
from src.infrastructure.search.mock_search_adapter import MockSearchAdapter

pytestmark = pytest.mark.unit


class _Resolver(ILlmAdapterResolver):
    def __init__(self) -> None:
        self.llm = MockLlmAdapter()

    def resolve(self, role: Role) -> ILlmAdapter:
        return self.llm


class _BrokenSearch(IWebSearchAdapter):
    async def search(self, query: str, max_results: int = 5) -> list[WebSearchResult]:
        raise ConnectionError("offline")


async def _build(search: IWebSearchAdapter, language: Language = Language.EN):
    agents = InMemoryAgentRepository()
    agent = Agent(
        AgentId.generate(), "Ana", Role.DATA_ANALYST, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m"
    )
    await agents.save(agent)
    artifacts = InMemoryArtifactRepository()
    write = WriteArtifactUseCase(artifacts, InMemoryMessageBus())
    use_case = ResearchTopicUseCase(agents, _Resolver(), search, write, language)
    return use_case, agent


class TestResearch:
    async def test_writes_artifact_with_sources(self) -> None:
        search = MockSearchAdapter([WebSearchResult("Doc", "https://x.io", "texto", 1.0)])
        use_case, agent = await _build(search)

        artifact = await use_case.execute(ResearchInput(agent.agent_id, "Clean Architecture"))

        assert artifact.path == "workspace/research/clean-architecture.md"
        assert "[Doc](https://x.io)" in artifact.content
        assert "## Sources" in artifact.content
        assert search.received_queries == ["Clean Architecture"]

    async def test_portuguese_footer(self) -> None:
        search = MockSearchAdapter([WebSearchResult("Doc", "https://x.io", "t", 1.0)])
        use_case, agent = await _build(search, Language.PT)

        artifact = await use_case.execute(ResearchInput(agent.agent_id, "Tema"))

        assert "## Fontes" in artifact.content

    async def test_search_failure_still_writes_report(self) -> None:
        use_case, agent = await _build(_BrokenSearch())

        artifact = await use_case.execute(ResearchInput(agent.agent_id, "Tema"))

        assert "## Sources" not in artifact.content

    async def test_unknown_agent(self) -> None:
        use_case, _ = await _build(MockSearchAdapter())
        with pytest.raises(AgentNotFoundError):
            await use_case.execute(ResearchInput(AgentId.generate(), "x"))

    def test_slugify(self) -> None:
        assert slugify("Olá, Mundo! Açaí") == "ola-mundo-acai"
        assert slugify("!!!") == "research"
