"""Ponto de entrada da aplicação FastAPI.

Responsável apenas por compor a aplicação HTTP (registrar rotas e metadados) —
nenhuma regra de negócio deve existir neste módulo (ver ADR-007).
"""

from __future__ import annotations

from fastapi import FastAPI

from src.presentation.api.agents_router import router as agents_router
from src.presentation.api.health_router import router as health_router

# Bloco: instância principal da aplicação FastAPI.
# Metadados usados para a documentação automática (OpenAPI/Swagger) em `/docs`.
app = FastAPI(
    title="AgentOffice Pro — Backend",
    description="Backend Clean Architecture que orquestra agentes de IA do AgentOffice Pro.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(agents_router)
