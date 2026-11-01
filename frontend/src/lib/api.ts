import type {
  ActivityEvent,
  ActorInput,
  Agent,
  ChatMessage,
  DismissalProposal,
  Goal,
  HireAgentInput,
  Language,
  MoveTaskInput,
  Priority,
  Role,
  Task,
} from "./types";

export type FetchLike = (
  input: string,
  init?: RequestInit,
) => Promise<Response>;

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export interface CreateTaskInput {
  title: string;
  description: string;
  priority: Priority;
  actor_id: string;
  actor_role: Role;
}

export interface ApiClient {
  listAgents(): Promise<Agent[]>;
  listTasks(): Promise<Task[]>;
  listActivity(limit: number): Promise<ActivityEvent[]>;
  listGoals(): Promise<Goal[]>;
  listMessages(sessionId: string): Promise<ChatMessage[]>;
  createGoal(text: string): Promise<Goal>;
  moveTask(taskId: string, input: MoveTaskInput): Promise<Task>;
  setTaskOwner(
    taskId: string,
    agentId: string,
    actor: ActorInput,
  ): Promise<Task>;
  setTaskPriority(
    taskId: string,
    priority: Priority,
    actor: ActorInput,
  ): Promise<Task>;
  fireAgent(agentId: string): Promise<Agent>;
  listPendingDismissals(): Promise<DismissalProposal[]>;
  decideDismissal(
    proposalId: string,
    approved: boolean,
  ): Promise<DismissalProposal>;
  sendMessage(sessionId: string, content: string): Promise<ChatMessage>;
  createTask(input: CreateTaskInput): Promise<Task>;
  hireAgent(input: HireAgentInput): Promise<Agent>;
  listModels(): Promise<string[]>;
  setOfficeLanguage(language: Language): Promise<void>;
}

// Bloco: cliente REST tipado; fetch e idioma são injetados para facilitar testes (DIP).
export function createApiClient(
  baseUrl: string,
  getLanguage: () => Language,
  fetchImpl: FetchLike = (input, init) => fetch(input, init),
): ApiClient {
  async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetchImpl(`${baseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "Accept-Language": getLanguage(),
        ...init.headers,
      },
    });
    if (!response.ok)
      throw new ApiError(response.status, await response.text());
    return (await response.json()) as T;
  }

  const post = <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) });

  return {
    listAgents: () => request<Agent[]>("/agents"),
    listTasks: () => request<Task[]>("/tasks"),
    listActivity: (limit) =>
      request<ActivityEvent[]>(`/activity?limit=${limit}`),
    listGoals: () => request<Goal[]>("/goals"),
    listMessages: (sessionId) =>
      request<ChatMessage[]>(`/sessions/${sessionId}/messages`),
    createGoal: (text) => post<Goal>("/goals", { text }),
    createTask: (input) => post<Task>("/tasks", input),
    listModels: () => request<string[]>("/models"),
    setOfficeLanguage: async (language) => {
      await request("/office/language", {
        method: "PUT",
        body: JSON.stringify({ language }),
      });
    },
    hireAgent: (input) => post<Agent>("/agents", input),
    moveTask: (taskId, input) => post<Task>(`/tasks/${taskId}/move`, input),
    setTaskOwner: (taskId, agentId, actor) =>
      request<Task>(`/tasks/${taskId}/owner`, {
        method: "PUT",
        body: JSON.stringify({ agent_id: agentId, ...actor }),
      }),
    setTaskPriority: (taskId, priority, actor) =>
      request<Task>(`/tasks/${taskId}/priority`, {
        method: "PUT",
        body: JSON.stringify({ priority, ...actor }),
      }),
    listPendingDismissals: () =>
      request<DismissalProposal[]>("/dismissals?pending_only=true"),
    decideDismissal: (proposalId, approved) =>
      post<DismissalProposal>(
        `/dismissals/${proposalId}/${approved ? "approve" : "reject"}`,
        {},
      ),
    fireAgent: (agentId) => post<Agent>(`/agents/${agentId}/fire`, {}),
    sendMessage: (sessionId, content) =>
      post<ChatMessage>("/messages", { session_id: sessionId, content }),
  };
}
