-- Extensões, tipos de domínio reutilizáveis e helper de updated_at (ADR-017/018).
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE DOMAIN agent_role AS TEXT CHECK (VALUE IN (
    'product_owner', 'scrum_master', 'tech_lead', 'dev_senior', 'dev_junior',
    'qa_engineer', 'data_analyst', 'hr_manager', 'product_consultant'));

-- Colunas do Kanban: o próprio status é a coluna do quadro.
CREATE DOMAIN task_status AS TEXT CHECK (VALUE IN (
    'backlog', 'todo', 'in_progress', 'testing', 'in_review', 'done', 'blocked'));

CREATE DOMAIN priority_level AS TEXT CHECK (VALUE IN ('low', 'medium', 'high', 'urgent'));

CREATE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
