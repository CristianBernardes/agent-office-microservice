import { describe, expect, it } from 'vitest'
import { MAP_WIDTH, placeAgents } from './layout'
import type { Agent } from './types'

const agent = (id: string, role: Agent['role']): Agent => ({
  agent_id: id, name: id, role, status: 'idle', llm_model: 'm',
})

describe('placeAgents', () => {
  it('posiciona em porcentagem do mapa', () => {
    const [p] = placeAgents([agent('a', 'dev_senior')])
    expect(p.left).toBeCloseTo((570 / MAP_WIDTH) * 100)
    expect(p.top).toBeGreaterThan(0)
  })

  it('desloca agentes repetidos do mesmo papel', () => {
    const [first, second] = placeAgents([agent('a', 'qa_engineer'), agent('b', 'qa_engineer')])
    expect(second.left).toBeGreaterThan(first.left)
    expect(second.top).toBe(first.top)
  })
})
