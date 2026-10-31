ALTER TABLE agents DROP CONSTRAINT IF EXISTS agents_current_task_fk;
DROP TABLE IF EXISTS task_transitions;
DROP TABLE IF EXISTS task_dependencies;
DROP TABLE IF EXISTS tasks;
