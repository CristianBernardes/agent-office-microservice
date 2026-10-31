-- Reuniões e cerimônias (planning, daily, retro...); a conversa fica em messages.meeting_id.
CREATE TABLE meetings (
    meeting_id   UUID PRIMARY KEY,
    goal_id      UUID REFERENCES goals (goal_id) ON DELETE SET NULL,
    kind         TEXT NOT NULL CHECK (kind IN (
                     'planning', 'refinement', 'daily', 'review', 'retrospective', 'brainstorm')),
    title        TEXT NOT NULL,
    organizer_id UUID REFERENCES agents (agent_id) ON DELETE SET NULL,
    status       TEXT NOT NULL DEFAULT 'scheduled'
                     CHECK (status IN ('scheduled', 'in_progress', 'done', 'cancelled')),
    summary      TEXT,
    decisions    JSONB NOT NULL DEFAULT '[]',
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at   TIMESTAMPTZ,
    ended_at     TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX meetings_goal_idx ON meetings (goal_id);

CREATE TABLE meeting_participants (
    meeting_id UUID NOT NULL REFERENCES meetings (meeting_id) ON DELETE CASCADE,
    agent_id   UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    joined_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (meeting_id, agent_id)
);
CREATE INDEX meeting_participants_agent_idx ON meeting_participants (agent_id);
