<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Agent, HiringProposal } from '../lib/types'

  let {
    proposal,
    proposer,
    defaultModel,
    models = [],
    onapprove,
    onreject,
  }: {
    proposal: HiringProposal
    proposer: Agent | undefined
    defaultModel: string
    models?: string[]
    onapprove: (proposal: HiringProposal, name: string, model: string) => Promise<void>
    onreject: (proposal: HiringProposal) => Promise<void>
  } = $props()

  // svelte-ignore state_referenced_locally
  let name = $state(i18n.t.roles[proposal.role])
  // svelte-ignore state_referenced_locally
  let model = $state(defaultModel)
  let busy = $state(false)
  let failed = $state(false)

  const message = $derived(
    i18n.t.hiringMessage
      .replace('{hr}', proposer?.name ?? i18n.t.roles.hr_manager)
      .replace('{role}', i18n.t.roles[proposal.role]),
  )
  const canApprove = $derived(name.trim() !== '' && model.trim() !== '')

  // Bloco: sem fechar no fundo nem no Esc — a proposta só some com uma decisão explícita.
  async function run(action: () => Promise<void>) {
    busy = true
    failed = false
    try {
      await action()
    } catch {
      failed = true
    } finally {
      busy = false
    }
  }
</script>

<div class="backdrop" role="presentation">
  <div
    class="modal"
    role="alertdialog"
    aria-modal="true"
    aria-labelledby="hiring-title"
    aria-describedby="hiring-message"
  >
    <div class="icon" aria-hidden="true">＋</div>
    <h2 id="hiring-title">{i18n.t.hiringTitle}</h2>
    <p id="hiring-message">{message}</p>
    <blockquote>
      <strong>{i18n.t.hiringReason}</strong>
      <span data-testid="hiring-reason">{proposal.reason}</span>
    </blockquote>
    <label>
      <span>{i18n.t.hiringName}</span>
      <input bind:value={name} data-testid="hiring-name" />
    </label>
    <label>
      <span>{i18n.t.hiringModel}</span>
      {#if models.length > 0}
        <select bind:value={model} data-testid="hiring-model">
          {#each models.includes(model) ? models : [model, ...models] as m (m)}<option value={m}>{m}</option>{/each}
        </select>
      {:else}
        <input bind:value={model} data-testid="hiring-model" />
      {/if}
    </label>
    {#if failed}<p role="alert" class="error">{i18n.t.loadError}</p>{/if}
    <div class="actions">
      <button type="button" class="ghost" disabled={busy} onclick={() => run(() => onreject(proposal))}
        >{i18n.t.hiringReject}</button
      >
      <button
        type="button"
        class="primary"
        disabled={busy || !canApprove}
        onclick={() => run(() => onapprove(proposal, name.trim(), model.trim()))}>{i18n.t.hiringApprove}</button
      >
    </div>
  </div>
</div>

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    z-index: 30;
    display: grid;
    place-items: center;
    background: rgba(8, 10, 15, 0.75);
    backdrop-filter: blur(3px);
  }
  .modal {
    width: min(480px, calc(100vw - 32px));
    padding: 28px 24px 22px;
    text-align: center;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.55);
  }
  .icon {
    width: 48px;
    height: 48px;
    margin: 0 auto 12px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: rgba(102, 187, 106, 0.15);
    color: #66bb6a;
    font-size: 24px;
  }
  h2 {
    margin: 0 0 8px;
    font-size: 1.15rem;
  }
  p {
    margin: 0 0 14px;
    line-height: 1.5;
    opacity: 0.9;
  }
  blockquote {
    margin: 0 0 14px;
    padding: 10px 12px;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: var(--bg);
    border-left: 3px solid #66bb6a;
    border-radius: 6px;
    font-size: 0.92rem;
    white-space: pre-wrap;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 12px;
    text-align: left;
    font-size: 0.85rem;
  }
  input,
  select {
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--bg);
    color: inherit;
  }
  .error {
    color: #ef5350;
  }
  .actions {
    display: flex;
    gap: 10px;
    margin-top: 6px;
  }
  button {
    flex: 1;
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid var(--border);
    color: inherit;
  }
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .ghost {
    background: transparent;
  }
  .primary {
    background: #66bb6a;
    border-color: #66bb6a;
    color: #fff;
  }
</style>
