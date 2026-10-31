# Design Doc — Ciclo de trabalho e qualidade de código

## Componentes

- `WorkLoopUseCase` (application): orquestra `_review`, `_work`, `_assign_todo`, `_plan`.
  Colaboradores injetados no construtor (Inversão de Dependência); sem acesso direto a infra.
- `task_splitter` (domain/services): funções puras de divisão de tarefas, testadas isoladamente.
- `task_workflow` (domain/policies): matriz cargo × estágio.
- `MoveTaskUseCase` / `AssignTaskUseCase`: regras de movimentação e dono obrigatório.

## Fluxo do cartão

`todo → in_progress → testing → in_review → done` (ADR-050). Na etapa `testing` o QA/tester valida a
entrega antes da revisão; reprovado, o cartão volta para `in_progress`. A migração
`2026_10_31_000010_add_testing_task_status` amplia o domínio `task_status` (constraint `task_status_check`,
validada em Postgres real).

## Princípios aplicados

| Princípio | Onde |
|---|---|
| SOLID (SRP/DIP) | Casos de uso pequenos; divisão extraída para o domínio; interfaces `I*Repository` |
| DRY | Helper `_speak` único para dispatch + mensagem; prompts centralizados em `_PROMPTS` |
| YAGNI | Sem parâmetros/abstrações além do necessário; limites WIP configuráveis só onde pedido |
| Design Patterns | Repository, Use Case, Strategy (prompts por idioma), Policy, Observer (MQTT) |
| Testes | Unit (`pytest -m unit`), integração (`-m integration`, Postgres/MQTT/Kafka), e2e, Vitest, Go test |
| Documentação | ADRs (`docs/adr`), RFCs (`docs/rfc`), Design Docs (`docs/design`) |
