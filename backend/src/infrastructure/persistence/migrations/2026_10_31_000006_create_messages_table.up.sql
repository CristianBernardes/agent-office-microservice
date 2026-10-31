-- Chat: usuário↔agentes, agentes↔agentes, reuniões e comentários de tarefa.
CREATE TABLE messages (
    message_id   UUID PRIMARY KEY,
    session_id   UUID NOT NULL REFERENCES sessions (session_id) ON DELETE CASCADE,
    meeting_id   UUID REFERENCES meetings (meeting_id) ON DELETE SET NULL,
    task_id      UUID REFERENCES tasks (task_id) ON DELETE SET NULL,
    reply_to_id  UUID REFERENCES messages (message_id) ON DELETE SET NULL,
    sender_id    UUID REFERENCES agents (agent_id) ON DELETE SET NULL,     -- NULL = usuário
    recipient_id UUID REFERENCES agents (agent_id) ON DELETE SET NULL,     -- NULL = broadcast
    topic        TEXT,
    kind         TEXT NOT NULL DEFAULT 'chat'
                     CHECK (kind IN ('chat', 'thought', 'system', 'question', 'decision')),
    content      TEXT NOT NULL,
    event_id     UUID UNIQUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX messages_session_idx ON messages (session_id, created_at);
CREATE INDEX messages_meeting_idx ON messages (meeting_id, created_at);
CREATE INDEX messages_task_idx ON messages (task_id, created_at);
CREATE INDEX messages_content_trgm_idx ON messages USING gin (content gin_trgm_ops);
