-- Sessão de trabalho e objetivos pedidos no chat (ex.: "venda 5 unidades/dia por R$ 39,90").
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    scenario   TEXT NOT NULL DEFAULT 'default',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at   TIMESTAMPTZ,
    highlights JSONB NOT NULL DEFAULT '[]'
);

CREATE TABLE goals (
    goal_id      UUID PRIMARY KEY,
    session_id   UUID REFERENCES sessions (session_id) ON DELETE SET NULL,
    requested_by UUID REFERENCES agents (agent_id) ON DELETE SET NULL,  -- NULL = usuário
    owner_id     UUID REFERENCES agents (agent_id) ON DELETE SET NULL,  -- normalmente o PO
    text         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'done', 'cancelled')),
    outcome      TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at    TIMESTAMPTZ,
    CHECK ((status = 'open') = (closed_at IS NULL))
);
CREATE INDEX goals_status_idx ON goals (status);
