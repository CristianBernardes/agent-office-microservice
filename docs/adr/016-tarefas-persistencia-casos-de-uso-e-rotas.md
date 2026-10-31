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

## Adendo — histórico de transições e matriz papel × estágio

- Toda mudança de estágio grava uma linha em `task_transitions` (`from_status`, `to_status`, ator,
  papel, nota). Criar, atribuir, concluir e mover registram histórico. `ITaskRepository` ganha
  `add_transition` e `list_transitions`. No Postgres, `actor_id` desconhecido vira `NULL` (a FK
  permite) para não perder o registro.
- Novo caso de uso `MoveTaskUseCase` (`POST /tasks/{id}/move`) com política de domínio
  `task_workflow` (matriz estágio→estágio × papéis). Movimento fora da matriz → 409
  (`task.invalid_move`); papel sem permissão → 403 (`task.move_forbidden`), ambos pt/en.
- Matriz: backlog→todo (PO, SM); todo→in_progress (devs, tech lead); in_progress→in_review (devs,
  tech lead); in_review→done (QA, tech lead, PO); in_review→in_progress (QA, tech lead);
  qualquer ativo→blocked (SM, tech lead, PO); blocked→todo (SM, PO).
- `assign` e `complete` seguem como atalhos de fluxo (backlog→in_progress e in_progress→done)
  sem a matriz, para não quebrar a API da rodada anterior; a matriz vale para `move`.
