"""Implementação do ``ILlmAdapter`` para endpoints compatíveis com a API OpenAI.

Usado para modelos em nuvem expostos por um gateway `/v1/chat/completions`
(ex.: modelos `us.anthropic.*`). URL e chave vêm sempre da configuração.
"""

from __future__ import annotations

import httpx

from src.domain.interfaces.llm_adapter import (
    ILlmAdapter,
    LlmEmbeddingResponse,
    LlmThoughtResponse,
)

from src.infrastructure.llm.anthropic_adapter import _parse_structured_reply

_CHAT_COMPLETIONS_PATH = "/v1/chat/completions"
_DEFAULT_REQUEST_TIMEOUT_SECONDS = 120.0
_DEFAULT_MAX_OUTPUT_TOKENS = 16384


class OpenAICompatibleAdapter(ILlmAdapter):
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        request_timeout_seconds: float = _DEFAULT_REQUEST_TIMEOUT_SECONDS,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._max_output_tokens = max_output_tokens
        self._http_client = httpx.AsyncClient(timeout=request_timeout_seconds)

    @property
    def model_name(self) -> str:
        return self._model

    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LlmThoughtResponse:
        """Envia o contexto ao gateway e retorna a resposta estruturada do agente."""
        if not self._base_url:
            raise RuntimeError(
                "CLOUD_LLM_BASE_URL não configurada. Defina essa variável no seu '.env' "
                "para usar modelos em nuvem."
            )
        headers = {"content-type": "application/json"}
        if self._api_key:
            headers["authorization"] = f"Bearer {self._api_key}"

        http_response = await self._http_client.post(
            f"{self._base_url}{_CHAT_COMPLETIONS_PATH}",
            headers=headers,
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context},
                ],
                "max_tokens": self._max_output_tokens,
                "temperature": temperature,
                "stream": False,
            },
        )
        http_response.raise_for_status()

        raw_content = http_response.json()["choices"][0]["message"].get("content") or ""
        parsed_content = _parse_structured_reply(raw_content)

        return LlmThoughtResponse(
            thought=parsed_content.get("thought", ""),
            action=parsed_content.get("action", "idle"),
            target=parsed_content.get("target"),
            tool_call=parsed_content.get("tool_call"),
            raw_response=raw_content,
        )

    async def embed(self, text: str) -> LlmEmbeddingResponse:
        """Modelos de chat em nuvem não geram embeddings; use outro provedor."""
        raise NotImplementedError(
            "OpenAICompatibleAdapter não implementa embeddings. Configure um modelo "
            "de embedding de outro provedor (ex.: OLLAMA_EMBEDDING_MODEL)."
        )

    async def close(self) -> None:
        """Libera a conexão HTTP subjacente."""
        await self._http_client.aclose()
