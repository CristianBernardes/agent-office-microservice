"""Ponto de entrada da aplicação FastAPI.

Responsável apenas por compor a aplicação HTTP (registrar rotas e metadados) —
nenhuma regra de negócio deve existir neste módulo (ver ADR-007).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.config.settings import get_settings
from src.infrastructure.persistence.postgres_connection import create_postgres_pool
from src.infrastructure.persistence.postgres_schema import apply_schema
from src.presentation.api.agents_router import router as agents_router
from src.presentation.api.health_router import router as health_router
from src.presentation.dependencies import set_database_pool


# Bloco: ciclo de vida da aplicação (ADR-014).
# Só abre a pool PostgreSQL quando `PERSISTENCE_BACKEND=postgres`; falha rápida
# se o banco estiver indisponível.
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.persistence_backend != "postgres":
        yield
        return
    pool = await create_postgres_pool(settings.database_url)
    try:
        await apply_schema(pool)
        set_database_pool(pool)
        yield
    finally:
        set_database_pool(None)
        await pool.close()


# Bloco: instância principal da aplicação FastAPI.
# Metadados usados para a documentação automática (OpenAPI/Swagger) em `/docs`.
app = FastAPI(
    title="AgentOffice Pro — Backend",
    description="Backend Clean Architecture que orquestra agentes de IA do AgentOffice Pro.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(agents_router)
