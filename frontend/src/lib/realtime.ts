import mqtt, { type MqttClient } from 'mqtt'
import type { AgentStatus } from './types'

export type RealtimeEvent =
  | { kind: 'status'; agentId: string; status: AgentStatus }
  | { kind: 'thought'; agentId: string; text: string }
  | { kind: 'action'; agentId: string; payload: Record<string, unknown> }

export interface RealtimeHandlers {
  onEvent(event: RealtimeEvent): void
  onConnection(connected: boolean): void
}

export const AGENT_TOPICS = 'office/agents/+/+'

// Bloco: traduz tópico + envelope RFC-001 em evento tipado; mensagens inválidas são ignoradas.
export function parseMessage(topic: string, raw: string): RealtimeEvent | null {
  const [root, scope, agentId, kind] = topic.split('/')
  if (root !== 'office' || scope !== 'agents' || !agentId) return null
  let payload: unknown
  try {
    payload = (JSON.parse(raw) as { payload?: unknown }).payload
  } catch {
    return null
  }
  if (typeof payload !== 'object' || payload === null) return null
  const data = payload as Record<string, unknown>
  if (kind === 'status' && typeof data.status === 'string') {
    return { kind: 'status', agentId, status: data.status as AgentStatus }
  }
  if (kind === 'thought' && typeof data.thought === 'string') {
    return { kind: 'thought', agentId, text: data.thought }
  }
  if (kind === 'action') return { kind: 'action', agentId, payload: data }
  return null
}

export type MqttConnect = (url: string) => MqttClient

// Bloco: cliente MQTT sobre WebSocket; a função de conexão é injetável para testes.
export function connectRealtime(
  url: string,
  handlers: RealtimeHandlers,
  connect: MqttConnect = (u) => mqtt.connect(u),
): () => void {
  const client = connect(url)
  client.on('connect', () => {
    client.subscribe(AGENT_TOPICS, { qos: 1 })
    handlers.onConnection(true)
  })
  client.on('close', () => handlers.onConnection(false))
  client.on('message', (topic, message) => {
    const event = parseMessage(topic, message.toString())
    if (event) handlers.onEvent(event)
  })
  return () => client.end(true)
}
