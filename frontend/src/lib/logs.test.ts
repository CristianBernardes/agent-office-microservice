import { describe, expect, it } from 'vitest'
import { mergeLogs } from './logs'

describe('mergeLogs', () => {
  it('ordena do mais recente ao mais antigo, unindo as duas fontes', () => {
    const lines = mergeLogs(
      [{ id: 1, at: '2026-01-01T10:00:02Z', agentId: 'a', text: 'ao vivo' }],
      [
        { event_id: 'e1', kind: 'task.moved', agent_id: 'a', payload: { to: 'done' }, created_at: '2026-01-01T10:00:03Z' },
        { event_id: 'e2', kind: 'hired', agent_id: null, payload: {}, created_at: '2026-01-01T10:00:01Z' },
      ],
    )
    expect(lines.map((l) => l.id)).toEqual(['e1', 'live-1', 'e2'])
    expect(lines[0].text).toBe('task.moved {"to":"done"}')
    expect(lines[2].text).toBe('hired')
  })
})
