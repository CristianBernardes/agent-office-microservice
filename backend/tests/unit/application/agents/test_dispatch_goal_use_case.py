"""Testes unitários do ``DispatchGoalUseCase``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.application.agents.agent_think_use_case import AgentThinkUseCase
from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.artifacts.approve_artifact_use_case import ApproveArtifactUseCase
from src.application.artifacts.review_artifact_use_case import ReviewArtifactUseCase
from src.application.artifacts.write_artifact_use_case import WriteArtifactUseCase
from src.application.tools.tool_registry import ToolRegistry
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.interfaces.llm_adapter import ILlmAdapter, LlmThoughtResponse
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter
from src.infrastructure.llm.role_based_llm_adapter_resolver import RoleBasedLlmAdapterResolver
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)
from src.infrastructure.prompts.file_prompt_provider import FilePromptProvider
from src.infrastructure.search.mock_search_adapter import MockSearchAdapter
from tests.unit.application.tasks.registry_support import task_use_cases

pytestmark = pytest.mark.unit


class _FailingLlmAdapter(MockLlmAdapter):
    async def think(
        self, system_prompt: str, context: str, temperature: float = 0.7
    ) -> LlmThoughtResponse:
        raise ConnectionError("llm down")


def _build(
    tmp_path: Path, adapter: ILlmAdapter
) -> tuple[DispatchGoalUseCase, InMemoryAgentRepository, InMemoryMessageBus]:
    bus = InMemoryMessageBus()
    artifacts = InMemoryArtifactRepository(
        writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
    )
    registry = ToolRegistry(
        write_artifact_use_case=WriteArtifactUseCase(
            artifact_repository=artifacts, message_bus=bus
        ),
        review_artifact_use_case=ReviewArtifactUseCase(
            artifact_repository=artifacts, message_bus=bus
        ),
        approve_artifact_use_case=ApproveArtifactUseCase(
            artifact_repository=artifacts, message_bus=bus
        ),
        web_search_adapter=MockSearchAdapter(),
        **task_use_cases(bus),
    )
    think = AgentThinkUseCase(
        llm_adapter_resolver=RoleBasedLlmAdapterResolver(
            adapter_factory=lambda _model: adapter, default_model="m", role_models={}
        ),
        message_bus=bus,
        prompt_provider=FilePromptProvider(),
        tool_registry=registry,
        language=Language.EN,
    )
    repository = InMemoryAgentRepository()
    return DispatchGoalUseCase(repository, think, bus), repository, bus


async def _saved_agent(repository: InMemoryAgentRepository) -> Agent:
    agent = Agent(
        agent_id=AgentId.generate(),
        name="Olivia",
        role=Role.PRODUCT_OWNER,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="m",
    )
    await repository.save(agent)
    return agent


class TestDispatchGoalUseCase:
    async def test_returns_decision_and_goes_back_to_idle(self, tmp_path: Path) -> None:
        use_case, repository, bus = _build(tmp_path, MockLlmAdapter())
        agent = await _saved_agent(repository)

        response = await use_case.execute(agent.agent_id, "Build a todo app")

        assert response.action == "idle"
        stored = await repository.find_by_id(agent.agent_id)
        assert stored is not None and stored.status == AgentStatus.IDLE
        statuses = bus.get_published_messages(f"office/agents/{agent.agent_id}/status")
        assert len(statuses) == 2

    async def test_unknown_agent_raises_not_found(self, tmp_path: Path) -> None:
        use_case, _, _ = _build(tmp_path, MockLlmAdapter())
        with pytest.raises(AgentNotFoundError):
            await use_case.execute(AgentId.generate(), "goal")

    async def test_offline_agent_is_rejected_and_stays_offline(self, tmp_path: Path) -> None:
        use_case, repository, _ = _build(tmp_path, MockLlmAdapter())
        agent = await _saved_agent(repository)
        agent.go_offline()
        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(agent.agent_id, "goal")
        assert agent.status == AgentStatus.OFFLINE

    async def test_llm_failure_does_not_leave_agent_thinking(self, tmp_path: Path) -> None:
        use_case, repository, _ = _build(tmp_path, _FailingLlmAdapter())
        agent = await _saved_agent(repository)
        with pytest.raises(ConnectionError):
            await use_case.execute(agent.agent_id, "goal")
        assert agent.status == AgentStatus.IDLE
