-- Quadro Kanban: tarefas com atores por etapa, dependências e trilha de transições.
CREATE TABLE tasks (
    task_id        UUID PRIMARY KEY,
    goal_id        UUID REFERENCES goals (goal_id) ON DELETE SET NULL,
    parent_task_id UUID REFERENCES tasks (task_id) ON DELETE CASCADE,
    title          TEXT NOT NULL,
    description    TEXT NOT NULL DEFAULT '',
    status         task_status NOT NULL DEFAULT 'backlog',
    priority       priority_level NOT NULL DEFAULT 'medium',
    created_by     UUID REFERENCES agents (agent_id) ON DELETE SET NULL,  -- NULL = usuário
    assigned_to    UUID REFERENCES agents (agent_id) ON DELETE SET NULL,  -- executor
    reviewer_id    UUID REFERENCES agents (agent_id) ON DELETE SET NULL,  -- QA / tech lead
    blocked_reason TEXT,
    result         TEXT,
    position       INTEGER NOT NULL DEFAULT 0,
    event_id       UUID UNIQUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at     TIMESTAMPTZ,
    completed_at   TIMESTAMPTZ,
    CHECK (reviewer_id IS NULL OR reviewer_id <> assigned_to),
    CHECK (status <> 'done' OR completed_at IS NOT NULL)
);
CREATE INDEX tasks_board_idx ON tasks (status, position);
CREATE INDEX tasks_assigned_idx ON tasks (assigned_to);
CREATE INDEX tasks_reviewer_idx ON tasks (reviewer_id);
CREATE INDEX tasks_goal_idx ON tasks (goal_id);
CREATE TRIGGER tasks_set_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE agents
    ADD CONSTRAINT agents_current_task_fk
    FOREIGN KEY (current_task_id) REFERENCES tasks (task_id) ON DELETE SET NULL;

CREATE TABLE task_dependencies (
    task_id       UUID NOT NULL REFERENCES tasks (task_id) ON DELETE CASCADE,
    depends_on_id UUID NOT NULL REFERENCES tasks (task_id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, depends_on_id),
    CHECK (task_id <> depends_on_id)
);

-- Histórico de cada movimento de cartão, com o ator da etapa.
CREATE TABLE task_transitions (
    transition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id       UUID NOT NULL REFERENCES tasks (task_id) ON DELETE CASCADE,
    from_status   task_status,
    to_status     task_status NOT NULL,
    actor_id      UUID REFERENCES agents (agent_id) ON DELETE SET NULL,
    actor_role    agent_role,
    note          TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX task_transitions_task_idx ON task_transitions (task_id, created_at);
