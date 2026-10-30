"""Implementação mock do ``ILlmAdapter``, usada em testes.

Permite injetar respostas pré-definidas para validar o comportamento dos casos de
uso sem depender de qualquer chamada de rede real a um provedor de LLM.
"""

from __future__ import annotations

from src.domain.interfaces.llm_adapter import (
    ILlmAdapter,
    LlmEmbeddingResponse,
    LlmThoughtResponse,
)

# Bloco: dimensão padrão do vetor de embedding gerado pelo mock.
# Escolhida para corresponder à dimensão mínima usada em testes de integração
# futuros com pgvector, sem representar nenhum modelo real.
_MOCK_EMBEDDING_DIMENSIONS = 8


# Bloco: adaptador de LLM mock.
# Se nenhuma resposta pré-definida for fornecida, retorna uma resposta padrão
# neutra, suficiente para testes que não se importam com o conteúdo exato do
# pensamento, apenas com o fluxo de chamadas.
class MockLlmAdapter(ILlmAdapter):
    def __init__(self, responses: list[LlmThoughtResponse] | None = None) -> None:
        self._responses = responses or []
        self._call_count = 0

    @property
    def model_name(self) -> str:
        return "mock-model"

    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LlmThoughtResponse:
        """Retorna a próxima resposta pré-configurada, ou uma resposta padrão."""
        if self._responses:
            response = self._responses[self._call_count % len(self._responses)]
            self._call_count += 1
            return response

        return LlmThoughtResponse(
            thought="Estou analisando o contexto recebido.",
            action="idle",
            target=None,
            tool_call=None,
            raw_response='{"thought": "Estou analisando o contexto recebido.", "action": "idle"}',
        )

    async def embed(self, text: str) -> LlmEmbeddingResponse:
        """Gera um vetor de embedding determinístico a partir do hash do texto."""
        seed = sum(ord(character) for character in text) % 1000
        vector = [(seed + index) / 1000.0 for index in range(_MOCK_EMBEDDING_DIMENSIONS)]
        return LlmEmbeddingResponse(
            vector=vector,
            model=self.model_name,
            dimensions=_MOCK_EMBEDDING_DIMENSIONS,
        )
