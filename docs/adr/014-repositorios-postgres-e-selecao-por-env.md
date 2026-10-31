# ADR-014 — Repositórios PostgreSQL e seleção de persistência via `.env`

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

Os repositórios de agentes e artefatos eram apenas em memória (dados perdidos a cada restart).
O ADR-006 já define PostgreSQL como banco do projeto.

## Decisão

- `PostgresAgentRepository` e `PostgresArtifactRepository` (asyncpg, SQL parametrizado, upsert
  `ON CONFLICT`). O artefato continua sendo escrito em disco pelo `MarkdownArtifactWriter` (RFC-002)
  e o conteúdo também é guardado no banco, permitindo reconstruir a entidade por completo.
- Esquema em `infrastructure/persistence/schema.sql`, idempotente (`CREATE TABLE IF NOT EXISTS`),
  aplicado no startup por `apply_schema(pool)` quando o backend é PostgreSQL. Sem framework de
  migração por ora (YAGNI); se o esquema evoluir, adota-se uma ferramenta em novo ADR.
- `PERSISTENCE_BACKEND` (`memory` | `postgres`, padrão `memory`) em `.env`. No modo `postgres`, o
  `lifespan` do FastAPI cria a pool a partir de `DATABASE_URL`, aplica o esquema e a injeta nas
  dependências; fecha a pool no shutdown. Valor inválido falha explicitamente.
- Testes unitários seguem usando memória; os repositórios Postgres têm testes de integração
  (`make test-integration`, requer `make up`).

## Consequências

- Agentes e artefatos sobrevivem a restarts quando `PERSISTENCE_BACKEND=postgres`.
- Falha de conexão no startup derruba a aplicação (fail fast), sem fallback silencioso para memória.
