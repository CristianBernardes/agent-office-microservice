# ADR-018 — Migrações de banco no estilo Laravel

## Status
Aceito

## Contexto
O ADR-014 aplicava um `schema.sql` idempotente a cada startup. Isso não permite evoluir colunas,
reverter mudanças nem saber qual versão do banco está em produção. O autor pediu migrações "ao
estilo Laravel" (`migrate`, `rollback`, `status`, `fresh`, `make:migration`). O projeto usa
`asyncpg` sem ORM (ADR-007), então Alembic/SQLAlchemy traria uma dependência pesada sem ganho.

## Decisão
1. Migrações são pares de arquivos SQL em `backend/src/infrastructure/persistence/migrations/`:
   `AAAA_MM_DD_HHMMSS_nome.up.sql` e `AAAA_MM_DD_HHMMSS_nome.down.sql` (o prefixo ordena).
2. A tabela `migrations(migration, batch, applied_at)` registra o que foi aplicado; cada execução de
   `migrate` forma um *batch* e `rollback` desfaz o último batch (semântica do Laravel).
3. Cada migração roda em transação; falhou, nada é registrado.
4. CLI (`python -m src.infrastructure.persistence.migrator`): `migrate`, `rollback`, `status`,
   `fresh` (derruba o schema `public` e reaplica), `make <nome>` (cria o par de arquivos).
   Atalhos no Makefile: `make migrate`, `migrate-rollback`, `migrate-status`, `migrate-fresh`,
   `make-migration name=...`.
5. No startup com `PERSISTENCE_BACKEND=postgres`, `lifespan` roda as migrações pendentes
   (`migrate`), substituindo `apply_schema`. Aplicar manualmente continua possível.
6. `ops/postgres/init.sql` fica só com extensões (`vector`, `pg_trgm`); as tabelas vêm das migrações.
7. Toda migração tem `down` funcional; migrações já publicadas nunca são editadas, só novas.

## Consequências
- Evolução do banco versionada e reversível, sem dependência nova.
- Menos portátil que um ORM, mas o projeto é Postgres-only (ADR-006).
- O modelo de dados (ADR-017) é entregue em migrações pequenas por assunto.
