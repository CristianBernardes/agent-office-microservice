import type { Task, TaskStatus } from './types'

export type WipLimits = Partial<Record<TaskStatus, number>>

export interface FlowMetrics {
  wip: number
  wipByColumn: Partial<Record<TaskStatus, number>>
  wipViolations: TaskStatus[]
  throughput: number
  leadTimeAvgMs: number | null
  leadTimeP85Ms: number | null
  cycleTimeAvgMs: number | null
  oldestAgingMs: number | null
}

const ACTIVE: readonly TaskStatus[] = ['in_progress', 'testing', 'in_review']

const ms = (iso: string | null): number | null => (iso ? new Date(iso).getTime() : null)

function average(values: number[]): number | null {
  return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null
}

export function percentile(values: number[], p: number): number | null {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  return sorted[Math.min(sorted.length - 1, Math.ceil(p * sorted.length) - 1)]
}

export function isWipExceeded(count: number, limit: number | undefined): boolean {
  return limit !== undefined && limit > 0 && count > limit
}

// Bloco: idade de um cartão em andamento (base do "aging WIP" do Kanban).
export function agingMs(task: Task, now: number): number | null {
  const start = ms(task.started_at)
  return start === null || !ACTIVE.includes(task.status) ? null : Math.max(0, now - start)
}

export function computeMetrics(tasks: Task[], limits: WipLimits, now: number): FlowMetrics {
  const wipByColumn: Partial<Record<TaskStatus, number>> = {}
  for (const status of ['todo', ...ACTIVE] as TaskStatus[]) {
    wipByColumn[status] = tasks.filter((t) => t.status === status).length
  }
  const done = tasks.filter((t) => t.status === 'done')
  const lead = done.flatMap((t) => {
    const end = ms(t.completed_at)
    return end === null ? [] : [end - new Date(t.created_at).getTime()]
  })
  const cycle = done.flatMap((t) => {
    const start = ms(t.started_at)
    const end = ms(t.completed_at)
    return start === null || end === null ? [] : [end - start]
  })
  const agings = tasks.flatMap((t) => agingMs(t, now) ?? [])
  return {
    wip: ACTIVE.reduce((sum, s) => sum + (wipByColumn[s] ?? 0), 0),
    wipByColumn,
    wipViolations: (Object.keys(wipByColumn) as TaskStatus[]).filter((s) =>
      isWipExceeded(wipByColumn[s] ?? 0, limits[s]),
    ),
    throughput: done.length,
    leadTimeAvgMs: average(lead),
    leadTimeP85Ms: percentile(lead, 0.85),
    cycleTimeAvgMs: average(cycle),
    oldestAgingMs: agings.length ? Math.max(...agings) : null,
  }
}

export function formatDuration(value: number | null): string {
  if (value === null) return '—'
  const minutes = Math.floor(value / 60000)
  if (minutes < 1) return '<1min'
  if (minutes < 60) return `${minutes}min`
  const hours = Math.floor(minutes / 60)
  return hours < 24 ? `${hours}h${String(minutes % 60).padStart(2, '0')}` : `${Math.floor(hours / 24)}d${hours % 24}h`
}

export interface Bar {
  label: string
  value: number
}

export interface KaizenCharts {
  wip: Bar[]
  leadTimes: Bar[]
  agings: Bar[]
}

// Bloco: dados dos gráficos Kaizen (fluxo por coluna, lead time concluído e idade dos cartões ativos).
export function kaizenCharts(tasks: Task[], now: number): KaizenCharts {
  const columns: TaskStatus[] = ['backlog', 'todo', ...ACTIVE, 'done']
  const leadTimes = tasks.flatMap((t) => {
    const end = ms(t.completed_at)
    return t.status === 'done' && end !== null
      ? [{ label: t.title, value: end - new Date(t.created_at).getTime() }]
      : []
  })
  const agings = tasks.flatMap((t) => {
    const age = agingMs(t, now)
    return age === null ? [] : [{ label: t.title, value: age }]
  })
  return {
    wip: columns.map((c) => ({ label: c, value: tasks.filter((t) => t.status === c).length })),
    leadTimes,
    agings: agings.sort((a, b) => b.value - a.value),
  }
}
