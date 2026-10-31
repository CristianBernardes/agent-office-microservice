import { describe, expect, it, vi } from 'vitest'
import type { MqttClient } from 'mqtt'
import { AGENT_TOPICS, connectRealtime, parseMessage } from './realtime'

const env = (payload: unknown) => JSON.stringify({ payload })

describe('parseMessage', () => {
  it('interpreta status, thought e action', () => {
    expect(parseMessage('office/agents/a1/status', env({ status: 'working' }))).toEqual({
      kind: 'status', agentId: 'a1', status: 'working',
    })
    expect(parseMessage('office/agents/a1/thought', env({ thought: 'ok' }))).toEqual({
      kind: 'thought', agentId: 'a1', text: 'ok',
    })
    expect(parseMessage('office/agents/a1/action', env({ tool: 'x' }))?.kind).toBe('action')
  })

  it('ignora tópicos e payloads inválidos', () => {
    expect(parseMessage('other/agents/a1/status', env({ status: 'idle' }))).toBeNull()
    expect(parseMessage('office/agents/a1/status', 'not json')).toBeNull()
    expect(parseMessage('office/agents/a1/status', env('x'))).toBeNull()
    expect(parseMessage('office/agents/a1/status', env({}))).toBeNull()
    expect(parseMessage('office/agents/a1/other', env({ a: 1 }))).toBeNull()
  })
})

describe('connectRealtime', () => {
  it('assina ao conectar, repassa eventos e encerra', () => {
    const listeners: Record<string, (...args: unknown[]) => void> = {}
    const client = {
      on: vi.fn((name: string, cb: (...args: unknown[]) => void) => { listeners[name] = cb }),
      subscribe: vi.fn(),
      end: vi.fn(),
    }
    const handlers = { onEvent: vi.fn(), onConnection: vi.fn() }
    const stop = connectRealtime('ws://x', handlers, () => client as unknown as MqttClient)

    listeners.connect()
    expect(client.subscribe).toHaveBeenCalledWith(AGENT_TOPICS, { qos: 1 })
    expect(handlers.onConnection).toHaveBeenLastCalledWith(true)

    listeners.message('office/agents/a1/status', Buffer.from(env({ status: 'idle' })))
    expect(handlers.onEvent).toHaveBeenCalledWith({ kind: 'status', agentId: 'a1', status: 'idle' })
    listeners.message('office/agents/a1/zzz', Buffer.from('{}'))
    expect(handlers.onEvent).toHaveBeenCalledTimes(1)

    listeners.close()
    expect(handlers.onConnection).toHaveBeenLastCalledWith(false)
    stop()
    expect(client.end).toHaveBeenCalledWith(true)
  })
})
