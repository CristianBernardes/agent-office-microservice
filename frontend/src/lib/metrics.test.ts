import { describe, expect, it } from 'vitest'
import type { Task } from './types'
import { agingMs, computeMetrics, formatDuration, isWipExceeded, percentile } from './metrics'

const T0 = new Date('2026-01-01T00:00:00Z').getTime()
const iso = (min: number) => new Date(T0 + min * 60000).toISOString()
const task = (status: Task['status'], over: Partial<Task> = {}): Task => ({
  task_id: Math.random().toString(),
  title: 't',
  description: '',
  status,
  priority: 'medium',
  assigned_to: null,
  result: null,
  created_at: iso(0),
  started_at: null,
  completed_at: null,
  ...over,
})

describe('metrics', () => {
  it('conta WIP e detecta violação de limite', () => {
    const tasks = [task('in_progress'), task('in_progress'), task('in_review'), task('backlog')]
    const m = computeMetrics(tasks, { in_progress: 1, in_review: 3 }, T0)
    expect(m.wip).toBe(3)
    expect(m.wipViolations).toEqual(['in_progress'])
  })

  it('limite 0 ou ausente não é violação', () => {
    expect(isWipExceeded(9, 0)).toBe(false)
    expect(isWipExceeded(9, undefined)).toBe(false)
    expect(isWipExceeded(6, 5)).toBe(true)
    expect(isWipExceeded(5, 5)).toBe(false)
  })

  it('calcula throughput, lead e cycle time', () => {
    const done = task('done', { started_at: iso(10), completed_at: iso(70) })
    const m = computeMetrics([done], {}, T0)
    expect(m.throughput).toBe(1)
    expect(m.leadTimeAvgMs).toBe(70 * 60000)
    expect(m.cycleTimeAvgMs).toBe(60 * 60000)
  })

  it('aging só vale para cartões em andamento ou revisão', () => {
    expect(agingMs(task('in_progress', { started_at: iso(0) }), T0 + 5 * 60000)).toBe(300000)
    expect(agingMs(task('todo', { started_at: iso(0) }), T0)).toBeNull()
  })

  it('percentil 85 e formatação', () => {
    expect(percentile([1, 2, 3, 4, 5, 6, 7], 0.85)).toBe(6)
    expect(percentile([], 0.85)).toBeNull()
    expect(formatDuration(null)).toBe('—')
    expect(formatDuration(30000)).toBe('<1min')
    expect(formatDuration(90 * 60000)).toBe('1h30')
  })
})
