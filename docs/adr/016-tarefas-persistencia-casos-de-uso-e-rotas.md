# ADR-016 — Tarefas: persistência, casos de uso, ferramentas e rotas

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

A entidade `Task` existe desde a Fase 1, e as ferramentas `create_task`, `assign_task` e
`complete_task` constam na tabela de permissões por papel, mas não havia persistência, casos de uso
nem handlers (o `ToolRegistry` levantava `ToolNotImplementedError`). Sem isso o time não consegue
coordenar trabalho nem a cena do escritório ter o que mostrar.

## Decisão

- `ITaskRepository` (`save`, `find_by_id`, `list_all`), com `InMemoryTaskRepository` e
  `PostgresTaskRepository` (tabela `tasks`, upsert), selecionados por `PERSISTENCE_BACKEND` (ADR-014).
- Casos de uso: `CreateTaskUseCase`, `AssignTaskUseCase`, `CompleteTaskUseCase`. Atribuir exige
  agente `IDLE` (regra já na entidade `Agent`); concluir exige tarefa `IN_PROGRESS` e devolve o
  agente a `IDLE` quando ele ainda estiver com aquela tarefa. Cada mudança publica em
  `office/tasks/updated` (envelope da RFC-001).
- Erro `TaskNotFoundError` (`task.not_found`, pt/en).
- `ToolRegistry` passa a ter handlers das 3 ferramentas (permissões inalteradas, centralizadas ali).
- Rotas finas: `GET /tasks`, `POST /tasks`, `POST /tasks/{id}/assign`, `POST /tasks/{id}/complete`
  (404 inexistente, 409 transição inválida, erros localizados via `Accept-Language`).

## Consequências

- Continuam sem handler: `send_message`, `hire_agent`, `start_ceremony` (próximas rodadas).
- A cena do escritório pode listar tarefas e agentes pela API.
