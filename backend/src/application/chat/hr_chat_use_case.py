"""Caso de uso: o dono do produto conversa diretamente com o RH (ADR-060).

A conversa vive numa sessão própria (``scenario="hr"``), separada dos objetivos. O RH recebe o
elenco com os identificadores e pode agir pela ferramenta ``propose_dismissal``; a decisão final
continua sendo do dono, pelo modal de aprovação (ADR-056).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.chat.chat_use_cases import (
    SendMessageInput,
    SendMessageUseCase,
    SessionNotFoundError,
)
from src.domain.entities.agent import Agent, AgentStatus, Role
from src.domain.entities.chat import ChatMessage, MessageKind, Session
from src.domain.exceptions.domain_exceptions import DomainError
from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.chat_repository import IChatRepository
from src.domain.localization.language import Language
from src.domain.localization.messages import translate
from src.domain.value_objects.identifiers import SessionId

HR_SCENARIO = "hr"
_HISTORY_LIMIT = 20

_PROMPTS = {
    Language.PT: "O dono do produto está conversando diretamente com você, RH.\n"
    "Elenco atual (nome | cargo | agent_id):\n{roster}\n\n"
    "Conversa até agora:\n{history}\n\n"
    "Mensagem do dono: {message}\n\n"
    "Responda ao dono com objetividade e SOMENTE com um objeto JSON, sem texto fora dele:\n"
    '{{"thought": "<sua resposta ao dono>", "action": "idle", "tool_call": null}}\n'
    "Se o dono pedir ou autorizar a demissão de alguém (inclusive confirmando um pedido "
    "anterior da conversa), preencha tool_call com\n"
    '{{"tool": "propose_dismissal", "args": {{"agent_id": "<id exato da lista>", '
    '"reason": "<motivo dado pelo dono>"}}}}\n'
    "e avise em thought que a proposta foi enviada para a aprovação dele. Nunca diga que "
    "fez algo (conversou com alguém, chamou ferramenta) sem que isso conste em tool_call; "
    "você não tem como conversar com outros agentes por aqui. Ao avaliar desempenho, use só o "
    "que você sabe do time e seja franco.",
    Language.EN: "The product owner is talking directly to you, HR.\n"
    "Current roster (name | role | agent_id):\n{roster}\n\n"
    "Conversation so far:\n{history}\n\n"
    "Owner message: {message}\n\n"
    "Answer the owner concisely and ONLY with a JSON object, no text outside it:\n"
    '{{"thought": "<your answer to the owner>", "action": "idle", "tool_call": null}}\n'
    "If the owner asks for or authorizes someone's dismissal (including confirming an earlier "
    "request in the conversation), fill tool_call with\n"
    '{{"tool": "propose_dismissal", "args": {{"agent_id": "<exact id from the list>", '
    '"reason": "<reason given by the owner>"}}}}\n'
    "and say in thought that the proposal was sent for their approval. Never claim to have done "
    "something (talked to someone, called a tool) unless it is in tool_call; you cannot talk to "
    "other agents from here. When assessing performance, use only what you know of the team "
    "and be candid.",
}

_OWNER_LABEL = {Language.PT: "Dono", Language.EN: "Owner"}


class HrUnavailableError(DomainError):
    """Levantada quando não há um gerente de RH ativo para conversar."""


@dataclass(frozen=True, slots=True)
class HrChatInput:
    content: str
    session_id: SessionId | None = None
    language: Language | None = None


@dataclass(frozen=True, slots=True)
class HrChatResult:
    session_id: SessionId
    reply: ChatMessage


# Bloco: registra a fala do dono, aciona o RH e grava a resposta na mesma sessão.
class HrChatUseCase:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        chat_repository: IChatRepository,
        dispatch_goal: DispatchGoalUseCase,
        send_message: SendMessageUseCase,
        language: Language,
    ) -> None:
        self._agents = agent_repository
        self._chat = chat_repository
        self._dispatch = dispatch_goal
        self._send = send_message
        self._language = language

    async def execute(self, data: HrChatInput) -> HrChatResult:
        lang = data.language or self._language
        agents = await self._agents.list_all()
        hr = self._hr_manager(agents)
        session_id = await self._resolve_session(data.session_id)
        names = {a.agent_id: a.name for a in agents}
        history = "\n".join(
            f"- {names.get(m.sender_id, 'RH') if m.sender_id else _OWNER_LABEL[lang]}: {m.content}"
            for m in await self._chat.list_messages(session_id, _HISTORY_LIMIT)
        )
        await self._send.execute(
            SendMessageInput(session_id, data.content, recipient_id=hr.agent_id)
        )
        prompt = _PROMPTS[lang].format(
            roster=self._roster(agents), history=history, message=data.content
        )
        kind = MessageKind.CHAT
        try:
            content = (await self._dispatch.execute(hr.agent_id, prompt, lang)).thought
        except (DomainError, AgentNotFoundError) as error:
            # A ferramenta recusou a ação (ex.: já pendente): o dono precisa ver o motivo.
            content, kind = error.localized(lang), MessageKind.SYSTEM
        except (KeyError, ValueError):
            # Argumentos inválidos na chamada da ferramenta (ex.: id fora da lista).
            content, kind = translate("hr_chat.invalid_tool_call", lang), MessageKind.SYSTEM
        reply = await self._send.execute(
            SendMessageInput(session_id, content, sender_id=hr.agent_id, kind=kind)
        )
        return HrChatResult(session_id, reply)

    async def _resolve_session(self, session_id: SessionId | None) -> SessionId:
        if session_id is None:
            session = Session(SessionId.generate(), scenario=HR_SCENARIO)
            await self._chat.save_session(session)
            return session.session_id
        existing = await self._chat.find_session(session_id)
        if existing is None or existing.scenario != HR_SCENARIO:
            raise SessionNotFoundError("chat.session_not_found", session_id=session_id)
        return session_id

    @staticmethod
    def _hr_manager(agents: list[Agent]) -> Agent:
        for agent in agents:
            if agent.role == Role.HR_MANAGER and agent.status != AgentStatus.OFFLINE:
                return agent
        raise HrUnavailableError("hr_chat.unavailable")

    @staticmethod
    def _roster(agents: list[Agent]) -> str:
        return "\n".join(
            f"- {a.name} | {a.role.value} | {a.agent_id}"
            for a in agents
            if a.status != AgentStatus.OFFLINE
        )
