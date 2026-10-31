"""Testes unitários dos casos de uso de chat (ADR-019)."""

from __future__ import annotations

import pytest

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.chat.chat_use_cases import (
    SendMessageInput,
    SendMessageUseCase,
    SessionNotFoundError,
    SubmitGoalInput,
    SubmitGoalUseCase,
)
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.entities.chat import MessageKind
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, SessionId
from src.infrastructure.messaging.in_memory_message_bus import InMemoryMessageBus
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_chat_repository import InMemoryChatRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def world() -> tuple[InMemoryChatRepository, InMemoryAgentRepository, InMemoryMessageBus]:
    return InMemoryChatRepository(), InMemoryAgentRepository(), InMemoryMessageBus()


async def _agent(repo: InMemoryAgentRepository) -> Agent:
    agent = Agent(
        agent_id=AgentId.generate(),
        name="Ana",
        role=Role.DEV_SENIOR,
        personality=Personality(0.5, 0.5, 0.5, 0.5, 0.5),
        llm_model="m",
    )
    await repo.save(agent)
    return agent


class TestSubmitGoal:
    async def test_creates_session_goal_message_and_events(self, world) -> None:  # type: ignore[no-untyped-def]
        chat, _, bus = world
        goal = await SubmitGoalUseCase(chat, bus).execute(SubmitGoalInput("Vender 5 por dia"))

        assert await chat.find_session(goal.session_id) is not None
        assert [g.text for g in await chat.list_goals()] == ["Vender 5 por dia"]
        assert len(await chat.list_messages(goal.session_id)) == 1
        created = bus.get_published_messages("office/goals/created")
        assert created[0]["payload"]["goal_id"] == str(goal.goal_id)  # type: ignore[index]
        assert len(bus.get_published_messages("office/chat/message")) == 1

    async def test_reuses_existing_session(self, world) -> None:  # type: ignore[no-untyped-def]
        chat, _, bus = world
        use_case = SubmitGoalUseCase(chat, bus)
        first = await use_case.execute(SubmitGoalInput("a"))
        second = await use_case.execute(SubmitGoalInput("b", first.session_id))
        assert second.session_id == first.session_id

    async def test_unknown_session_raises_localized(self, world) -> None:  # type: ignore[no-untyped-def]
        chat, _, bus = world
        with pytest.raises(SessionNotFoundError) as error:
            await SubmitGoalUseCase(chat, bus).execute(SubmitGoalInput("a", SessionId.generate()))
        assert error.value.localized(Language.EN)
        assert error.value.localized(Language.PT) != error.value.localized(Language.EN)


class TestSendMessage:
    async def _session(self, chat, bus) -> SessionId:  # type: ignore[no-untyped-def]
        goal = await SubmitGoalUseCase(chat, bus).execute(SubmitGoalInput("x"))
        return goal.session_id

    async def test_user_message_is_published_with_user_role(self, world) -> None:  # type: ignore[no-untyped-def]
        chat, agents, bus = world
        sid = await self._session(chat, bus)
        await SendMessageUseCase(chat, agents, bus).execute(SendMessageInput(sid, "oi"))
        last = bus.get_published_messages("office/chat/message")[-1]
        assert last["agent_role"] == "user"

    async def test_agent_message_uses_agent_role(self, world) -> None:  # type: ignore[no-untyped-def]
        chat, agents, bus = world
        sid = await self._session(chat, bus)
        agent = await _agent(agents)
        message = await SendMessageUseCase(chat, agents, bus).execute(
            SendMessageInput(sid, "pronto", sender_id=agent.agent_id, kind=MessageKind.DECISION)
        )
        assert message.kind is MessageKind.DECISION
        assert bus.get_published_messages("office/chat/message")[-1]["agent_role"] == "dev_senior"
        assert len(await chat.list_messages(sid)) == 2

    async def test_unknown_session_sender_and_recipient(self, world) -> None:  # type: ignore[no-untyped-def]
        chat, agents, bus = world
        use_case = SendMessageUseCase(chat, agents, bus)
        with pytest.raises(SessionNotFoundError):
            await use_case.execute(SendMessageInput(SessionId.generate(), "x"))
        sid = await self._session(chat, bus)
        with pytest.raises(AgentNotFoundError):
            await use_case.execute(SendMessageInput(sid, "x", sender_id=AgentId.generate()))
        with pytest.raises(AgentNotFoundError):
            await use_case.execute(SendMessageInput(sid, "x", recipient_id=AgentId.generate()))
