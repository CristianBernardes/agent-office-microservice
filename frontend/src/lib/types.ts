export type Role =
  | 'product_owner'
  | 'scrum_master'
  | 'tech_lead'
  | 'dev_senior'
  | 'dev_junior'
  | 'qa_engineer'
  | 'data_analyst'
  | 'hr_manager'
  | 'product_consultant'

export type AgentStatus = 'idle' | 'thinking' | 'working' | 'talking' | 'offline'
export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'testing' | 'in_review' | 'done' | 'blocked'
export type Priority = 'low' | 'medium' | 'high' | 'urgent'
export type Language = 'pt' | 'en'

export interface Agent {
  agent_id: string
  name: string
  role: Role
  status: AgentStatus
  llm_model: string
}

export interface Task {
  task_id: string
  title: string
  description: string
  status: TaskStatus
  priority: Priority
  assigned_to: string | null
  result: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface Goal {
  goal_id: string
  session_id: string
  text: string
  status: string
}

export interface ActivityEvent {
  event_id: string
  kind: string
  agent_id: string | null
  payload: Record<string, unknown>
  created_at: string
}

export type MessageKind = 'chat' | 'thought' | 'system' | 'question' | 'decision'

export interface ChatMessage {
  message_id: string
  session_id: string
  sender_id: string | null
  recipient_id: string | null
  task_id: string | null
  kind: MessageKind
  content: string
}

export interface HireAgentInput {
  name: string
  role: Role
  llm_model: string
}

export interface MoveTaskInput {
  to_status: TaskStatus
  actor_id: string
  actor_role: Role
}

export const ROLES: readonly Role[] = [
  'product_owner',
  'scrum_master',
  'tech_lead',
  'dev_senior',
  'dev_junior',
  'qa_engineer',
  'data_analyst',
  'hr_manager',
  'product_consultant',
]

export const KANBAN_COLUMNS: readonly TaskStatus[] = [
  'backlog',
  'todo',
  'in_progress',
  'testing',
  'in_review',
  'done',
]
