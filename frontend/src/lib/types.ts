export type Role =
  | "product_owner"
  | "scrum_master"
  | "tech_lead"
  | "dev_senior"
  | "dev_junior"
  | "qa_engineer"
  | "data_analyst"
  | "hr_manager"
  | "product_consultant"
  | "dev_mid"
  | "database_administrator"
  | "devops_engineer"
  | "site_reliability_engineer"
  | "ux_ui_designer"
  | "business_analyst"
  | "software_architect"
  | "security_engineer"
  | "test_automation_engineer"
  | "data_engineer"
  | "ai_engineer"
  | "ml_engineer"
  | "systems_analyst"
  | "product_designer"
  | "technical_support"
  | "infrastructure_analyst"
  | "data_quality_analyst"
  | "engineering_manager";

export type AgentStatus =
  "idle" | "thinking" | "working" | "talking" | "offline";
export type TaskStatus =
  | "backlog"
  | "todo"
  | "in_progress"
  | "testing"
  | "in_review"
  | "done"
  | "blocked";
export type Priority = "low" | "medium" | "high" | "urgent";
export type Language = "pt" | "en";

export interface Agent {
  agent_id: string;
  name: string;
  role: Role;
  status: AgentStatus;
  llm_model: string;
}

export interface Task {
  task_id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  assigned_to: string | null;
  result: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface Goal {
  goal_id: string;
  session_id: string;
  text: string;
  status: string;
}

export interface ActivityEvent {
  event_id: string;
  kind: string;
  agent_id: string | null;
  payload: Record<string, unknown>;
  created_at: string;
}

export type MessageKind =
  "chat" | "thought" | "system" | "question" | "decision";

export interface ChatMessage {
  message_id: string;
  session_id: string;
  sender_id: string | null;
  recipient_id: string | null;
  task_id: string | null;
  kind: MessageKind;
  content: string;
}

export interface HireAgentInput {
  name: string;
  role: Role;
  llm_model: string;
}

export interface MoveTaskInput {
  to_status: TaskStatus;
  actor_id: string;
  actor_role: Role;
  owner_override?: boolean;
}

export interface ActorInput {
  actor_id: string;
  actor_role: Role;
}

// Bloco: papéis sem arte/assento próprio reutilizam os de um papel base (sprites e lugar no mapa).
export type BaseRole =
  | "product_owner"
  | "scrum_master"
  | "tech_lead"
  | "dev_senior"
  | "dev_junior"
  | "qa_engineer"
  | "data_analyst"
  | "hr_manager"
  | "product_consultant";

export const BASE_ROLE: Record<Role, BaseRole> = {
  product_owner: "product_owner",
  scrum_master: "scrum_master",
  tech_lead: "tech_lead",
  dev_senior: "dev_senior",
  dev_junior: "dev_junior",
  qa_engineer: "qa_engineer",
  data_analyst: "data_analyst",
  hr_manager: "hr_manager",
  product_consultant: "product_consultant",
  dev_mid: "dev_junior",
  database_administrator: "data_analyst",
  devops_engineer: "dev_senior",
  site_reliability_engineer: "dev_senior",
  ux_ui_designer: "product_consultant",
  business_analyst: "product_consultant",
  software_architect: "tech_lead",
  security_engineer: "tech_lead",
  test_automation_engineer: "qa_engineer",
  data_engineer: "data_analyst",
  ai_engineer: "dev_senior",
  ml_engineer: "data_analyst",
  systems_analyst: "product_consultant",
  product_designer: "product_consultant",
  technical_support: "dev_junior",
  infrastructure_analyst: "dev_senior",
  data_quality_analyst: "data_analyst",
  engineering_manager: "scrum_master",
};

export const ROLES: readonly Role[] = [
  "product_owner",
  "scrum_master",
  "tech_lead",
  "dev_senior",
  "dev_junior",
  "qa_engineer",
  "data_analyst",
  "hr_manager",
  "product_consultant",
  "dev_mid",
  "database_administrator",
  "devops_engineer",
  "site_reliability_engineer",
  "ux_ui_designer",
  "business_analyst",
  "software_architect",
  "security_engineer",
  "test_automation_engineer",
  "data_engineer",
  "ai_engineer",
  "ml_engineer",
  "systems_analyst",
  "product_designer",
  "technical_support",
  "infrastructure_analyst",
  "data_quality_analyst",
  "engineering_manager",
];

export const KANBAN_COLUMNS: readonly TaskStatus[] = [
  "backlog",
  "todo",
  "in_progress",
  "testing",
  "in_review",
  "done",
];

export const PRIORITIES: readonly Priority[] = [
  "urgent",
  "high",
  "medium",
  "low",
];

export interface HrChatReply {
  session_id: string;
  reply: ChatMessage;
}

export interface HiringProposal {
  proposal_id: string;
  role: Role;
  proposed_by: string;
  reason: string;
  task_id: string | null;
  status: "pending" | "approved" | "rejected";
  hired_agent_id: string | null;
  created_at: string;
  decided_at: string | null;
}

export interface DismissalProposal {
  proposal_id: string;
  agent_id: string;
  proposed_by: string;
  reason: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  decided_at: string | null;
}
