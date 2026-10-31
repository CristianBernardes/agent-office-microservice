import { describe, expect, it, vi } from 'vitest'
import { ApiError, createApiClient } from './api'

function reply(body: unknown, status = 200) {
  return vi.fn().mockImplementation(async () => new Response(JSON.stringify(body), { status }))
}

describe('createApiClient', () => {
  it('lista agentes enviando Accept-Language', async () => {
    const fetchMock = reply([{ agent_id: '1' }])
    const api = createApiClient('http://api', () => 'en', fetchMock)
    expect(await api.listAgents()).toEqual([{ agent_id: '1' }])
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('http://api/agents')
    expect(init.headers['Accept-Language']).toBe('en')
  })

  it('cria objetivo com POST', async () => {
    const fetchMock = reply({ goal_id: 'g' }, 201)
    await createApiClient('http://api', () => 'pt', fetchMock).createGoal('entregar')
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('http://api/goals')
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body)).toEqual({ text: 'entregar' })
  })

  it('move tarefa e limita atividade', async () => {
    const fetchMock = reply({})
    const api = createApiClient('http://api', () => 'pt', fetchMock)
    await api.moveTask('t1', { to_status: 'done', actor_id: 'a', actor_role: 'qa_engineer' })
    await api.listActivity(20)
    expect(fetchMock.mock.calls[0][0]).toBe('http://api/tasks/t1/move')
    expect(fetchMock.mock.calls[1][0]).toBe('http://api/activity?limit=20')
  })

  it('lista objetivos e mensagens da sessão', async () => {
    const fetchMock = reply([])
    const api = createApiClient('http://api', () => 'pt', fetchMock)
    await api.listGoals()
    await api.listMessages('s1')
    expect(fetchMock.mock.calls[0][0]).toBe('http://api/goals')
    expect(fetchMock.mock.calls[1][0]).toBe('http://api/sessions/s1/messages')
  })

  it('cria tarefa', async () => {
    const fetchMock = reply({}, 201)
    const input = { title: 'T', description: '', priority: 'low' as const, actor_id: 'a', actor_role: 'product_owner' as const }
    await createApiClient('http://api', () => 'pt', fetchMock).createTask(input)
    expect(fetchMock.mock.calls[0][0]).toBe('http://api/tasks')
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual(input)
  })

  it('contrata agente', async () => {
    const fetchMock = reply({}, 201)
    const input = { name: 'Ana', role: 'dev_senior' as const, llm_model: 'm' }
    await createApiClient('http://api', () => 'pt', fetchMock).hireAgent(input)
    expect(fetchMock.mock.calls[0][0]).toBe('http://api/agents')
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual(input)
  })

  it('lança ApiError em resposta de erro', async () => {
    const api = createApiClient('http://api', () => 'pt', reply({ detail: 'x' }, 422))
    await expect(api.listTasks()).rejects.toBeInstanceOf(ApiError)
  })
})
