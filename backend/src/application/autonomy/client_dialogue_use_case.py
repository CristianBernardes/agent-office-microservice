"""Caso de uso: o PO conversa com o cliente (o usuário) pelo chat (ADR-055).

Quando o usuário responde no chat à pergunta do PO, o PO confirma o entendimento, registra a
decisão do cliente na memória e responde na mesma sessão. O time não espera pela resposta: ela
entra como contexto e orienta os próximos passos.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from uuid import UUID

from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.application.chat.chat_use_cases import SendMessageInput, SendMessageUseCase
from src.application.memory.memory_use_cases import RememberInput, RememberUseCase
from src.domain.entities.agent import Agent, AgentStatus, Role
from src.domain.entities.chat import MessageKind
from src.domain.entities.memory import MemoryType
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.chat_repository import IChatRepository
from src.domain.interfaces.message_bus import IMessageBus
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import SessionId

logger = logging.getLogger(__name__)

_CHAT_MESSAGE_TOPIC = "office/chat/message"
_USER_ROLE = "user"
_HISTORY_LIMIT = 30

_PROMPTS = {
    Language.PT: "Objetivo do cliente: {goal}\nConversa até agora:\n{history}\n\n"
    "Resposta do cliente: {reply}\n\n"
    "Como Product Owner, confirme o seu entendimento ao cliente e diga, em poucas linhas, "
    "o que isso muda no escopo e nas entregas do time.",
    Language.EN: "Client goal: {goal}\nConversation so far:\n{history}\n\n"
    "Client reply: {reply}\n\n"
    "As Product Owner, confirm your understanding to the client and say, in a few lines, "
    "what this changes in the team's scope and deliverables.",
}


class ClientDialogueUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        chat_repository: IChatRepository,
        dispatch_goal: DispatchGoalUseCase,
        send_message: SendMessageUseCase,
        remember: RememberUseCase,
        language: Language,
    ) -> None:
        self._agents = agent_repository
        self._chat = chat_repository
        self._dispatch = dispatch_goal
        self._send = send_message
        self._remember = remember
        self._language = language

    async def execute(
        self, session_id: SessionId, reply: str, language: Language | None = None
    ) -> bool:
        """Responde ao cliente; devolve ``False`` se não houve diálogo (sem PO ou sem objetivo)."""
        owner = await self._product_owner()
        goals = [g for g in await self._chat.list_goals() if g.session_id == session_id]
        # A mensagem inicial do objetivo é o próprio objetivo, não uma resposta do cliente.
        if owner is None or not goals or any(g.text == reply for g in goals):
            return False
        lang = language or self._language
        history = "\n".join(
            f"- {m.content}" for m in await self._chat.list_messages(session_id, _HISTORY_LIMIT)
        )
        prompt = _PROMPTS[lang].format(goal=goals[-1].text, history=history, reply=reply)
        await self._remember.execute(
            RememberInput(
                agent_id=owner.agent_id,
                content=reply,
                memory_type=MemoryType.CONVERSATION,
                importance=0.9,
                session_id=session_id,
            )
        )
        response = await self._dispatch.execute(owner.agent_id, prompt, lang)
        await self._send.execute(
            SendMessageInput(
                session_id=session_id,
                content=response.thought,
                sender_id=owner.agent_id,
                kind=MessageKind.DECISION,
            )
        )
        return True

    async def _product_owner(self) -> Agent | None:
        for agent in await self._agents.list_all():
            if agent.role == Role.PRODUCT_OWNER and agent.status != AgentStatus.OFFLINE:
                return agent
        return None


# Bloco: assina as mensagens do chat e reage só às respostas do usuário (nunca às dos agentes).
_background_tasks: set[asyncio.Task[object]] = set()


async def _run_safely(use_case: ClientDialogueUseCase, session_id: SessionId, text: str) -> None:
    try:
        await use_case.execute(session_id, text)
    except Exception:
        logger.exception("Falha no diálogo do PO com o cliente")


def register_client_dialogue(
    bus: IMessageBus, use_case_factory: Callable[[], ClientDialogueUseCase]
) -> Callable[[], Awaitable[None]]:
    """Devolve a corrotina de registro da assinatura de ``office/chat/message``."""

    async def handler(_topic: str, envelope: dict[str, object]) -> None:
        payload = envelope.get("payload")
        if envelope.get("agent_role") != _USER_ROLE or not isinstance(payload, dict):
            return
        if payload.get("kind") != MessageKind.CHAT.value:
            return
        try:
            session_id = SessionId(value=UUID(str(payload["session_id"])))
            text = str(payload["content"])
        except (KeyError, ValueError):
            logger.warning("Mensagem de chat inválida descartada")
            return
        task = asyncio.create_task(_run_safely(use_case_factory(), session_id, text))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

    async def register() -> None:
        await bus.subscribe(_CHAT_MESSAGE_TOPIC, handler)

    return register
