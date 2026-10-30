"""Implementação do ``ILlmAdapter`` para o Ollama.

O Ollama é sempre acessado como um serviço **externo**, nunca dentro do Docker
Compose deste projeto (ver ADR-009). A URL base é sempre recebida por injeção de
dependência (vinda da configuração em `.env`), nunca fixada neste módulo.
"""

from __future__ import annotations

import json

import httpx

from src.domain.interfaces.llm_adapter import (
    ILlmAdapter,
    LlmEmbeddingResponse,
    LlmThoughtResponse,
)

# Bloco: tempo máximo de espera por uma resposta do Ollama.
# Modelos locais podem ser lentos na primeira chamada (carregamento em memória);
# o timeout é generoso para evitar falhas espúrias em hardware mais modesto.
_REQUEST_TIMEOUT_SECONDS = 120.0


# Bloco: adaptador de LLM para o Ollama, acessado via HTTP.
class OllamaAdapter(ILlmAdapter):
    def __init__(self, base_url: str, model: str, embedding_model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._embedding_model = embedding_model
        self._http_client = httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS)

    @property
    def model_name(self) -> str:
        return self._model

    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LlmThoughtResponse:
        """Envia o contexto ao Ollama e retorna a resposta estruturada do agente."""
        http_response = await self._http_client.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context},
                ],
                "options": {"temperature": temperature},
                "stream": False,
            },
        )
        http_response.raise_for_status()

        raw_content = http_response.json()["message"]["content"]
        parsed_content = json.loads(raw_content)

        return LlmThoughtResponse(
            thought=parsed_content.get("thought", ""),
            action=parsed_content.get("action", "idle"),
            target=parsed_content.get("target"),
            tool_call=parsed_content.get("tool_call"),
            raw_response=raw_content,
        )

    async def embed(self, text: str) -> LlmEmbeddingResponse:
        """Gera um embedding vetorial para o texto usando o modelo de embeddings configurado."""
        http_response = await self._http_client.post(
            f"{self._base_url}/api/embeddings",
            json={"model": self._embedding_model, "prompt": text},
        )
        http_response.raise_for_status()

        vector = http_response.json()["embedding"]
        return LlmEmbeddingResponse(
            vector=vector,
            model=self._embedding_model,
            dimensions=len(vector),
        )

    async def close(self) -> None:
        """Libera a conexão HTTP subjacente."""
        await self._http_client.aclose()
