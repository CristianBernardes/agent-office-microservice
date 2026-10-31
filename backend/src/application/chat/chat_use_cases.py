"""Casos de uso do chat: enviar objetivo e enviar mensagem (ver ADR-019)."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.common.message_envelope import build_message_envelope
from src.domain.entities.chat import ChatMessage, Goal, MessageKind, Session
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.chat_repository import IChatRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.value_objects.identifiers import AgentId, GoalId, MessageId, SessionId, TaskId

_GOAL_CREATED_TOPIC = "office/goals/created"
_CHAT_MESSAGE_TOPIC = "office/chat/message"
_USER_ROLE = "user"


# Bloco: erro levantado quando a sessão informada não existe.
class SessionNotFoundError(DomainError):
    """Levantada quando a sessão de chat não é encontrada."""


# Bloco: publicação compartilhada do evento de mensagem (DRY).
async def _publish_message(bus: IMessageBus, message: ChatMessage, sender_role: str) -> None:
    envelope = build_message_envelope(
        agent_id=str(message.sender_id) if message.sender_id else _USER_ROLE,
        agent_role=sender_role,
        payload={
            "message_id": str(message.message_id),
            "session_id": str(message.session_id),
            "recipient_id": str(message.recipient_id) if message.recipient_id else None,
            "task_id": str(message.task_id) if message.task_id else None,
            "kind": message.kind.value,
            "content": message.content,
        },
    )
    await bus.publish(_CHAT_MESSAGE_TOPIC, envelope, qos=1)


# Bloco: entrada do envio de objetivo pelo usuário.
@dataclass(frozen=True, slots=True)
class SubmitGoalInput:
    text: str
    session_id: SessionId | None = None


# Bloco: o usuário entrega um objetivo; os agentes o consomem via MQTT.
class SubmitGoalUseCase:
    def __init__(self, chat_repository: IChatRepository, message_bus: IMessageBus) -> None:
        self._chat = chat_repository
        self._bus = message_bus

    async def execute(self, data: SubmitGoalInput) -> Goal:
        session = await self._resolve_session(data.session_id)
        goal = Goal(GoalId.generate(), session.session_id, data.text)
        await self._chat.save_goal(goal)
        message = ChatMessage(MessageId.generate(), session.session_id, data.text)
        await self._chat.add_message(message)
        await self._bus.publish(
            _GOAL_CREATED_TOPIC,
            build_message_envelope(
                agent_id=_USER_ROLE,
                agent_role=_USER_ROLE,
                payload={
                    "goal_id": str(goal.goal_id),
                    "session_id": str(goal.session_id),
                    "text": goal.text,
                },
            ),
            qos=1,
        )
        await _publish_message(self._bus, message, _USER_ROLE)
        return goal

    async def _resolve_session(self, session_id: SessionId | None) -> Session:
        if session_id is None:
            session = Session(SessionId.generate())
            await self._chat.save_session(session)
            return session
        existing = await self._chat.find_session(session_id)
        if existing is None:
            raise SessionNotFoundError("chat.session_not_found", session_id=session_id)
        return existing


# Bloco: entrada do envio de mensagem (``sender_id`` nulo = usuário).
@dataclass(frozen=True, slots=True)
class SendMessageInput:
    session_id: SessionId
    content: str
    sender_id: AgentId | None = None
    recipient_id: AgentId | None = None
    task_id: TaskId | None = None
    kind: MessageKind = MessageKind.CHAT


# Bloco: envio de mensagem de chat por usuário ou agente.
class SendMessageUseCase:
    def __init__(
        self,
        chat_repository: IChatRepository,
        agent_repository: IAgentRepository,
        message_bus: IMessageBus,
    ) -> None:
        self._chat = chat_repository
        self._agents = agent_repository
        self._bus = message_bus

    async def execute(self, data: SendMessageInput) -> ChatMessage:
        if await self._chat.find_session(data.session_id) is None:
            raise SessionNotFoundError("chat.session_not_found", session_id=data.session_id)
        sender_role = await self._role_of(data.sender_id)
        if data.recipient_id is not None:
            await self._role_of(data.recipient_id)
        message = ChatMessage(
            MessageId.generate(),
            data.session_id,
            data.content,
            data.sender_id,
            data.recipient_id,
            data.task_id,
            data.kind,
        )
        await self._chat.add_message(message)
        await _publish_message(self._bus, message, sender_role)
        return message

    async def _role_of(self, agent_id: AgentId | None) -> str:
        if agent_id is None:
            return _USER_ROLE
        agent = await self._agents.find_by_id(agent_id)
        if agent is None:
            raise AgentNotFoundError("agent.not_found", agent_id=agent_id)
        return agent.role.value
