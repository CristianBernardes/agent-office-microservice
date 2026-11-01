<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import { taskProgress } from '../lib/progress'
  import type { Agent, Task } from '../lib/types'
  import FireButton from './FireButton.svelte'

  let {
    agents,
    tasks,
    selectedId,
    onselect,
    onfire,
  }: {
    agents: Agent[]
    tasks: Task[]
    selectedId: string | null
    onselect: (agentId: string) => void
    onfire?: (agent: Agent) => Promise<void>
  } = $props()

  const tasksOf = (agentId: string) => tasks.filter((t) => t.assigned_to === agentId)
  const unassigned = $derived(tasks.filter((t) => !t.assigned_to))
</script>

<section class="panel" aria-label={i18n.t.team}>
  <h2>{i18n.t.team}</h2>
  {#if agents.length === 0}
    <p class="empty">{i18n.t.noAgents}</p>
  {/if}
  <ul>
    {#each agents as agent (agent.agent_id)}
      <li class:selected={selectedId === agent.agent_id}>
        <button type="button" class="who" onclick={() => onselect(agent.agent_id)}>
          <strong>{agent.name}</strong>
          <span>{i18n.t.roles[agent.role]}</span>
          <span class="status status-{agent.status}">{i18n.t.agentStatus[agent.status]}</span>
        </button>
        {#if onfire}<div class="fire-row"><FireButton {agent} {onfire} /></div>{/if}
        {#each tasksOf(agent.agent_id) as task (task.task_id)}
          <div class="task" data-testid="assigned-task">
            <span class="title">{task.title}</span>
            <span class="state">{i18n.t.taskStatus[task.status]}</span>
            <progress max="100" value={taskProgress(task.status)} aria-label={`${i18n.t.progress}: ${task.title}`}
            ></progress>
          </div>
        {:else}
          <p class="none">{i18n.t.noTasks}</p>
        {/each}
      </li>
    {/each}
  </ul>
  {#if unassigned.length > 0}
    <h3>{i18n.t.unassigned}</h3>
    {#each unassigned as task (task.task_id)}
      <div class="task">
        <span class="title">{task.title}</span>
        <span class="state">{i18n.t.taskStatus[task.status]}</span>
      </div>
    {/each}
  {/if}
</section>

<style>
  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 360px;
    overflow: auto;
  }
  li {
    background: var(--bg);
    border-radius: 8px;
    padding: 8px;
    border: 1px solid transparent;
  }
  li.selected {
    border-color: var(--accent);
  }
  .who {
    display: flex;
    gap: 8px;
    align-items: baseline;
    width: 100%;
    background: none;
    border: 0;
    color: inherit;
    cursor: pointer;
    padding: 0;
    text-align: left;
  }
  .who span {
    font-size: 12px;
    opacity: 0.7;
  }
  .status {
    margin-left: auto;
  }
  .status-working,
  .status-thinking {
    color: #66bb6a;
    opacity: 1 !important;
  }
  .task {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 2px 8px;
    margin-top: 6px;
    font-size: 13px;
  }
  .state {
    font-size: 12px;
    opacity: 0.8;
  }
  progress {
    grid-column: 1 / -1;
    width: 100%;
    height: 6px;
    accent-color: var(--accent);
  }
  .fire-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 4px;
  }
  .none,
  .empty {
    font-size: 12px;
    opacity: 0.6;
    margin: 6px 0 0;
  }
  h3 {
    font-size: 13px;
    margin: 12px 0 4px;
    opacity: 0.8;
  }
</style>
