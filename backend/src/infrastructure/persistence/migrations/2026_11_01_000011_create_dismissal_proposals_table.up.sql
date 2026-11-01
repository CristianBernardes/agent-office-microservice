-- Propostas de demissão feitas pelo RH e decididas pelo dono do produto (ADR-056).
CREATE TABLE dismissal_proposals (
    proposal_id UUID PRIMARY KEY,
    agent_id    UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    proposed_by UUID NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    reason      TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at  TIMESTAMPTZ
);
CREATE INDEX dismissal_proposals_status_idx ON dismissal_proposals (status, created_at);
CREATE INDEX dismissal_proposals_agent_idx ON dismissal_proposals (agent_id);
