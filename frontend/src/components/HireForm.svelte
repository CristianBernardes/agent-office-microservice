<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import { ROLES, type HireAgentInput, type Role } from '../lib/types'

  let {
    defaultModel,
    models = [],
    onsubmit,
  }: { defaultModel: string; models?: string[]; onsubmit: (input: HireAgentInput) => Promise<void> } = $props()

  let name = $state('')
  let role = $state<Role>('dev_senior')
  // svelte-ignore state_referenced_locally
  let model = $state(defaultModel)
  let done = $state(false)
  let failed = $state(false)

  const defaultTeam: Role[] = ['product_owner', 'scrum_master', 'tech_lead', 'dev_senior', 'dev_junior', 'qa_engineer']

  async function hireTeam() {
    done = false
    failed = false
    try {
      for (const r of defaultTeam) await onsubmit({ name: i18n.t.roles[r], role: r, llm_model: model.trim() })
      done = true
    } catch {
      failed = true
    }
  }

  async function submit(event: SubmitEvent) {
    event.preventDefault()
    if (!name.trim() || !model.trim()) return
    done = false
    failed = false
    try {
      await onsubmit({ name: name.trim(), role, llm_model: model.trim() })
      name = ''
      done = true
    } catch {
      failed = true
    }
  }
</script>

<form class="panel" onsubmit={submit}>
  <h2>{i18n.t.hireTitle}</h2>
  <div class="row">
    <input bind:value={name} placeholder={i18n.t.hireName} aria-label={i18n.t.hireName} />
    <select bind:value={role} aria-label={i18n.t.hireRole}>
      {#each ROLES as r (r)}<option value={r}>{i18n.t.roles[r]}</option>{/each}
    </select>
    {#if models.length > 0}
      <select bind:value={model} aria-label={i18n.t.hireModel}>
        {#each models.includes(model) ? models : [model, ...models] as m (m)}<option value={m}>{m}</option>{/each}
      </select>
    {:else}
      <input bind:value={model} aria-label={i18n.t.hireModel} />
    {/if}
    <button type="submit" disabled={!name.trim() || !model.trim()}>{i18n.t.hireSubmit}</button>
    <button type="button" disabled={!model.trim()} onclick={hireTeam}>{i18n.t.hireTeam}</button>
  </div>
  {#if done}<p role="status">{i18n.t.hireDone}</p>{/if}
  {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
</form>

<style>
  .row { display: flex; gap: 8px; flex-wrap: wrap; }
  input, select { background: var(--bg); color: inherit; border: 1px solid var(--border); border-radius: 6px; padding: 8px; }
  button { background: var(--accent); color: #fff; border: 0; padding: 8px 14px; border-radius: 6px; cursor: pointer; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
