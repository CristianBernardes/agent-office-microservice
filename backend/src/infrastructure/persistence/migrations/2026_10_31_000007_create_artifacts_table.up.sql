-- Metadados dos .md gerados pelos agentes (arquivo em workspace/projects/<goal_id>/, ADR-004).
CREATE TABLE artifacts (
    artifact_id   UUID PRIMARY KEY,
    goal_id       UUID REFERENCES goals (goal_id) ON DELETE SET NULL,
    task_id       UUID REFERENCES tasks (task_id) ON DELETE SET NULL,
    meeting_id    UUID REFERENCES meetings (meeting_id) ON DELETE SET NULL,
    author_id     UUID NOT NULL REFERENCES agents (agent_id) ON DELETE RESTRICT,
    title         TEXT NOT NULL,
    content       TEXT NOT NULL,
    artifact_type TEXT NOT NULL CHECK (artifact_type IN (
                      'backlog', 'sprint_planning', 'adr', 'design_doc', 'implementation',
                      'test_plan', 'bug_report', 'analysis', 'retrospective', 'user_story',
                      'onboarding')),
    path          TEXT NOT NULL UNIQUE,
    status        TEXT NOT NULL CHECK (status IN ('draft', 'in_review', 'approved', 'archived')),
    version       INTEGER NOT NULL DEFAULT 1,
    event_id      UUID UNIQUE,
    created_at    TIMESTAMPTZ NOT NULL,
    updated_at    TIMESTAMPTZ NOT NULL
);
CREATE INDEX artifacts_goal_idx ON artifacts (goal_id);
CREATE INDEX artifacts_task_idx ON artifacts (task_id);
CREATE INDEX artifacts_author_idx ON artifacts (author_id);
CREATE INDEX artifacts_search_trgm_idx ON artifacts USING gin ((title || ' ' || content) gin_trgm_ops);
