"""Testes unitários do ``AgentThinkUseCase``."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.application.agents.agent_think_use_case import AgentThinkUseCase
from src.application.artifacts.approve_artifact_use_case import ApproveArtifactUseCase
from src.application.artifacts.review_artifact_use_case import ReviewArtifactUseCase
from src.application.artifacts.write_artifact_use_case import WriteArtifactUseCase
from src.application.tools.tool_registry import ToolRegistry
from src.domain.entities.agent import Agent, AgentStatus, Personality, Role
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.interfaces.llm_adapter import LlmThoughtResponse
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.llm.mock_llm_adapter import MockLlmAdapter
from src.infrastructure.llm.role_based_llm_adapter_resolver import RoleBasedLlmAdapterResolver
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)
from src.infrastructure.prompts.file_prompt_provider import FilePromptProvider
from src.infrastructure.search.mock_search_adapter import MockSearchAdapter
from tests.unit.application.tasks.registry_support import task_use_cases

pytestmark = pytest.mark.unit


@pytest.fixture
def neutral_personality() -> Personality:
    return Personality(0.5, 0.5, 0.5, 0.5, 0.5)


def _resolver_for(adapter: MockLlmAdapter) -> RoleBasedLlmAdapterResolver:
    return RoleBasedLlmAdapterResolver(
        adapter_factory=lambda _model: adapter, default_model="mock-model", role_models={}
    )


def _build_tool_registry(tmp_path: Path, message_bus: InMemoryMessageBus) -> ToolRegistry:
    repository = InMemoryArtifactRepository(
        writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
    )
    return ToolRegistry(
        write_artifact_use_case=WriteArtifactUseCase(
            artifact_repository=repository, message_bus=message_bus
        ),
        review_artifact_use_case=ReviewArtifactUseCase(
            artifact_repository=repository, message_bus=message_bus
        ),
        approve_artifact_use_case=ApproveArtifactUseCase(
            artifact_repository=repository, message_bus=message_bus
        ),
        web_search_adapter=MockSearchAdapter(),
        **task_use_cases(message_bus),
    )


class TestAgentThinkUseCase:
    async def test_moves_agent_to_thinking_status(
        self, tmp_path: Path, neutral_personality: Personality
    ) -> None:
        agent = Agent(
            agent_id=AgentId.generate(),
            name="Alice",
            role=Role.DEV_SENIOR,
            personality=neutral_personality,
            llm_model="mock-model",
        )
        message_bus = InMemoryMessageBus()
        use_case = AgentThinkUseCase(
            llm_adapter_resolver=_resolver_for(MockLlmAdapter()),
            message_bus=message_bus,
            prompt_provider=FilePromptProvider(),
            language=Language.PT,
            tool_registry=_build_tool_registry(tmp_path, message_bus),
        )

        await use_case.execute(agent, context="Contexto de teste.")

        assert agent.status == AgentStatus.THINKING

    async def test_publishes_status_thought_and_action_topics(
        self, tmp_path: Path, neutral_personality: Personality
    ) -> None:
        agent = Agent(
            agent_id=AgentId.generate(),
            name="Bob",
            role=Role.PRODUCT_OWNER,
            personality=neutral_personality,
            llm_model="mock-model",
        )
        message_bus = InMemoryMessageBus()
        use_case = AgentThinkUseCase(
            llm_adapter_resolver=_resolver_for(MockLlmAdapter()),
            message_bus=message_bus,
            prompt_provider=FilePromptProvider(),
            language=Language.PT,
            tool_registry=_build_tool_registry(tmp_path, message_bus),
        )

        await use_case.execute(agent, context="Contexto de teste.")

        status_topic = f"office/agents/{agent.agent_id}/status"
        thought_topic = f"office/agents/{agent.agent_id}/thought"
        action_topic = f"office/agents/{agent.agent_id}/action"

        assert len(message_bus.get_published_messages(status_topic)) == 1
        assert len(message_bus.get_published_messages(thought_topic)) == 1
        assert len(message_bus.get_published_messages(action_topic)) == 1

    async def test_raises_when_agent_is_offline(
        self, tmp_path: Path, neutral_personality: Personality
    ) -> None:
        agent = Agent(
            agent_id=AgentId.generate(),
            name="Carol",
            role=Role.QA_ENGINEER,
            personality=neutral_personality,
            llm_model="mock-model",
        )
        agent.go_offline()
        message_bus = InMemoryMessageBus()
        use_case = AgentThinkUseCase(
            llm_adapter_resolver=_resolver_for(MockLlmAdapter()),
            message_bus=message_bus,
            prompt_provider=FilePromptProvider(),
            language=Language.PT,
            tool_registry=_build_tool_registry(tmp_path, message_bus),
        )

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(agent, context="Contexto de teste.")

    async def test_executes_tool_call_through_tool_registry(
        self, tmp_path: Path, neutral_personality: Personality
    ) -> None:
        agent = Agent(
            agent_id=AgentId.generate(),
            name="Diana",
            role=Role.PRODUCT_OWNER,
            personality=neutral_personality,
            llm_model="mock-model",
        )
        llm_response = LlmThoughtResponse(
            thought="Vou registrar o backlog inicial.",
            action="write_artifact",
            target=None,
            tool_call={
                "tool": "write_artifact",
                "args": {
                    "title": "Backlog — Sprint 1",
                    "content": "# Backlog",
                    "artifact_type": "backlog",
                    "path": "sprint-1/backlog.md",
                },
            },
            raw_response="{}",
        )
        message_bus = InMemoryMessageBus()
        use_case = AgentThinkUseCase(
            llm_adapter_resolver=_resolver_for(MockLlmAdapter(responses=[llm_response])),
            message_bus=message_bus,
            prompt_provider=FilePromptProvider(),
            language=Language.PT,
            tool_registry=_build_tool_registry(tmp_path, message_bus),
        )

        await use_case.execute(agent, context="Contexto de teste.")

        assert (tmp_path / "sprint-1/backlog.md").exists()
