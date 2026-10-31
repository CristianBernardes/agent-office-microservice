<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import { KANBAN_COLUMNS, type Agent, type Task, type TaskStatus } from '../lib/types'

  let {
    tasks,
    agents,
    onmove,
  }: {
    tasks: Task[]
    agents: Agent[]
    onmove: (task: Task, to: TaskStatus, actor: Agent) => Promise<void>
  } = $props()

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
  {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
  <div class="columns">
    {#each KANBAN_COLUMNS as column (column)}
      <div class="column" data-testid={`column-${column}`}>
        <h3>{i18n.t.taskStatus[column]}</h3>
        {#each tasks.filter((t) => t.status === column) as task (task.task_id)}
          <article class="card">
            <strong>{task.title}</strong>
            <span class="owner">{actorOf(task)?.name ?? i18n.t.unassigned}</span>
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
  .columns { display: grid; grid-template-columns: repeat(5, minmax(150px, 1fr)); gap: 10px; overflow-x: auto; }
  .column { background: var(--bg); border-radius: 8px; padding: 8px; min-height: 80px; }
  h3 { margin: 0 0 8px; font-size: 13px; opacity: 0.8; }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 8px; margin-bottom: 8px; display: flex; flex-direction: column; gap: 4px; font-size: 13px; }
  .owner { font-size: 12px; opacity: 0.75; }
  .prio { font-size: 11px; opacity: 0.8; }
  .prio-urgent, .prio-high { color: #ff8a65; }
  select { background: var(--bg); color: inherit; border: 1px solid var(--border); border-radius: 4px; }
</style>
