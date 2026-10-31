# ADR-025: Tarefas vinculadas ao objetivo e ao revisor

- Status: Aceito

## Contexto
O schema (`tasks.goal_id`, `tasks.reviewer_id`) já prevê esses vínculos, mas a entidade `Task`
e o repositório os ignoravam. Sem `goal_id` não dá para listar o backlog de um objetivo.

## Decisão
- `Task` ganha `goal_id: GoalId | None` e `reviewer_id: AgentId | None`.
- `CreateTaskInput` aceita `goal_id` opcional; a reunião de objetivo o preenche.
- O repositório Postgres persiste ambos. `position` fica com o default do banco (YAGNI até
  existir reordenação no frontend).

## Consequências
Rastreabilidade objetivo → tarefas. O vínculo de revisor é gravado por casos de uso futuros.
