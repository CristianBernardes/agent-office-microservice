"""Caso de uso: o dono do produto conversa diretamente com o RH (ADR-060).

A conversa vive numa sessão própria (``scenario="hr"``), separada dos objetivos. Quando o dono
ordena uma demissão, o RH registra a proposta na hora; a demissão só acontece quando o dono a
aprova na modal (ADR-056). Nas demais mensagens o RH responde pelo LLM.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.application.agents.dispatch_goal_use_case import DispatchGoalUseCase
from src.application.chat.chat_use_cases import (
    SendMessageInput,
    SendMessageUseCase,
    SessionNotFoundError,
)
from src.application.chat.dismissal_intent import detect_dismissal_targets
from src.application.dismissals.dismissal_use_cases import (
    ProposeDismissalInput,
    ProposeDismissalUseCase,
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
    "Elenco atual (nome | cargo):\n{roster}\n\n"
    "Conversa até agora:\n{history}\n\n"
    "Mensagem do dono: {message}\n\n"
    "Responda ao dono com objetividade. Use só o que você sabe do time e seja franco. Nunca "
    "diga que fez algo (como conversar com outro agente) que você não fez; demissões ordenadas "
    "pelo dono são executadas pelo sistema, não por você aqui.",
    Language.EN: "The product owner is talking directly to you, HR.\n"
    "Current roster (name | role):\n{roster}\n\n"
    "Conversation so far:\n{history}\n\n"
    "Owner message: {message}\n\n"
    "Answer the owner concisely. Use only what you know of the team and be candid. Never claim "
    "to have done something (like talking to another agent) that you did not do; dismissals "
    "ordered by the owner are carried out by the system, not by you here.",
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
        propose_dismissal: ProposeDismissalUseCase,
        language: Language,
    ) -> None:
        self._agents = agent_repository
        self._chat = chat_repository
        self._dispatch = dispatch_goal
        self._send = send_message
        self._propose = propose_dismissal
        self._language = language

    async def execute(self, data: HrChatInput) -> HrChatResult:
        lang = data.language or self._language
        agents = await self._agents.list_all()
        hr = self._hr_manager(agents)
        session_id = await self._resolve_session(data.session_id)
        names = {a.agent_id: a.name for a in agents}
        messages = await self._chat.list_messages(session_id, _HISTORY_LIMIT)
        await self._send.execute(
            SendMessageInput(session_id, data.content, recipient_id=hr.agent_id)
        )
        active = [a for a in agents if a.status != AgentStatus.OFFLINE]
        targets = detect_dismissal_targets(
            data.content, [m.content for m in messages], [a for a in active if a is not hr]
        )
        kind = MessageKind.CHAT
        if targets:
            content, kind = await self._dismiss(hr, targets, data.content, lang)
        else:
            history = "\n".join(
                f"- {names.get(m.sender_id, 'RH') if m.sender_id else _OWNER_LABEL[lang]}: "
                f"{m.content}"
                for m in messages
            )
            prompt = _PROMPTS[lang].format(
                roster=self._roster(agents), history=history, message=data.content
            )
            content = (await self._dispatch.execute(hr.agent_id, prompt, lang)).thought
        reply = await self._send.execute(
            SendMessageInput(session_id, content, sender_id=hr.agent_id, kind=kind)
        )
        return HrChatResult(session_id, reply)

    # Bloco: ordem do dono vira proposta; quem demite é o dono, na modal de aprovação (ADR-056).
    async def _dismiss(
        self, hr: Agent, targets: list[Agent], reason: str, lang: Language
    ) -> tuple[str, MessageKind]:
        lines: list[str] = []
        failed = False
        for target in targets:
            try:
                await self._propose.execute(
                    ProposeDismissalInput(hr.agent_id, target.agent_id, reason)
                )
                lines.append(translate("hr_chat.proposed", lang, name=target.name))
            except DomainError as error:
                failed = True
                lines.append(error.localized(lang))
        return "\n".join(lines), MessageKind.SYSTEM if failed else MessageKind.CHAT

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
            f"- {a.name} | {a.role.value}" for a in agents if a.status != AgentStatus.OFFLINE
        )
