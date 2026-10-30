-- ─────────────────────────────────────────────────────────────────────────
-- Inicialização do banco do AgentOffice Microservice.
--
-- Nesta rodada de implementação (Fase 0 + Fase 1 do plano de migração),
-- apenas a extensão pgvector é habilitada — ela é infraestrutura básica do
-- banco, não um recurso especulativo. As tabelas de domínio (agents, tasks,
-- artifacts, memories) são criadas via migrações nas fases seguintes, quando
-- os repositórios PostgreSQL concretos forem implementados (ver
-- docs/adr/006-postgresql-com-pgvector.md).
-- ─────────────────────────────────────────────────────────────────────────

CREATE EXTENSION IF NOT EXISTS vector;
