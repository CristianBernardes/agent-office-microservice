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

from src.application.agents.hire_agent_use_case import HireAgentInput, HireAgentUseCase
from src.application.artifacts.approve_artifact_use_case import ApproveArtifactUseCase
from src.application.artifacts.review_artifact_use_case import ReviewArtifactUseCase
from src.application.artifacts.write_artifact_use_case import (
    WriteArtifactInput,
    WriteArtifactUseCase,
)
from src.application.chat.chat_use_cases import SendMessageInput, SendMessageUseCase
from src.application.meetings.meeting_use_cases import (
    StartCeremonyInput,
    StartCeremonyUseCase,
)
from src.application.research.research_use_case import ResearchInput, ResearchTopicUseCase
from src.application.tasks.task_use_cases import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskInput,
    CreateTaskUseCase,
)
from src.application.tools.tool_permissions import ToolName, role_can_use_tool
from src.domain.entities.agent import Personality, Role
from src.domain.entities.artifact import Artifact, ArtifactType
from src.domain.entities.chat import ChatMessage, MessageKind
from src.domain.entities.meeting import MeetingKind
from src.domain.entities.task import Priority, Task
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.web_search_adapter import IWebSearchAdapter, WebSearchResult
from src.domain.value_objects.identifiers import (
    AgentId,
    ArtifactId,
    GoalId,
    SessionId,
    TaskId,
)


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
# Apenas as ferramentas com caso de uso real implementado possuem handler
# (artefatos, `web_search` e tarefas) — as demais ferramentas constam em `ToolName` e na tabela de
# permissões (fonte única de verdade com a Fase 3), mas levantam
# `ToolNotImplementedError` até que seus casos de uso sejam implementados.
class ToolRegistry:
    def __init__(
        self,
        write_artifact_use_case: WriteArtifactUseCase,
        review_artifact_use_case: ReviewArtifactUseCase,
        approve_artifact_use_case: ApproveArtifactUseCase,
        web_search_adapter: IWebSearchAdapter,
        create_task_use_case: CreateTaskUseCase,
        assign_task_use_case: AssignTaskUseCase,
        complete_task_use_case: CompleteTaskUseCase,
        send_message_use_case: SendMessageUseCase,
        hire_agent_use_case: HireAgentUseCase | None = None,
        default_llm_model: str = "",
        start_ceremony_use_case: StartCeremonyUseCase | None = None,
        research_use_case: ResearchTopicUseCase | None = None,
    ) -> None:
        self._handlers: dict[ToolName, ToolHandler] = {
            ToolName.WRITE_ARTIFACT: self._make_write_artifact_handler(write_artifact_use_case),
            ToolName.REVIEW_ARTIFACT: self._make_review_artifact_handler(review_artifact_use_case),
            ToolName.APPROVE_ARTIFACT: self._make_approve_artifact_handler(
                approve_artifact_use_case
            ),
            ToolName.WEB_SEARCH: self._make_web_search_handler(web_search_adapter),
            ToolName.CREATE_TASK: self._make_create_task_handler(create_task_use_case),
            ToolName.ASSIGN_TASK: self._make_assign_task_handler(assign_task_use_case),
            ToolName.COMPLETE_TASK: self._make_complete_task_handler(complete_task_use_case),
            ToolName.SEND_MESSAGE: self._make_send_message_handler(send_message_use_case),
        }
        if hire_agent_use_case is not None:
            self._handlers[ToolName.HIRE_AGENT] = self._make_hire_agent_handler(
                hire_agent_use_case, default_llm_model
            )
        if start_ceremony_use_case is not None:
            self._handlers[ToolName.START_CEREMONY] = self._make_start_ceremony_handler(
                start_ceremony_use_case
            )
        if research_use_case is not None:
            self._handlers[ToolName.RESEARCH] = self._make_research_handler(research_use_case)

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
                "tool.permission_denied", role=requester_role.value, tool=tool_name.value
            )

        handler = self._handlers.get(tool_name)
        if handler is None:
            raise ToolNotImplementedError("tool.not_implemented", tool=tool_name.value)

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

    @staticmethod
    def _make_create_task_handler(use_case: CreateTaskUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> Task:
            return await use_case.execute(
                CreateTaskInput(
                    title=str(arguments["title"]),
                    description=str(arguments.get("description", "")),
                    priority=Priority(str(arguments.get("priority", Priority.MEDIUM.value))),
                    creator_id=requester_id,
                    creator_role=requester_role,
                )
            )

        return handler

    @staticmethod
    def _make_assign_task_handler(use_case: AssignTaskUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> Task:
            return await use_case.execute(
                task_id=TaskId(value=UUID(str(arguments["task_id"]))),
                assignee_id=AgentId(value=UUID(str(arguments["agent_id"]))),
                actor_id=requester_id,
                actor_role=requester_role,
            )

        return handler

    @staticmethod
    def _make_complete_task_handler(use_case: CompleteTaskUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> Task:
            return await use_case.execute(
                task_id=TaskId(value=UUID(str(arguments["task_id"]))),
                result=str(arguments["result"]),
                actor_id=requester_id,
                actor_role=requester_role,
            )

        return handler

    @staticmethod
    def _make_send_message_handler(use_case: SendMessageUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> ChatMessage:
            recipient = arguments.get("recipient_id")
            task = arguments.get("task_id")
            return await use_case.execute(
                SendMessageInput(
                    session_id=SessionId(value=UUID(str(arguments["session_id"]))),
                    content=str(arguments["content"]),
                    sender_id=requester_id,
                    recipient_id=AgentId(value=UUID(str(recipient))) if recipient else None,
                    task_id=TaskId(value=UUID(str(task))) if task else None,
                    kind=MessageKind(str(arguments.get("kind", MessageKind.CHAT.value))),
                )
            )

        return handler

    @staticmethod
    def _make_hire_agent_handler(use_case: HireAgentUseCase, default_model: str) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> object:
            return await use_case.execute(
                HireAgentInput(
                    name=str(arguments["name"]),
                    role=Role(str(arguments["role"])),
                    personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
                    llm_model=str(arguments.get("llm_model") or default_model),
                )
            )

        return handler

    @staticmethod
    def _make_start_ceremony_handler(use_case: StartCeremonyUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> object:
            raw_participants = arguments.get("participants") or []
            goal = arguments.get("goal_id")
            return await use_case.execute(
                StartCeremonyInput(
                    kind=MeetingKind(str(arguments["kind"])),
                    title=str(arguments["title"]),
                    organizer_id=requester_id,
                    participants=tuple(
                        AgentId(value=UUID(str(p)))
                        for p in (raw_participants if isinstance(raw_participants, list) else [])
                    ),
                    goal_id=GoalId(value=UUID(str(goal))) if goal else None,
                )
            )

        return handler

    @staticmethod
    def _make_research_handler(use_case: ResearchTopicUseCase) -> ToolHandler:
        async def handler(
            requester_id: AgentId, requester_role: Role, arguments: dict[str, object]
        ) -> object:
            return await use_case.execute(
                ResearchInput(agent_id=requester_id, topic=str(arguments["topic"]))
            )

        return handler
