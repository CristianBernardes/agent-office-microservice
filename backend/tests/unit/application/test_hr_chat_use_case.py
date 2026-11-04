"""Testes do chat direto do dono do produto com o RH (ADR-060)."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.application.agents.fire_agent_use_case import AgentNotFoundError
from src.application.chat.hr_chat_use_case import HrChatInput, HrChatUseCase, HrUnavailableError
from src.domain.entities.agent import Agent, Personality, Role
from src.domain.entities.chat import ChatMessage, MessageKind, Session
from src.domain.exceptions.domain_exceptions import InvalidValueError
from src.domain.localization.language import Language
from src.domain.value_objects.identifiers import AgentId, MessageId, SessionId
from src.infrastructure.persistence.in_memory_agent_repository import InMemoryAgentRepository
from src.infrastructure.persistence.in_memory_chat_repository import InMemoryChatRepository
from src.presentation.dependencies import (
    get_agent_repository,
    get_chat_repository,
    get_hr_chat_use_case,
)
from src.presentation.main import app

pytestmark = pytest.mark.unit


class _Dispatch:
    def __init__(self, error: Exception | None = None) -> None:
        self.contexts: list[str] = []
        self._error = error

    async def execute(self, agent_id: AgentId, context: str, language: Language | None) -> object:
        self.contexts.append(context)
        if self._error:
            raise self._error
        return type("R", (), {"thought": "Vou propor."})()


class _Send:
    def __init__(self, chat: InMemoryChatRepository) -> None:
        self._chat = chat

    async def execute(self, data):  # type: ignore[no-untyped-def]
        message = ChatMessage(
            MessageId.generate(),
            data.session_id,
            data.content,
            data.sender_id,
            data.recipient_id,
            None,
            data.kind,
        )
        await self._chat.add_message(message)
        return message


def _agent(name: str, role: Role) -> Agent:
    return Agent(AgentId.generate(), name, role, Personality(0.5, 0.5, 0.5, 0.5, 0.5), "m")


async def _build(
    dispatch: _Dispatch, with_hr: bool = True
) -> tuple[HrChatUseCase, InMemoryChatRepository, Agent]:
    agents, chat = InMemoryAgentRepository(), InMemoryChatRepository()
    hr = _agent("Rita", Role.HR_MANAGER)
    dev = _agent("Davi", Role.DEV_JUNIOR)
    if with_hr:
        await agents.save(hr)
    await agents.save(dev)
    use_case = HrChatUseCase(agents, chat, dispatch, _Send(chat), Language.EN)  # type: ignore[arg-type]
    return use_case, chat, dev


async def test_creates_an_hr_session_and_gives_hr_the_roster() -> None:
    dispatch = _Dispatch()
    use_case, chat, dev = await _build(dispatch)

    result = await use_case.execute(HrChatInput("Fire Davi, he keeps missing deadlines"))

    session = await chat.find_session(result.session_id)
    assert session is not None and session.scenario == "hr"
    assert f"Davi | dev_junior | {dev.agent_id}" in dispatch.contexts[0]
    assert "Owner message: Fire Davi" in dispatch.contexts[0]
    assert result.reply.content == "Vou propor."
    assert result.reply.kind == MessageKind.CHAT
    assert len(await chat.list_messages(result.session_id)) == 2


async def test_reuses_the_session_and_sends_history() -> None:
    dispatch = _Dispatch()
    use_case, _, _ = await _build(dispatch)
    first = await use_case.execute(HrChatInput("How is the team?"))

    second = await use_case.execute(HrChatInput("And Davi?", session_id=first.session_id))

    assert second.session_id == first.session_id
    assert "- How is the team?" in dispatch.contexts[1]


async def test_tool_refusal_becomes_a_system_message() -> None:
    use_case, _, _ = await _build(_Dispatch(InvalidValueError("dismissal.reason_required")))
    result = await use_case.execute(HrChatInput("Fire Davi"))
    assert result.reply.kind == MessageKind.SYSTEM
    assert "needs a reason" in result.reply.content


async def test_requires_an_active_hr_manager() -> None:
    use_case, _, _ = await _build(_Dispatch(), with_hr=False)
    with pytest.raises(HrUnavailableError):
        await use_case.execute(HrChatInput("Hello"))


async def test_rejects_a_session_that_is_not_an_hr_session() -> None:
    use_case, chat, _ = await _build(_Dispatch())
    other = SessionId.generate()
    await chat.save_session(Session(other))
    with pytest.raises(Exception, match="not found"):
        await use_case.execute(HrChatInput("Hello", session_id=other))


async def test_agent_not_found_during_dispatch_is_reported() -> None:
    use_case, _, _ = await _build(_Dispatch(AgentNotFoundError("agent.not_found", agent_id="x")))
    result = await use_case.execute(HrChatInput("Fire x"))
    assert result.reply.kind == MessageKind.SYSTEM


client = TestClient(app)


@pytest.fixture
def _clean() -> Iterator[None]:
    for factory in (get_agent_repository, get_chat_repository):
        factory.cache_clear()
    yield


class TestHrChatRoute:
    def test_conflict_without_hr(self, _clean: None) -> None:
        response = client.post("/hr/chat", json={"content": "Oi"})
        assert response.status_code == 409

    def test_unknown_session_is_404(self, _clean: None) -> None:
        client.post("/agents", json={"name": "Rita", "role": "hr_manager", "llm_model": "m"})
        response = client.post("/hr/chat", json={"content": "Oi", "session_id": str(uuid4())})
        assert response.status_code == 404

    def test_talks_to_hr_and_history_is_listable(self, _clean: None) -> None:
        app.dependency_overrides[get_hr_chat_use_case] = lambda: HrChatUseCase(
            get_agent_repository(),
            get_chat_repository(),
            _Dispatch(),  # type: ignore[arg-type]
            _Send(get_chat_repository()),  # type: ignore[arg-type]
            Language.EN,
        )
        try:
            self._talk()
        finally:
            app.dependency_overrides.clear()

    @staticmethod
    def _talk() -> None:
        client.post("/agents", json={"name": "Rita", "role": "hr_manager", "llm_model": "m"})
        response = client.post("/hr/chat", json={"content": "Como está o time?"})
        assert response.status_code == 200
        body = response.json()
        messages = client.get(f"/sessions/{body['session_id']}/messages").json()
        assert [m["content"] for m in messages][0] == "Como está o time?"
        assert body["reply"]["sender_id"] is not None
