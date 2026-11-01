import type { ApiClient } from "./api";
import type { RealtimeEvent } from "./realtime";
import type {
  ActivityEvent,
  Agent,
  ChatMessage,
  DismissalProposal,
  Task,
} from "./types";

const ACTIVITY_LIMIT = 50;
const LOG_LIMIT = 100;

export interface LogEntry {
  id: number;
  at: string;
  agentId: string;
  text: string;
}

// Bloco: estado reativo do escritório (Svelte 5 runes); recebe REST inicial e eventos em tempo real.
export class OfficeStore {
  agents = $state<Agent[]>([]);
  tasks = $state<Task[]>([]);
  activity = $state<ActivityEvent[]>([]);
  messages = $state<ChatMessage[]>([]);
  logs = $state<LogEntry[]>([]);
  thoughts = $state<Record<string, string>>({});
  selectedAgentId = $state<string | null>(null);
  sessionId = $state<string | null>(null);
  dismissals = $state<DismissalProposal[]>([]);
  connected = $state(false);
  error = $state(false);
  private logSeq = 0;

  // Bloco: carga/atualização via REST; as mensagens vêm da sessão do objetivo mais recente.
  async load(api: ApiClient): Promise<void> {
    try {
      const [agents, tasks, activity, goals, dismissals] = await Promise.all([
        api.listAgents(),
        api.listTasks(),
        api.listActivity(ACTIVITY_LIMIT),
        api.listGoals(),
        api.listPendingDismissals(),
      ]);
      this.agents = agents;
      this.tasks = tasks;
      this.activity = activity;
      this.dismissals = dismissals;
      this.sessionId =
        goals.length > 0 ? goals[goals.length - 1].session_id : null;
      this.messages =
        this.sessionId !== null ? await api.listMessages(this.sessionId) : [];
      this.error = false;
    } catch {
      this.error = true;
    }
  }

  apply(event: RealtimeEvent): void {
    if (event.kind === "status") {
      this.agents = this.agents.map((a) =>
        a.agent_id === event.agentId ? { ...a, status: event.status } : a,
      );
      this.log(event.agentId, `status: ${event.status}`);
    } else if (event.kind === "thought") {
      this.thoughts = { ...this.thoughts, [event.agentId]: event.text };
      this.log(event.agentId, event.text);
    } else {
      this.log(event.agentId, JSON.stringify(event.payload));
    }
  }

  private log(agentId: string, text: string): void {
    const entry = {
      id: this.logSeq++,
      at: new Date().toISOString(),
      agentId,
      text,
    };
    this.logs = [entry, ...this.logs].slice(0, LOG_LIMIT);
  }

  select(agentId: string | null): void {
    this.selectedAgentId = agentId;
  }

  tasksOf(agentId: string): Task[] {
    return this.tasks.filter((t) => t.assigned_to === agentId);
  }

  replaceTask(task: Task): void {
    this.tasks = this.tasks.map((t) => (t.task_id === task.task_id ? task : t));
  }

  tasksByStatus(status: Task["status"]): Task[] {
    return this.tasks.filter((t) => t.status === status);
  }
}
