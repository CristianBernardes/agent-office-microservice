<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import { agingMs, computeMetrics, formatDuration, isWipExceeded, type WipLimits } from '../lib/metrics'
  import { KANBAN_COLUMNS, type Agent, type Task, type TaskStatus } from '../lib/types'

  let {
    tasks,
    agents,
    onmove,
    wipLimits = {},
  }: {
    tasks: Task[]
    agents: Agent[]
    onmove: (task: Task, to: TaskStatus, actor: Agent) => Promise<void>
    wipLimits?: WipLimits
  } = $props()

  let now = $state(Date.now())
  $effect(() => {
    const timer = setInterval(() => (now = Date.now()), 30000)
    return () => clearInterval(timer)
  })
  const itemsOf = (column: TaskStatus) => tasks.filter((t) => t.status === column)
  const exceeded = (column: TaskStatus) => isWipExceeded(itemsOf(column).length, wipLimits[column])
  const metrics = $derived(computeMetrics(tasks, wipLimits, now))

  let failed = $state(false)
  const actorOf = (task: Task) => agents.find((a) => a.agent_id === task.assigned_to)

  async function move(task: Task, to: TaskStatus) {
    const actor = actorOf(task)
    if (!actor || to === task.status) return
    failed = false
    try {
      await onmove(task, to, actor)
    } catch {
      failed = true
    }
  }
</script>

<section class="panel" aria-label={i18n.t.board}>
  <h2>{i18n.t.board}</h2>
  <div class="metrics" data-testid="flow-metrics">
    <span title={i18n.t.metrics.wip} class:alert={metrics.wipViolations.length > 0}>{i18n.t.metrics.wip}: <b>{metrics.wip}</b></span>
    <span>{i18n.t.metrics.throughput}: <b>{metrics.throughput}</b></span>
    <span>{i18n.t.metrics.leadTime}: <b>{formatDuration(metrics.leadTimeAvgMs)}</b></span>
    <span>{i18n.t.metrics.leadP85}: <b>{formatDuration(metrics.leadTimeP85Ms)}</b></span>
    <span>{i18n.t.metrics.cycleTime}: <b>{formatDuration(metrics.cycleTimeAvgMs)}</b></span>
    <span>{i18n.t.metrics.aging}: <b>{formatDuration(metrics.oldestAgingMs)}</b></span>
  </div>
  {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
  <div class="columns">
    {#each KANBAN_COLUMNS as column (column)}
      <div class="column" data-testid={`column-${column}`}>
        <h3 class:alert={exceeded(column)} title={exceeded(column) ? i18n.t.metrics.wipExceeded : ''}>
          {i18n.t.taskStatus[column]}
          <span class="count" data-testid={`count-${column}`}>{itemsOf(column).length}{wipLimits[column] ? `/${wipLimits[column]}` : ''}</span>
        </h3>
        {#each itemsOf(column) as task (task.task_id)}
          <article class="card">
            <strong>{task.title}</strong>
            <span class="owner">
              {actorOf(task)?.name ?? i18n.t.unassigned}{#if actorOf(task)} · {i18n.t.roles[actorOf(task)!.role]}{/if}
            </span>
            {#if agingMs(task, now) !== null}
              <span class="aging">⏱ {formatDuration(agingMs(task, now))}</span>
            {/if}
            <span class="prio prio-{task.priority}">{i18n.t.priority[task.priority]}</span>
            <select
              aria-label={`${task.title}: ${i18n.t.board}`}
              value={task.status}
              disabled={!actorOf(task)}
              onchange={(e) => move(task, e.currentTarget.value as TaskStatus)}
            >
              {#each KANBAN_COLUMNS as option (option)}
                <option value={option}>{i18n.t.taskStatus[option]}</option>
              {/each}
            </select>
          </article>
        {/each}
      </div>
    {/each}
  </div>
</section>

<style>
  .columns { display: grid; grid-template-columns: repeat(6, minmax(150px, 1fr)); gap: 10px; overflow-x: auto; }
  .column { background: var(--bg); border-radius: 8px; padding: 8px; min-height: 80px; }
  h3 { margin: 0 0 8px; font-size: 13px; opacity: 0.8; }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 8px; margin-bottom: 8px; display: flex; flex-direction: column; gap: 4px; font-size: 13px; }
  .owner { font-size: 12px; opacity: 0.75; }
  .prio { font-size: 11px; opacity: 0.8; }
  .prio-urgent, .prio-high { color: #ff8a65; }
  .metrics { display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px; margin-bottom: 10px; opacity: 0.9; }
  .alert { color: #ff5252; }
  .count { font-weight: normal; opacity: 0.8; margin-left: 4px; }
  .aging { font-size: 11px; opacity: 0.7; }
  select { background: var(--bg); color: inherit; border: 1px solid var(--border); border-radius: 4px; }
</style>
