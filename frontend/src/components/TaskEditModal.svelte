<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Agent, Priority, Task } from '../lib/types'
  import { PRIORITIES } from '../lib/types'

  let {
    task,
    agents,
    onsave,
    onclose,
  }: {
    task: Task
    agents: Agent[]
    onsave: (task: Task, changes: { owner?: string; priority?: Priority }) => Promise<void>
    onclose: () => void
  } = $props()

  // svelte-ignore state_referenced_locally
  let owner = $state(task.assigned_to ?? '')
  // svelte-ignore state_referenced_locally
  let priority = $state<Priority>(task.priority)
  let failed = $state(false)

  // Bloco: só envia o que mudou, para não gerar histórico desnecessário.
  async function save(event: SubmitEvent) {
    event.preventDefault()
    const changes: { owner?: string; priority?: Priority } = {}
    if (owner && owner !== task.assigned_to) changes.owner = owner
    if (priority !== task.priority) changes.priority = priority
    failed = false
    try {
      if (changes.owner || changes.priority) await onsave(task, changes)
      onclose()
    } catch {
      failed = true
    }
  }

  function onkeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') onclose()
  }
</script>

<svelte:window {onkeydown} />

<div class="backdrop" role="presentation" onclick={(e) => e.target === e.currentTarget && onclose()}>
  <div class="modal" role="dialog" aria-modal="true" aria-label={i18n.t.taskEdit}>
    <form onsubmit={save}>
      <h2>{i18n.t.taskEdit}</h2>
      <p class="title">{task.title}</p>
      {#if task.description}<p class="desc">{task.description}</p>{/if}
      <label>
        {i18n.t.taskOwner}
        <select bind:value={owner}>
          {#if !task.assigned_to}<option value="">{i18n.t.unassigned}</option>{/if}
          {#each agents as a (a.agent_id)}
            <option value={a.agent_id}>{a.name} · {i18n.t.roles[a.role]}</option>
          {/each}
        </select>
      </label>
      <label>
        {i18n.t.taskPriority}
        <select bind:value={priority}>
          {#each PRIORITIES as p (p)}<option value={p}>{i18n.t.priority[p]}</option>{/each}
        </select>
      </label>
      {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
      <div class="actions">
        <button type="button" class="ghost" onclick={onclose}>{i18n.t.cancel}</button>
        <button type="submit">{i18n.t.taskSave}</button>
      </div>
    </form>
  </div>
</div>

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    z-index: 20;
    display: grid;
    place-items: center;
    background: rgba(8, 10, 15, 0.7);
  }
  .modal {
    width: min(460px, calc(100vw - 32px));
    max-height: 90vh;
    overflow: auto;
    padding: 22px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
  }
  form {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  h2 {
    margin: 0;
    font-size: 1.1rem;
  }
  .title {
    margin: 0;
    font-weight: 600;
  }
  .desc {
    margin: 0;
    font-size: 13px;
    opacity: 0.75;
    white-space: pre-wrap;
    max-height: 120px;
    overflow: auto;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 13px;
  }
  select {
    background: var(--bg);
    color: inherit;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px;
  }
  .actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
  }
  button {
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    border: 1px solid var(--accent);
    background: var(--accent);
    color: #fff;
  }
  .ghost {
    background: transparent;
    border-color: var(--border);
    color: inherit;
  }
</style>
