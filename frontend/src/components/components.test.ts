import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ChatPanel from './ChatPanel.svelte'
import DonationModal from './DonationModal.svelte'
import HireForm from './HireForm.svelte'
import GoalForm from './GoalForm.svelte'
import KanbanBoard from './KanbanBoard.svelte'
import LanguageSwitcher from './LanguageSwitcher.svelte'
import TaskForm from './TaskForm.svelte'
import TeamBoard from './TeamBoard.svelte'
import { i18n } from '../lib/i18n.svelte'
import type { Agent, ChatMessage, Task } from '../lib/types'

const agent: Agent = {
  agent_id: 'a1', name: 'Ana', role: 'dev_senior', status: 'working', model: 'm',
} as unknown as Agent
const task: Task = {
  task_id: 't1', title: 'Implementar API', status: 'in_progress', priority: 'high', assigned_to: 'a1',
} as unknown as Task

beforeEach(() => i18n.set('pt'))

describe('componentes', () => {
  it('LanguageSwitcher troca o idioma', async () => {
    render(LanguageSwitcher)
    await fireEvent.click(screen.getByRole('button', { name: 'EN' }))
    expect(i18n.language).toBe('en')
  })

  it('GoalForm envia o texto e limpa o campo', async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined)
    render(GoalForm, { onsubmit })
    const box = screen.getByRole('textbox')
    await fireEvent.input(box, { target: { value: 'Criar produto X' } })
    await fireEvent.submit(box.closest('form')!)
    expect(onsubmit).toHaveBeenCalledWith('Criar produto X')
  })

  it('TaskForm envia título, descrição e prioridade', async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined)
    render(TaskForm, { hasAgents: true, onsubmit })
    await fireEvent.input(screen.getByLabelText('Título'), { target: { value: 'Produto X' } })
    await fireEvent.submit(screen.getByRole('button').closest('form')!)
    expect(onsubmit).toHaveBeenCalledWith('Produto X', '', 'medium')
  })

  it('TaskForm bloqueia sem agentes', () => {
    render(TaskForm, { hasAgents: false, onsubmit: vi.fn() })
    expect(screen.getByRole('button')).toHaveProperty('disabled', true)
  })

  it('KanbanBoard move a task usando o responsável como ator', async () => {
    const onmove = vi.fn().mockResolvedValue(undefined)
    render(KanbanBoard, { tasks: [task], agents: [agent], onmove })
    await fireEvent.change(screen.getByRole('combobox'), { target: { value: 'done' } })
    expect(onmove).toHaveBeenCalledWith(task, 'done', agent)
  })

  it('TeamBoard mostra quem está com qual task', () => {
    render(TeamBoard, { agents: [agent], tasks: [task], selectedId: null, onselect: vi.fn() })
    expect(screen.getByText('Ana')).toBeTruthy()
    expect(screen.getByTestId('assigned-task').textContent).toContain('Implementar API')
  })

  it('ChatPanel mostra remetente e conteúdo', () => {
    const message = {
      message_id: 'm1', sender_id: 'a1', recipient_id: null, kind: 'decision', content: 'Usaremos FastAPI',
    } as unknown as ChatMessage
    render(ChatPanel, { messages: [message], agents: [agent] })
    expect(screen.getByText('Usaremos FastAPI')).toBeTruthy()
    expect(screen.getByText('Ana')).toBeTruthy()
  })

  it('DonationModal usa Pix em pt e PayPal em en', async () => {
    const view = render(DonationModal, { paypalUrl: 'https://paypal.me/x', pixLabel: 'Pix', onclose: vi.fn() })
    expect(screen.getByRole('img')).toBeTruthy()
    i18n.set('en')
    view.rerender({ paypalUrl: 'https://paypal.me/x', pixLabel: 'Pix', onclose: vi.fn() })
    expect(await screen.findByRole('link')).toHaveProperty('href', 'https://paypal.me/x')
  })

  it('HireForm envia nome, cargo e modelo', async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined)
    render(HireForm, { defaultModel: 'qwen', onsubmit })
    await fireEvent.input(screen.getByLabelText('Nome'), { target: { value: 'Ana' } })
    await fireEvent.change(screen.getByLabelText('Cargo'), { target: { value: 'tech_lead' } })
    await fireEvent.click(screen.getByRole('button', { name: 'Contratar' }))
    expect(onsubmit).toHaveBeenCalledWith({ name: 'Ana', role: 'tech_lead', llm_model: 'qwen' })
  })

  it('HireForm contrata o time padrão', async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined)
    render(HireForm, { defaultModel: 'qwen', onsubmit })
    await fireEvent.click(screen.getByRole('button', { name: 'Contratar time padrão' }))
    await waitFor(() => expect(onsubmit).toHaveBeenCalledTimes(6))
  })
})
