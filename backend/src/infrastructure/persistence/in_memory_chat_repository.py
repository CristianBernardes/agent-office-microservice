"""Implementação em memória do ``IChatRepository``."""

from __future__ import annotations

from src.domain.entities.chat import ChatMessage, Goal, Session
from src.domain.interfaces.chat_repository import IChatRepository
from src.domain.value_objects.identifiers import GoalId, SessionId


# Bloco: repositório de chat em dicionários/listas em memória.
class InMemoryChatRepository(IChatRepository):
    def __init__(self) -> None:
        self._sessions: dict[SessionId, Session] = {}
        self._goals: dict[GoalId, Goal] = {}
        self._messages: list[ChatMessage] = []

    async def save_session(self, session: Session) -> None:
        """Cria a sessão sem sobrescrever uma existente."""
        self._sessions.setdefault(session.session_id, session)

    async def find_session(self, session_id: SessionId) -> Session | None:
        """Retorna a sessão ou ``None``."""
        return self._sessions.get(session_id)

    async def save_goal(self, goal: Goal) -> None:
        """Cria ou atualiza o objetivo."""
        self._goals[goal.goal_id] = goal

    async def list_goals(self) -> list[Goal]:
        """Objetivos na ordem de criação."""
        return list(self._goals.values())

    async def add_message(self, message: ChatMessage) -> None:
        """Acrescenta a mensagem ao histórico."""
        self._messages.append(message)

    async def list_messages(self, session_id: SessionId, limit: int = 100) -> list[ChatMessage]:
        """Últimas ``limit`` mensagens da sessão, em ordem cronológica."""
        own = [m for m in self._messages if m.session_id == session_id]
        return own[-limit:]
