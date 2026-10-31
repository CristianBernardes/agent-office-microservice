-- ─────────────────────────────────────────────────────────────────────────
-- Inicialização do banco do AgentOffice Microservice.
--
-- Apenas as extensões (infraestrutura do banco). As tabelas vêm das migrações
-- em backend/src/infrastructure/persistence/migrations (ADR-018): `make migrate`.
-- ─────────────────────────────────────────────────────────────────────────

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
