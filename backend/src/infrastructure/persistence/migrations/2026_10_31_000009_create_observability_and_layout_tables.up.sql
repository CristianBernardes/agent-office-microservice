-- Auditoria de ferramentas, feed de atividade (SystemLog) e layout do escritório.
CREATE TABLE tool_invocations (
    invocation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id      UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    task_id       UUID REFERENCES tasks (task_id) ON DELETE SET NULL,
    tool          TEXT NOT NULL,
    arguments     JSONB NOT NULL DEFAULT '{}',
    result        TEXT,
    status        TEXT NOT NULL CHECK (status IN ('success', 'denied', 'failed')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX tool_invocations_agent_idx ON tool_invocations (agent_id, created_at DESC);

CREATE TABLE activity_events (
    event_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id   UUID REFERENCES agents (agent_id) ON DELETE SET NULL,
    kind       TEXT NOT NULL,
    payload    JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX activity_events_created_idx ON activity_events (created_at DESC);

CREATE TABLE office_layout (
    name       TEXT PRIMARY KEY,
    layout     JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER office_layout_set_updated_at BEFORE UPDATE ON office_layout
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
