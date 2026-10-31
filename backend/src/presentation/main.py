"""Ponto de entrada da aplicação FastAPI.

Responsável apenas por compor a aplicação HTTP (registrar rotas e metadados) —
nenhuma regra de negócio deve existir neste módulo (ver ADR-007).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.application.activity.activity_feed import register_activity_feed
from src.application.autonomy.goal_meeting_use_case import register_goal_autonomy
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.persistence.migrator import migrate
from src.infrastructure.persistence.postgres_connection import create_postgres_pool
from src.presentation.api.activity_router import router as activity_router
from src.presentation.api.agents_router import router as agents_router
from src.presentation.api.chat_router import router as chat_router
from src.presentation.api.health_router import router as health_router
from src.presentation.api.layout_router import router as layout_router
from src.presentation.api.memory_router import router as memory_router
from src.presentation.api.research_router import router as research_router
from src.presentation.api.social_router import router as social_router
from src.presentation.api.tasks_router import router as tasks_router
from src.presentation.dependencies import (
    get_activity_repository,
    get_goal_meeting_use_case,
    get_message_bus,
    set_database_pool,
)


# Bloco: ciclo de vida da aplicação (ADR-014).
# Só abre a pool PostgreSQL quando `PERSISTENCE_BACKEND=postgres`; falha rápida
# se o banco estiver indisponível.
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    bus = get_message_bus()
    await bus.connect()
    await register_activity_feed(bus, get_activity_repository)()
    if settings.autonomy_enabled:
        await register_goal_autonomy(bus, get_goal_meeting_use_case)()
    try:
        async with _database(settings):
            yield
    finally:
        await bus.disconnect()


@asynccontextmanager
async def _database(settings: Settings) -> AsyncIterator[None]:
    if settings.persistence_backend != "postgres":
        yield
        return
    pool = await create_postgres_pool(settings.database_url)
    try:
        await migrate(pool)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(agents_router)
app.include_router(tasks_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(social_router)
app.include_router(layout_router)
app.include_router(activity_router)
app.include_router(research_router)
