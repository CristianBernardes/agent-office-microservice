-- Esquema do AgentOffice (idempotente) — ver ADR-014.
CREATE TABLE IF NOT EXISTS agents (
    agent_id          UUID PRIMARY KEY,
    name              TEXT NOT NULL,
    role              TEXT NOT NULL,
    llm_model         TEXT NOT NULL,
    status            TEXT NOT NULL,
    current_task_id   UUID,
    openness          DOUBLE PRECISION NOT NULL,
    conscientiousness DOUBLE PRECISION NOT NULL,
    extraversion      DOUBLE PRECISION NOT NULL,
    agreeableness     DOUBLE PRECISION NOT NULL,
    neuroticism       DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id   UUID PRIMARY KEY,
    title         TEXT NOT NULL,
    content       TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    path          TEXT NOT NULL,
    author_id     UUID NOT NULL,
    status        TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL,
    updated_at    TIMESTAMPTZ NOT NULL
);
