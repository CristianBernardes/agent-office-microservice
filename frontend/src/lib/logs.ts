import type { ActivityEvent } from "./types";
import type { LogEntry } from "./office.svelte";

export interface LogLine {
  id: string;
  at: string;
  agentId: string | null;
  text: string;
}

// Bloco: une os logs em tempo real com a atividade persistida (mais recentes primeiro, sem repetir).
export function mergeLogs(
  live: readonly LogEntry[],
  persisted: readonly ActivityEvent[],
): LogLine[] {
  const fromLive: LogLine[] = live.map((l) => ({
    id: `live-${l.id}`,
    at: l.at,
    agentId: l.agentId,
    text: l.text,
  }));
  const fromApi: LogLine[] = persisted.map((e) => ({
    id: e.event_id,
    at: e.created_at,
    agentId: e.agent_id,
    text: `${e.kind} ${Object.keys(e.payload).length > 0 ? JSON.stringify(e.payload) : ""}`.trim(),
  }));
  return [...fromLive, ...fromApi].sort(
    (a, b) => Date.parse(b.at) - Date.parse(a.at),
  );
}
