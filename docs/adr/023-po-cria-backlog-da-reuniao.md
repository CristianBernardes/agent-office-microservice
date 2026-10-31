# ADR-023 — PO cria o backlog a partir da reunião

- Status: aceita

## Decisão

- Ao fim da reunião (ADR-022), se o product_owner participou, ele cria no backlog uma tarefa por
  contribuição dos demais papéis (`[papel] primeira linha da fala`, descrição = fala completa),
  via `CreateTaskUseCase` (nasce em backlog, publica `office/tasks/updated`).
- Determinístico (sem parsear JSON do LLM) — YAGNI; sem PO, não há tarefas. Falha ao criar uma
  tarefa é logada e não interrompe as demais.
