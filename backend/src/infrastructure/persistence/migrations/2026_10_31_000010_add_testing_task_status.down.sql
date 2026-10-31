UPDATE tasks SET status = 'in_progress' WHERE status = 'testing';
ALTER DOMAIN task_status DROP CONSTRAINT task_status_check;
ALTER DOMAIN task_status ADD CONSTRAINT task_status_check CHECK (VALUE IN (
    'backlog', 'todo', 'in_progress', 'in_review', 'done', 'blocked'));
