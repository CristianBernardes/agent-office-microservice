"""Testes do diálogo do PO com o cliente pelo chat (ADR-055)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from src.application.autonomy.client_dialogue_use_case import (
    ClientDialogueUseCase,
    register_client_dialogue,
)
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.entities.chat import Goal, MessageKind, Session
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, GoalId, SessionId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_chat_repository import InMemoryChatRepository

pytestmark = pytest.mark.unit


class _Dispatch:
    def __init__(self) -> None:
        self.contexts: list[str] = []

    async def execute(self, agent_id: AgentId, context: str, language: Any = None) -> Any:
        self.contexts.append(context)
        return SimpleNamespace(thought="entendi")


class _Sink:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    async def execute(self, data: Any) -> None:
        self.calls.append(data)


async def _build(
    with_po: bool = True, with_goal: bool = True, language: Language = Language.EN
) -> tuple[ClientDialogueUseCase, SessionId, _Dispatch, _Sink, _Sink]:
    agents, chat = InMemoryAgentRepository(), InMemoryChatRepository()
    if with_po:
        await agents.save(
            Agent(
                AgentId.generate(),
                "PO",
                Role.PRODUCT_OWNER,
                Personality(0.5, 0.5, 0.5, 0.5, 0.5),
                "m",
            )
        )
    session = SessionId.generate()
    await chat.save_session(Session(session))
    if with_goal:
        await chat.save_goal(Goal(GoalId.generate(), session, "Sell a product"))
    dispatch, send, remember = _Dispatch(), _Sink(), _Sink()
    use_case = ClientDialogueUseCase(
        agents,
        chat,
        dispatch,  # type: ignore[arg-type]
        send,  # type: ignore[arg-type]
        remember,  # type: ignore[arg-type]
        language,
    )
    return use_case, session, dispatch, send, remember


async def test_po_answers_the_client_and_remembers_the_decision() -> None:
    use_case, session, dispatch, send, remember = await _build()

    assert await use_case.execute(session, "Focus on Pix payments") is True

    assert send.calls[0].kind == MessageKind.DECISION
    assert send.calls[0].sender_id is not None
    assert remember.calls[0].content == "Focus on Pix payments"
    assert "Client reply: Focus on Pix payments" in dispatch.contexts[0]


async def test_the_goal_text_itself_is_not_a_client_reply() -> None:
    use_case, session, _, send, _ = await _build()
    assert await use_case.execute(session, "Sell a product") is False
    assert send.calls == []


async def test_no_dialogue_without_po_or_goal() -> None:
    no_po, session, *_ = await _build(with_po=False)
    assert await no_po.execute(session, "hi") is False
    no_goal, session, *_ = await _build(with_goal=False)
    assert await no_goal.execute(session, "hi") is False


async def test_prompt_is_localized() -> None:
    use_case, session, dispatch, *_ = await _build(language=Language.PT)
    await use_case.execute(session, "Foque no Pix")
    assert "Resposta do cliente: Foque no Pix" in dispatch.contexts[0]


async def test_subscription_reacts_only_to_user_chat_messages() -> None:
    use_case, session, _, send, _ = await _build()
    bus = InMemoryMessageBus()
    await register_client_dialogue(bus, lambda: use_case)()

    def envelope(role: str, kind: str) -> dict[str, object]:
        return {
            "agent_role": role,
            "payload": {"session_id": str(session.value), "content": "ok", "kind": kind},
        }

    await bus.publish("office/chat/message", envelope("product_owner", "chat"))
    await bus.publish("office/chat/message", envelope("user", "question"))
    await bus.publish("office/chat/message", {"agent_role": "user", "payload": {}})
    await asyncio.sleep(0.05)
    assert send.calls == []

    await bus.publish("office/chat/message", envelope("user", "chat"))
    await asyncio.sleep(0.05)
    assert len(send.calls) == 1
