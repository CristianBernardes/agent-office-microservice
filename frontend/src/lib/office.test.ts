import { describe, expect, it, vi } from 'vitest'
import type { ApiClient } from './api'
import { OfficeStore } from './office.svelte'
import type { Agent, Task } from './types'

const agent = (id: string): Agent => ({
  agent_id: id, name: id, role: 'dev_senior', status: 'idle', llm_model: 'm',
})
const task = (id: string, status: Task['status']): Task => ({
  task_id: id, title: id, description: '', status, priority: 'low', assigned_to: null, result: null,
  created_at: '2026-01-01T00:00:00Z', started_at: null, completed_at: null,
})

function fakeApi(overrides: Partial<ApiClient> = {}): ApiClient {
  return {
    listAgents: vi.fn().mockResolvedValue([agent('a1')]),
    listTasks: vi.fn().mockResolvedValue([task('t1', 'todo')]),
    listActivity: vi.fn().mockResolvedValue([]),
    listGoals: vi.fn().mockResolvedValue([]),
    listMessages: vi.fn().mockResolvedValue([]),
    createGoal: vi.fn(),
    moveTask: vi.fn(),
    createTask: vi.fn(),
    hireAgent: vi.fn(),
    listModels: vi.fn(),
    setOfficeLanguage: vi.fn(),
    ...overrides,
  }
}

describe('OfficeStore', () => {
  it('carrega dados iniciais', async () => {
    const store = new OfficeStore()
    await store.load(fakeApi())
    expect(store.agents).toHaveLength(1)
    expect(store.tasksByStatus('todo')).toHaveLength(1)
    expect(store.error).toBe(false)
  })

  it('marca erro quando a API falha', async () => {
    const store = new OfficeStore()
    await store.load(fakeApi({ listAgents: vi.fn().mockRejectedValue(new Error('x')) }))
    expect(store.error).toBe(true)
  })

  it('aplica status e pensamento em tempo real', async () => {
    const store = new OfficeStore()
    await store.load(fakeApi())
    store.apply({ kind: 'status', agentId: 'a1', status: 'working' })
    store.apply({ kind: 'thought', agentId: 'a1', text: 'hmm' })
    store.apply({ kind: 'action', agentId: 'a1', payload: {} })
    expect(store.agents[0].status).toBe('working')
    expect(store.thoughts.a1).toBe('hmm')
  })

  it('carrega as mensagens da sessão do objetivo mais recente', async () => {
    const store = new OfficeStore()
    const listMessages = vi.fn().mockResolvedValue([{ message_id: 'm1' }])
    const goals = [{ session_id: 's1' }, { session_id: 's2' }]
    await store.load(fakeApi({ listGoals: vi.fn().mockResolvedValue(goals), listMessages }))
    expect(listMessages).toHaveBeenCalledWith('s2')
    expect(store.messages).toHaveLength(1)
  })

  it('gera logs em tempo real (mais recente primeiro, limitado) e seleciona agente', async () => {
    const store = new OfficeStore()
    await store.load(fakeApi())
    store.apply({ kind: 'status', agentId: 'a1', status: 'working' })
    store.apply({ kind: 'action', agentId: 'a1', payload: { tool: 'x' } })
    expect(store.logs[0].text).toContain('tool')
    for (let i = 0; i < 120; i++) store.apply({ kind: 'thought', agentId: 'a1', text: `t${i}` })
    expect(store.logs).toHaveLength(100)
    store.select('a1')
    expect(store.selectedAgentId).toBe('a1')
  })

  it('lista tarefas atribuídas a um agente', async () => {
    const store = new OfficeStore()
    await store.load(fakeApi())
    store.replaceTask({ ...task('t1', 'todo'), assigned_to: 'a1' })
    expect(store.tasksOf('a1')).toHaveLength(1)
    expect(store.tasksOf('zz')).toHaveLength(0)
  })

  it('substitui tarefa movida', async () => {
    const store = new OfficeStore()
    await store.load(fakeApi())
    store.replaceTask(task('t1', 'done'))
    expect(store.tasksByStatus('done')).toHaveLength(1)
    expect(store.tasksByStatus('todo')).toHaveLength(0)
  })
})
