"""Rota de verificação de saúde do serviço (health check).

Usada por orquestradores de container (Docker Compose `healthcheck`, Kubernetes
`livenessProbe`, etc.) para determinar se o serviço está em condições de receber
tráfego.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


# Bloco: endpoint de verificação de saúde.
@router.get("/health")
async def health_check() -> dict[str, str]:
    """Retorna um status simples indicando que o serviço está operacional."""
    return {"status": "ok"}
