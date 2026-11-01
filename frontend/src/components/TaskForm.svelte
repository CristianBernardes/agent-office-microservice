<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Priority } from '../lib/types'

  let {
    hasAgents,
    onsubmit,
  }: { hasAgents: boolean; onsubmit: (title: string, description: string, priority: Priority) => Promise<void> } =
    $props()

  let title = $state('')
  let description = $state('')
  let priority = $state<Priority>('medium')
  let done = $state(false)
  let failed = $state(false)
  const priorities: Priority[] = ['low', 'medium', 'high', 'urgent']

  async function submit(event: SubmitEvent) {
    event.preventDefault()
    if (!title.trim() || !hasAgents) return
    done = false
    failed = false
    try {
      await onsubmit(title.trim(), description.trim(), priority)
      title = ''
      description = ''
      done = true
    } catch {
      failed = true
    }
  }
</script>

<form class="panel" onsubmit={submit}>
  <h2>{i18n.t.taskFormTitle}</h2>
  <input bind:value={title} placeholder={i18n.t.taskName} aria-label={i18n.t.taskName} />
  <textarea rows="3" bind:value={description} placeholder={i18n.t.taskDescription} aria-label={i18n.t.taskDescription}
  ></textarea>
  <select bind:value={priority} aria-label="priority">
    {#each priorities as p (p)}<option value={p}>{i18n.t.priority[p]}</option>{/each}
  </select>
  <button type="submit" disabled={!title.trim() || !hasAgents}>{i18n.t.taskCreate}</button>
  {#if !hasAgents}<p>{i18n.t.taskNeedsAgent}</p>{/if}
  {#if done}<p role="status">{i18n.t.taskCreated}</p>{/if}
  {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
</form>

<style>
  input,
  textarea,
  select {
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 8px;
    background: var(--bg);
    color: inherit;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px;
  }
  button {
    background: var(--accent);
    color: #fff;
    border: 0;
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
  }
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
