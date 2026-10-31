"""Rota de listagem dos modelos de LLM disponíveis no provedor (Ollama)."""

from __future__ import annotations

import httpx
from fastapi import APIRouter

from src.infrastructure.config.settings import get_settings

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_models() -> list[str]:
    """Lista os modelos instalados no Ollama; vazio se o provedor estiver fora do ar."""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            names = [item["name"] for item in response.json().get("models", [])]
    except (httpx.HTTPError, KeyError, ValueError):
        return []
    return sorted(names)
