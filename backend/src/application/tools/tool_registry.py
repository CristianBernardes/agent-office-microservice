"""Registro de ferramentas disponíveis para os agentes, com validação de
permissão por papel antes de qualquer execução (ver `ROLE_TOOL_PERMISSIONS`).

Atua como a camada de orquestração entre o resultado de ``AgentThinkUseCase``
(uma ação/ferramenta solicitada pelo LLM) e os casos de uso concretos que de
fato produzem efeito (criar artefato, revisar, aprovar, pesquisar na web) —
nenhum desses casos de uso conhece `Role` ou permissões; essa responsabilidade
fica centralizada apenas aqui (Single Responsibility Principle).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import UUID

from src.application.artifacts.approve_artifact_use_case import ApproveArtifactUseCase
from src.application.artifacts.review_artifact_use_case import ReviewArtifactUseCase
from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.application.tools.tool_permissions import ToolName, role_can_use_tool
from src.domain.entities.agent import Role
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.web_search_adapter import IWebSearchAdapter, WebSearchResult
from src.domain.value_objects.identifiers import AgentId, ArtifactId


# Bloco: erro levantado quando o papel solicitante não tem permissão para a
# ferramenta pedida — nunca executamos a ferramenta "mesmo assim" nem ignoramos
# silenciosamente a solicitação.
class ToolPermissionDeniedError(DomainError):
    """Levantada quando um papel tenta usar uma ferramenta sem permissão."""


# Bloco: erro levantado quando a ferramenta é conhecida (está em `ToolName`),
# mas ainda não tem um handler implementado nesta rodada do projeto — distinto
# de uma permissão negada, para que o chamador saiba diferenciar "você não
# pode" de "isso ainda não existe".
class ToolNotImplementedError(DomainError):
    """Levantada quando a ferramenta solicitada ainda não possui handler implementado."""


# Bloco: assinatura de um handler de ferramenta.
ToolHandler = Callable[[AgentId, Role, dict[str, object]], Awaitable[object]]


# Bloco: registro central de ferramentas.
# Apenas as ferramentas com caso de uso real implementado nesta rodada possuem
# handler (`write_artifact`, `review_artifact`, `approve_artifact`,
# `web_search`) — as demais ferramentas já constam em `ToolName` e na tabela de
# permissões (fonte única de verdade com a Fase 3), mas levantam
# `ToolNotImplementedError` até que seus casos de uso sejam implementados.
class ToolRegistry:
    def __init__(
        self,
        write_artifact_use_case: WriteArtifactUseCase,
        review_artifact_use_case: ReviewArtifactUseCase,
        approve_artifact_use_case: ApproveArtifactUseCase,
        web_search_adapter: IWebSearchAdapter,
    ) -> None:
        self._handlers: dict[ToolName, ToolHandler] = {
            ToolName.WRITE_ARTIFACT: self._make_write_artifact_handler(write_artifact_use_case),
            ToolName.REVIEW_ARTIFACT: self._make_review_artifact_handler(review_artifact_use_case),
            ToolName.APPROVE_ARTIFACT: self._make_approve_artifact_handler(
                approve_artifact_use_case
            ),
            ToolName.WEB_SEARCH: self._make_web_search_handler(web_search_adapter),
        }

    async def execute(
        self,
        tool_name: ToolName,
        requester_id: AgentId,
        requester_role: Role,
        arguments: dict[str, object],
    ) -> object:
        """Valida a permissão do papel e delega à ferramenta correspondente."""
        if not role_can_use_tool(requester_role, tool_name):
            raise ToolPermissionDeniedError(
                f"O papel '{requester_role.value}' não tem permissão para usar a ferramenta "
                f"'{tool_name.value}'."
            )

        handler = self._handlers.get(tool_name)
        if handler is None:
            raise ToolNotImplementedError(
                f"A ferramenta '{tool_name.value}' ainda não possui um handler implementado "
                "nesta rodada do projeto."
            )

        return await handler(requester_id, requester_role, arguments)

    @staticmethod
    def _make_write_artifact_handler(use_case: WriteArtifactUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> Artifact:
            return await use_case.execute(
                WriteArtifactInput(
                    title=str(arguments["title"]),
                    content=str(arguments["content"]),
                    artifact_type=ArtifactType(str(arguments["artifact_type"])),
                    path=str(arguments["path"]),
                    author_id=requester_id,
                    author_role=requester_role,
                )
            )

        return handler

    @staticmethod
    def _make_review_artifact_handler(use_case: ReviewArtifactUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> Artifact:
            return await use_case.execute(
                artifact_id=ArtifactId(value=UUID(str(arguments["artifact_id"]))),
                reviewer_id=requester_id,
                reviewer_role=requester_role,
            )

        return handler

    @staticmethod
    def _make_approve_artifact_handler(use_case: ApproveArtifactUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> Artifact:
            return await use_case.execute(
                artifact_id=ArtifactId(value=UUID(str(arguments["artifact_id"]))),
                approver_id=requester_id,
                approver_role=requester_role,
            )

        return handler

    @staticmethod
    def _make_web_search_handler(adapter: IWebSearchAdapter) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> list[WebSearchResult]:
            raw_max_results = arguments.get("max_results", 5)
            max_results = raw_max_results if isinstance(raw_max_results, int) else 5
            return await adapter.search(query=str(arguments["query"]), max_results=max_results)

        return handler
