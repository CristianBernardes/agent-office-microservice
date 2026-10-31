-- Etapa de teste (ADR-050): amplia o domínio task_status com 'testing'.
ALTER DOMAIN task_status DROP CONSTRAINT task_status_check;
ALTER DOMAIN task_status ADD CONSTRAINT task_status_check CHECK (VALUE IN (
    'backlog', 'todo', 'in_progress', 'testing', 'in_review', 'done', 'blocked'));
