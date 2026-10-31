# SQL de teste / Test SQL

**PT** — Cria de uma vez as 15 tarefas do backlog inicial (as mesmas do `scripts/seed_team.py`) direto no Postgres, para testar o quadro Kanban.

**EN** — Creates the 15 initial backlog tasks (same as `scripts/seed_team.py`) directly in Postgres, to test the Kanban board.

| Arquivo / File | Conteúdo / Content |
|---|---|
| `tasks.pt.sql` | 15 tarefas em português / 15 tasks in Portuguese |
| `tasks.en.sql` | 15 tarefas em inglês / 15 tasks in English |
| `clear_tasks.sql` | Remove todas as tarefas / removes all tasks |

```bash
# Requer migrações aplicadas e PERSISTENCE_BACKEND=postgres / requires applied migrations
docker exec -i agent-office-microservice-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < sql/tasks.pt.sql
docker exec -i agent-office-microservice-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < sql/tasks.en.sql
```

> Com `PERSISTENCE_BACKEND=memory` (padrão) o backend não lê o Postgres; use `python3 scripts/seed_team.py`.
> With `PERSISTENCE_BACKEND=memory` (default) the backend does not read Postgres; use `python3 scripts/seed_team.py`.
