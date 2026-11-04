"""Implementação do ``ILlmAdapter`` para a Anthropic (Claude).

Provedor de LLM em nuvem, usado quando um papel tem um modelo Claude configurado
em `.env` (ver ADR-058). A chave de API e a URL base são sempre recebidas por
injeção de dependência (vindas da configuração), nunca fixadas neste módulo —
mesma filosofia de integração HTTP leve já usada para o Ollama e a Tavily
(ADR-005, ADR-011).
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from src.domain.interfaces.llm_adapter import (
    ILlmAdapter,
    LlmEmbeddingResponse,
    LlmThoughtResponse,
)
from src.domain.services.llm_output_guard import strip_reasoning_preamble
from src.infrastructure.llm.anthropic_constants import ANTHROPIC_API_VERSION

# Bloco: endpoint da API Messages da Anthropic.
_MESSAGES_PATH = "/v1/messages"

# Bloco: tempo máximo de espera por uma resposta da API da Anthropic.
_DEFAULT_REQUEST_TIMEOUT_SECONDS = 120.0

# Bloco: limite de tokens de saída; a API da Anthropic exige esse campo (sem
# padrão implícito como a maioria dos provedores compatíveis com OpenAI).
_DEFAULT_MAX_OUTPUT_TOKENS = 4096

# Bloco: modelos locais/remotos nem sempre obedecem ao formato JSON pedido no
# system prompt; a leitura é tolerante, igual ao `OllamaAdapter` (ADR-036).
_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def _parse_structured_reply(raw_content: str) -> dict[str, Any]:
    """Extrai o objeto JSON da resposta; se não houver, trata o texto inteiro como pensamento."""
    content = strip_reasoning_preamble(raw_content)
    candidates = [content]
    match = _JSON_OBJECT.search(content)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {"thought": content, "action": "idle"}


# Bloco: adaptador de LLM para a Anthropic, acessado via HTTP (API Messages).
class AnthropicAdapter(ILlmAdapter):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.anthropic.com",
        request_timeout_seconds: float = _DEFAULT_REQUEST_TIMEOUT_SECONDS,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._max_output_tokens = max_output_tokens
        self._http_client = httpx.AsyncClient(timeout=request_timeout_seconds)

    @property
    def model_name(self) -> str:
        return self._model

    def _require_api_key(self) -> None:
        if not self._api_key:
            # Falha explícita apenas na primeira chamada, nunca na construção do
            # adaptador: papéis que não usam Claude não devem ser impactados
            # pela ausência da chave (mesmo racional do ADR-011).
            raise RuntimeError(
                "ANTHROPIC_API_KEY não configurada. Defina essa variável no seu "
                "'.env' com uma chave obtida em https://console.anthropic.com "
                "para usar um modelo Claude."
            )

    async def think(
        self,
        system_prompt: str,
        context: str,
        temperature: float = 0.7,
    ) -> LlmThoughtResponse:
        """Envia o contexto à Anthropic e retorna a resposta estruturada do agente."""
        self._require_api_key()

        http_response = await self._http_client.post(
            f"{self._base_url}{_MESSAGES_PATH}",
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": ANTHROPIC_API_VERSION,
                "content-type": "application/json",
            },
            json={
                "model": self._model,
                "system": system_prompt,
                "messages": [{"role": "user", "content": context}],
                "max_tokens": self._max_output_tokens,
                "temperature": temperature,
            },
        )
        http_response.raise_for_status()

        content_blocks = http_response.json().get("content", [])
        raw_content = "".join(
            block.get("text", "") for block in content_blocks if block.get("type") == "text"
        )
        parsed_content = _parse_structured_reply(raw_content)

        return LlmThoughtResponse(
            thought=parsed_content.get("thought", ""),
            action=parsed_content.get("action", "idle"),
            target=parsed_content.get("target"),
            tool_call=parsed_content.get("tool_call"),
            raw_response=raw_content,
        )

    async def embed(self, text: str) -> LlmEmbeddingResponse:
        """A Anthropic não oferece uma API de embeddings — sempre delega a outro provedor."""
        raise NotImplementedError(
            "AnthropicAdapter não implementa embeddings. Configure um modelo de "
            "embedding de outro provedor (ex.: OLLAMA_EMBEDDING_MODEL) para o papel "
            "que usa memória semântica."
        )

    async def close(self) -> None:
        """Libera a conexão HTTP subjacente."""
        await self._http_client.aclose()
