"""Contrato (porta) de persistência do chat: sessões, objetivos e mensagens (ADR-019)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.chat import ChatMessage, Goal, Session
from src.domain.value_objects.identifiers import SessionId


# Bloco: raiz única de consistência do chat.
class IChatRepository(ABC):
    @abstractmethod
    async def save_session(self, session: Session) -> None:
        """Cria a sessão (idempotente)."""

    @abstractmethod
    async def find_session(self, session_id: SessionId) -> Session | None:
        """Busca a sessão, ou ``None`` se não existir."""

    @abstractmethod
    async def save_goal(self, goal: Goal) -> None:
        """Persiste um objetivo (criação ou atualização)."""

    @abstractmethod
    async def list_goals(self) -> list[Goal]:
        """Lista os objetivos, do mais antigo ao mais novo."""

    @abstractmethod
    async def add_message(self, message: ChatMessage) -> None:
        """Grava uma mensagem de chat."""

    @abstractmethod
    async def list_messages(self, session_id: SessionId, limit: int = 100) -> list[ChatMessage]:
        """Últimas ``limit`` mensagens da sessão, em ordem cronológica."""
