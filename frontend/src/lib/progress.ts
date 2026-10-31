import type { TaskStatus } from "./types";

// Bloco: andamento aproximado de uma tarefa a partir do seu status no fluxo.
const PROGRESS: Record<TaskStatus, number> = {
  backlog: 0,
  todo: 10,
  in_progress: 50,
  testing: 65,
  in_review: 80,
  done: 100,
  blocked: 30,
};

export function taskProgress(status: TaskStatus): number {
  return PROGRESS[status];
}
