# ADR-035 — Permissões de atribuir e concluir tarefas

**Status:** Aceito

## Contexto
A matriz papel × estágio (ADR-016) só valia para `move`. `assign` e `complete` aceitavam qualquer papel.

## Decisão
Política de domínio em `task_workflow.py`: `can_assign` (PO, SM, Tech Lead) e `can_complete` (devs, Tech Lead e QA). Violação levanta `PermissionDeniedError` (`task.assign_forbidden`, `task.complete_forbidden`), que a API traduz em 403 localizado pt/en.

## Consequências
Os três caminhos de mutação de tarefas respeitam papéis. Ferramentas dos agentes passam o papel real do agente.
