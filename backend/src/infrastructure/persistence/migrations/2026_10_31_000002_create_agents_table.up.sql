-- Agentes: identidade, personalidade (Big Five) e "vida" (atividade, humor, energia, estação).
CREATE TABLE agents (
    agent_id          UUID PRIMARY KEY,
    name              TEXT NOT NULL UNIQUE,
    role              agent_role NOT NULL,
    llm_model         TEXT NOT NULL,
    status            TEXT NOT NULL CHECK (status IN ('idle', 'thinking', 'working', 'talking', 'offline')),
    current_task_id   UUID,
    openness          DOUBLE PRECISION NOT NULL CHECK (openness BETWEEN 0 AND 1),
    conscientiousness DOUBLE PRECISION NOT NULL CHECK (conscientiousness BETWEEN 0 AND 1),
    extraversion      DOUBLE PRECISION NOT NULL CHECK (extraversion BETWEEN 0 AND 1),
    agreeableness     DOUBLE PRECISION NOT NULL CHECK (agreeableness BETWEEN 0 AND 1),
    neuroticism       DOUBLE PRECISION NOT NULL CHECK (neuroticism BETWEEN 0 AND 1),
    activity          TEXT NOT NULL DEFAULT 'at_desk' CHECK (activity IN (
                          'at_desk', 'in_meeting', 'walking', 'resting', 'researching', 'reading')),
    mood              REAL NOT NULL DEFAULT 0 CHECK (mood BETWEEN -1 AND 1),
    energy            REAL NOT NULL DEFAULT 1 CHECK (energy BETWEEN 0 AND 1),
    station           TEXT,
    hired_by          UUID REFERENCES agents (agent_id) ON DELETE SET NULL,
    last_active_at    TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX agents_role_idx ON agents (role);
CREATE TRIGGER agents_set_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
