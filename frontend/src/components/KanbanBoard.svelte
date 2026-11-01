<script lang="ts">
  import KaizenChartsModal from './KaizenChartsModal.svelte'
  import TaskEditModal from './TaskEditModal.svelte'
  import { i18n } from '../lib/i18n.svelte'
  import { agingMs, computeMetrics, formatDuration, isWipExceeded, type WipLimits } from '../lib/metrics'
  import { KANBAN_COLUMNS, PRIORITIES, type Agent, type Priority, type Task, type TaskStatus } from '../lib/types'

  let {
    tasks,
    agents,
    onmove,
    onupdate,
    wipLimits = {},
  }: {
    tasks: Task[]
    agents: Agent[]
    onmove: (task: Task, to: TaskStatus, actor: Agent) => Promise<void>
    onupdate?: (task: Task, changes: { owner?: string; priority?: Priority }) => Promise<void>
    wipLimits?: WipLimits
  } = $props()

  let now = $state(Date.now())
  $effect(() => {
    const timer = setInterval(() => (now = Date.now()), 30000)
    return () => clearInterval(timer)
  })
  // Bloco: dentro da coluna, as mais prioritárias ficam no topo (ordem estável por prioridade).
  const itemsOf = (column: TaskStatus) =>
    tasks
      .filter((t) => t.status === column)
      .sort((a, b) => PRIORITIES.indexOf(a.priority) - PRIORITIES.indexOf(b.priority))
  const exceeded = (column: TaskStatus) => isWipExceeded(itemsOf(column).length, wipLimits[column])
  const metrics = $derived(computeMetrics(tasks, wipLimits, now))

  let showCharts = $state(false)
  let failed = $state(false)
  let editing = $state<Task | null>(null)
  let draggingId = $state<string | null>(null)
  let overColumn = $state<TaskStatus | null>(null)

  const active = $derived(agents.filter((a) => a.status !== 'offline'))
  const actorOf = (task: Task) => agents.find((a) => a.agent_id === task.assigned_to)
  // Bloco: o dono do produto move qualquer cartão; o ator registrado é o responsável (ou o PO).
  const actorFor = (task: Task) => {
    const owner = actorOf(task)
    if (owner && owner.status !== 'offline') return owner
    return active.find((a) => a.role === 'product_owner') ?? active[0]
  }

  async function move(task: Task, to: TaskStatus) {
    const actor = actorFor(task)
    if (!actor || to === task.status) return
    failed = false
    try {
      await onmove(task, to, actor)
    } catch {
      failed = true
    }
  }

  function dragStart(event: DragEvent, task: Task) {
    draggingId = task.task_id
    event.dataTransfer?.setData('text/plain', task.task_id)
    if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move'
  }

  function dragEnd() {
    draggingId = null
    overColumn = null
  }

  async function drop(event: DragEvent, column: TaskStatus) {
    event.preventDefault()
    const id = event.dataTransfer?.getData('text/plain') || draggingId
    dragEnd()
    const task = tasks.find((t) => t.task_id === id)
    if (task) await move(task, column)
  }

  async function saveEdit(task: Task, changes: { owner?: string; priority?: Priority }) {
    await onupdate?.(task, changes)
  }
</script>

<section class="panel" aria-label={i18n.t.board}>
  <h2>{i18n.t.board}</h2>
  <div class="metrics" data-testid="flow-metrics">
    <span title={i18n.t.metrics.wip} class:alert={metrics.wipViolations.length > 0}
      >{i18n.t.metrics.wip}: <b>{metrics.wip}</b></span
    >
    <span>{i18n.t.metrics.throughput}: <b>{metrics.throughput}</b></span>
    <span>{i18n.t.metrics.leadTime}: <b>{formatDuration(metrics.leadTimeAvgMs)}</b></span>
    <span>{i18n.t.metrics.leadP85}: <b>{formatDuration(metrics.leadTimeP85Ms)}</b></span>
    <span>{i18n.t.metrics.cycleTime}: <b>{formatDuration(metrics.cycleTimeAvgMs)}</b></span>
    <span>{i18n.t.metrics.aging}: <b>{formatDuration(metrics.oldestAgingMs)}</b></span>
    <button type="button" class="charts-btn" onclick={() => (showCharts = true)}>{i18n.t.charts.button}</button>
  </div>
  {#if showCharts}<KaizenChartsModal {tasks} {now} onclose={() => (showCharts = false)} />{/if}
  {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
  {#if editing}
    <TaskEditModal task={editing} agents={active} onsave={saveEdit} onclose={() => (editing = null)} />
  {/if}
  <div class="columns">
    {#each KANBAN_COLUMNS as column (column)}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div
        class="column"
        class:over={overColumn === column}
        data-testid={`column-${column}`}
        ondragover={(e) => {
          e.preventDefault()
          overColumn = column
        }}
        ondragleave={() => (overColumn = null)}
        ondrop={(e) => drop(e, column)}
      >
        <h3 class:alert={exceeded(column)} title={exceeded(column) ? i18n.t.metrics.wipExceeded : ''}>
          {i18n.t.taskStatus[column]}
          <span class="count" data-testid={`count-${column}`}
            >{itemsOf(column).length}{wipLimits[column] ? `/${wipLimits[column]}` : ''}</span
          >
        </h3>
        {#each itemsOf(column) as task (task.task_id)}
          <article
            class="card"
            class:dragging={draggingId === task.task_id}
            draggable="true"
            title={i18n.t.taskDragHint}
            ondragstart={(e) => dragStart(e, task)}
            ondragend={dragEnd}
          >
            <strong>{task.title}</strong>
            <span class="owner">
              {actorOf(task)?.name ?? i18n.t.unassigned}{#if actorOf(task)}
                · {i18n.t.roles[actorOf(task)!.role]}{/if}
            </span>
            {#if agingMs(task, now) !== null}
              <span class="aging">⏱ {formatDuration(agingMs(task, now))}</span>
            {/if}
            <span class="prio prio-{task.priority}">{i18n.t.priority[task.priority]}</span>
            {#if onupdate}
              <button type="button" class="edit" onclick={() => (editing = task)}>✎ {i18n.t.taskEdit}</button>
            {/if}
            <select
              aria-label={`${task.title}: ${i18n.t.board}`}
              value={task.status}
              disabled={!actorFor(task)}
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
  .charts-btn {
    background: transparent;
    color: inherit;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1px 8px;
    cursor: pointer;
  }
  .columns {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 8px;
    overflow-x: auto;
  }
  .column {
    background: var(--bg);
    border-radius: 8px;
    padding: 6px;
    min-height: 80px;
  }
  h3 {
    margin: 0 0 8px;
    font-size: 13px;
    opacity: 0.8;
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px;
    margin-bottom: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 13px;
  }
  .owner {
    font-size: 12px;
    opacity: 0.75;
  }
  .prio {
    font-size: 11px;
    opacity: 0.8;
  }
  .prio-urgent,
  .prio-high {
    color: #ff8a65;
  }
  .metrics {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    font-size: 12px;
    margin-bottom: 10px;
    opacity: 0.9;
  }
  .alert {
    color: #ff5252;
  }
  .count {
    font-weight: normal;
    opacity: 0.8;
    margin-left: 4px;
  }
  .aging {
    font-size: 11px;
    opacity: 0.7;
  }
  .column.over {
    outline: 2px dashed var(--accent);
  }
  .card {
    cursor: grab;
  }
  .card.dragging {
    opacity: 0.4;
  }
  .edit {
    align-self: flex-start;
    background: transparent;
    color: inherit;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 11px;
    cursor: pointer;
  }
  select {
    background: var(--bg);
    color: inherit;
    border: 1px solid var(--border);
    border-radius: 4px;
  }
</style>
