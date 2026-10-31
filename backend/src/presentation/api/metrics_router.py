"""Endpoint `/metrics` no formato Prometheus (ADR-052).

Expõe métricas HTTP (via middleware) e gauges de negócio (tarefas por status e
agentes por papel), calculados a cada coleta.
"""

from __future__ import annotations

import time
from collections import Counter as TallyCounter
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from src.domain.interfaces.agent_repository import IAgentRepository
from src.domain.interfaces.task_repository import ITaskRepository

registry = CollectorRegistry()

HTTP_REQUESTS = Counter(
    "office_http_requests_total",
    "Requisições HTTP por método, rota e status.",
    ["method", "route", "status"],
    registry=registry,
)
HTTP_LATENCY = Histogram(
    "office_http_request_duration_seconds",
    "Latência das requisições HTTP.",
    ["method", "route"],
    registry=registry,
)
TASKS_BY_STATUS = Gauge(
    "office_tasks",
    "Quantidade de tarefas por status.",
    ["status"],
    registry=registry,
)
AGENTS_BY_ROLE = Gauge(
    "office_agents",
    "Quantidade de agentes por papel.",
    ["role"],
    registry=registry,
)

router = APIRouter(tags=["metrics"])


# Bloco: middleware que registra contagem e latência por rota (template, não URL crua).
async def metrics_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    started = time.perf_counter()
    response = await call_next(request)
    route = getattr(request.scope.get("route"), "path", "unmatched")
    HTTP_REQUESTS.labels(request.method, route, str(response.status_code)).inc()
    HTTP_LATENCY.labels(request.method, route).observe(time.perf_counter() - started)
    return response


# Bloco: atualiza os gauges de negócio a partir dos repositórios.
async def refresh_business_gauges(tasks: ITaskRepository, agents: IAgentRepository) -> None:
    by_status = TallyCounter(t.status.value for t in await tasks.list_all())
    by_role = TallyCounter(a.role.value for a in await agents.list_all())
    TASKS_BY_STATUS.clear()
    AGENTS_BY_ROLE.clear()
    for status, count in by_status.items():
        TASKS_BY_STATUS.labels(status).set(count)
    for role, count in by_role.items():
        AGENTS_BY_ROLE.labels(role).set(count)


@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    # Import tardio evita ciclo com dependencies.
    from src.presentation.dependencies import get_agent_repository, get_task_repository

    await refresh_business_gauges(get_task_repository(), get_agent_repository())
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
