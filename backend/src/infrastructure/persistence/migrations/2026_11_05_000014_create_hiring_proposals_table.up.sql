-- Propostas de contratação feitas pelo RH e decididas pelo dono do produto.
CREATE TABLE hiring_proposals (
    proposal_id    UUID PRIMARY KEY,
    role           agent_role NOT NULL,
    proposed_by    UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    reason         TEXT NOT NULL,
    task_id        UUID REFERENCES tasks (task_id) ON DELETE SET NULL,
    status         TEXT NOT NULL DEFAULT 'pending'
                       CHECK (status IN ('pending', 'approved', 'rejected')),
    hired_agent_id UUID REFERENCES agents (agent_id) ON DELETE SET NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at     TIMESTAMPTZ
);
CREATE INDEX hiring_proposals_status_idx ON hiring_proposals (status, created_at);
