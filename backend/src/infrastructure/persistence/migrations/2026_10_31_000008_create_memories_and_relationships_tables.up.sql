-- Memória semântica (pgvector, 768 dims = nomic-embed-text) e vínculos entre agentes.
CREATE TABLE memories (
    memory_id        UUID PRIMARY KEY,
    agent_id         UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    session_id       UUID REFERENCES sessions (session_id) ON DELETE SET NULL,
    goal_id          UUID REFERENCES goals (goal_id) ON DELETE SET NULL,
    content          TEXT NOT NULL,
    memory_type      TEXT NOT NULL DEFAULT 'observation' CHECK (memory_type IN (
                         'observation', 'reflection', 'conversation', 'decision', 'fact')),
    importance       REAL NOT NULL DEFAULT 0.5 CHECK (importance BETWEEN 0 AND 1),
    embedding        vector(768),
    event_id         UUID UNIQUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_accessed_at TIMESTAMPTZ
);
CREATE INDEX memories_agent_idx ON memories (agent_id, created_at DESC);
CREATE INDEX memories_embedding_idx ON memories USING hnsw (embedding vector_cosine_ops);

-- Um par, uma linha: agent_a < agent_b.
CREATE TABLE relationships (
    agent_a             UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    agent_b             UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    score               REAL NOT NULL DEFAULT 0 CHECK (score BETWEEN -1 AND 1),
    status              TEXT NOT NULL DEFAULT 'stranger' CHECK (status IN (
                            'stranger', 'acquaintance', 'colleague', 'friend', 'rival')),
    interactions        INTEGER NOT NULL DEFAULT 0 CHECK (interactions >= 0),
    last_interaction_at TIMESTAMPTZ,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (agent_a, agent_b),
    CHECK (agent_a < agent_b)
);
CREATE TRIGGER relationships_set_updated_at BEFORE UPDATE ON relationships
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
