"""Testes unitários do ``ToolRegistry``."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from src.application.artifacts.approve_artifact_use_case import ApproveArtifactUseCase
from src.application.artifacts.review_artifact_use_case import ReviewArtifactUseCase
from src.application.artifacts.write_artifact_use_case import WriteArtifactUseCase
from src.application.chat.chat_use_cases import SessionNotFoundError
from src.application.tools.tool_permissions import ToolName
from src.application.tools.tool_registry import (
    ToolNotImplementedError,
    ToolPermissionDeniedError,
    ToolRegistry,
)
from src.domain.entities.agent import Role
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.interfaces.web_search_adapter import WebSearchResult
from src.domain.value_objects.identifiers import AgentId, ArtifactId
from src.infrastructure.filesystem.markdown_artifact_writer import MarkdownArtifactWriter
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_artifact_repository import (
    InMemoryArtifactRepository,
)
from src.infrastructure.search.mock_search_adapter import MockSearchAdapter
from tests.unit.application.tasks.registry_support import task_use_cases

pytestmark = pytest.mark.unit


def _build_registry(tmp_path: Path, search_adapter: MockSearchAdapter) -> ToolRegistry:
    repository = InMemoryArtifactRepository(
        writer=MarkdownArtifactWriter(workspace_root=str(tmp_path))
    )
    message_bus = InMemoryMessageBus()
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
        web_search_adapter=search_adapter,
        **task_use_cases(message_bus),
    )


class TestToolRegistry:
    async def test_executes_write_artifact_for_permitted_role(self, tmp_path: Path) -> None:
        registry = _build_registry(tmp_path, MockSearchAdapter())

        result = await registry.execute(
            tool_name=ToolName.WRITE_ARTIFACT,
            requester_id=AgentId.generate(),
            requester_role=Role.PRODUCT_OWNER,
            arguments={
                "title": "Backlog — Sprint 1",
                "content": "# Backlog",
                "artifact_type": ArtifactType.BACKLOG.value,
                "path": "sprint-1/backlog.md",
            },
        )

        assert isinstance(result, Artifact)

    async def test_denies_approve_artifact_for_dev_junior(self, tmp_path: Path) -> None:
        registry = _build_registry(tmp_path, MockSearchAdapter())

        with pytest.raises(ToolPermissionDeniedError):
            await registry.execute(
                tool_name=ToolName.APPROVE_ARTIFACT,
                requester_id=AgentId.generate(),
                requester_role=Role.DEV_JUNIOR,
                arguments={"artifact_id": str(ArtifactId.generate())},
            )

    async def test_raises_not_implemented_for_tool_without_handler(self, tmp_path: Path) -> None:
        registry = _build_registry(tmp_path, MockSearchAdapter())

        with pytest.raises(ToolNotImplementedError):
            await registry.execute(
                tool_name=ToolName.HIRE_AGENT,
                requester_id=AgentId.generate(),
                requester_role=Role.HR_MANAGER,
                arguments={},
            )

    async def test_executes_web_search_for_permitted_role(self, tmp_path: Path) -> None:
        configured_results = [
            WebSearchResult(
                title="Nicho validado",
                url="https://example.com",
                content="Conteúdo relevante",
                score=0.95,
            )
        ]
        search_adapter = MockSearchAdapter(results=configured_results)
        registry = _build_registry(tmp_path, search_adapter)

        results = await registry.execute(
            tool_name=ToolName.WEB_SEARCH,
            requester_id=AgentId.generate(),
            requester_role=Role.PRODUCT_CONSULTANT,
            arguments={"query": "nicho de SaaS B2C no Brasil"},
        )

        assert results == configured_results
        assert search_adapter.received_queries == ["nicho de SaaS B2C no Brasil"]

    async def test_denies_web_search_for_scrum_master(self, tmp_path: Path) -> None:
        registry = _build_registry(tmp_path, MockSearchAdapter())

        with pytest.raises(ToolPermissionDeniedError):
            await registry.execute(
                tool_name=ToolName.WEB_SEARCH,
                requester_id=AgentId.generate(),
                requester_role=Role.SCRUM_MASTER,
                arguments={"query": "qualquer coisa"},
            )

    async def test_send_message_tool_posts_to_session(self, tmp_path: Path) -> None:
        registry = _build_registry(tmp_path, MockSearchAdapter())
        with pytest.raises(SessionNotFoundError):
            await registry.execute(
                tool_name=ToolName.SEND_MESSAGE,
                requester_id=AgentId.generate(),
                requester_role=Role.PRODUCT_OWNER,
                arguments={"session_id": str(uuid4()), "content": "oi"},
            )
