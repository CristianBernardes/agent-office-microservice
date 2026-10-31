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

import { hueFor, meetingPoint, pickMeeting } from './layout'

describe('vida no escritório', () => {
  const mk = (id: string, status = 'idle') => ({ agent_id: id, status }) as never
  it('hue difere por variante e é determinístico', () => {
    expect(hueFor(0)).toBe(0)
    expect(hueFor(1)).not.toBe(hueFor(2))
    expect(hueFor(1)).toBe(hueFor(1))
  })
  it('pickMeeting exige dois agentes livres', () => {
    expect(pickMeeting([mk('a')], new Set(), () => 0)).toBeNull()
    expect(pickMeeting([mk('a'), mk('b', 'offline')], new Set(), () => 0)).toBeNull()
    expect(pickMeeting([mk('a'), mk('b')], new Set(['b']), () => 0)).toBeNull()
    expect(pickMeeting([mk('a'), mk('b')], new Set(), () => 0)).toEqual({ walker: 'a', target: 'b' })
  })
  it('meetingPoint fica ao lado do colega', () => {
    expect(meetingPoint(10, 20).left).toBeGreaterThan(10)
    expect(meetingPoint(10, 20).top).toBe(20)
  })
})
