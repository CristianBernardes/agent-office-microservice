"""Rota de listagem dos modelos de LLM disponíveis para os agentes.

Combina os modelos instalados no Ollama (provedor padrão, ADR-005/ADR-009) com
os modelos Claude disponíveis na conta da Anthropic, quando `ANTHROPIC_API_KEY`
estiver configurada (ADR-058) — sem a chave, nenhum papel pode efetivamente usar
um modelo Claude, então eles não aparecem na lista.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter

from src.infrastructure.config.settings import get_settings
from src.infrastructure.llm.anthropic_constants import ANTHROPIC_API_VERSION

router = APIRouter(prefix="/models", tags=["models"])

# Modelos de embedding não conversam; ficam fora da lista de escolha dos agentes.
_EMBEDDING_MARKERS = ("embed",)

_REQUEST_TIMEOUT_SECONDS = 5


async def _list_ollama_models(base_url: str) -> list[str]:
    """Lista os modelos instalados no Ollama; vazio se o provedor estiver fora do ar."""
    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            return [
                item["name"]
                for item in response.json().get("models", [])
                if not any(marker in item["name"] for marker in _EMBEDDING_MARKERS)
            ]
    except (httpx.HTTPError, KeyError, ValueError):
        return []


async def _list_anthropic_models(api_key: str, base_url: str) -> list[str]:
    """Lista os modelos Claude disponíveis na conta configurada; vazio sem chave ou erro."""
    if not api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{base_url}/v1/models",
                headers={"x-api-key": api_key, "anthropic-version": ANTHROPIC_API_VERSION},
            )
            response.raise_for_status()
            return [item["id"] for item in response.json().get("data", [])]
    except (httpx.HTTPError, KeyError, ValueError):
        return []


@router.get("")
async def list_models() -> list[str]:
    """Lista os modelos de LLM disponíveis: locais (Ollama) e, se configurada, Claude."""
    settings = get_settings()
    ollama_models = await _list_ollama_models(settings.ollama_base_url)
    anthropic_models = await _list_anthropic_models(
        settings.anthropic_api_key, settings.anthropic_base_url
    )
    return sorted(ollama_models + anthropic_models)
