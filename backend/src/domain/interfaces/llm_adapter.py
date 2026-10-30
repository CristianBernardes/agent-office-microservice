"""Contrato (porta) para adaptadores de modelos de linguagem (LLM).

Qualquer provedor de LLM (Ollama, OpenAI-compatible, ou um mock de testes) deve
implementar esta interface para ser utilizável pelos casos de uso da camada de
aplicação, sem que ela precise conhecer detalhes do provedor concreto (ver
ADR-005 e ADR-007).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# Bloco: resposta estruturada de uma chamada de raciocínio ao LLM.
# O campo `tool_call` é opcional porque nem toda resposta do agente envolve o uso
# de uma ferramenta — às vezes o agente apenas pensa ou conversa.
@dataclass(frozen=True, slots=True)
class LlmThoughtResponse:
    thought: str
    action: str
    target: str | None
    tool_call: dict[str, object] | None
    raw_response: str


# Bloco: resposta de uma chamada de geração de embedding vetorial.
@dataclass(frozen=True, slots=True)
class LlmEmbeddingResponse:
    vector: list[float]
    model: str
    dimensions: int


# Bloco: contrato único para qualquer provedor de LLM.
# Interface pequena e focada (Interface Segregation Principle): apenas as duas
# operações que a aplicação efetivamente precisa — raciocinar e gerar embeddings.
class ILlmAdapter(ABC):
    @abstractmethod
    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LlmThoughtResponse:
        """Envia um contexto ao LLM e retorna uma resposta estruturada."""

    @abstractmethod
    async def embed(self, text: str) -> LlmEmbeddingResponse:
        """Gera um vetor de embedding para o texto informado."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nome do modelo configurado neste adaptador."""
