<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Agent, DismissalProposal } from '../lib/types'

  let {
    proposal,
    target,
    proposer,
    ondecide,
  }: {
    proposal: DismissalProposal
    target: Agent | undefined
    proposer: Agent | undefined
    ondecide: (proposal: DismissalProposal, approved: boolean) => Promise<void>
  } = $props()

  let busy = $state(false)
  let failed = $state(false)

  const message = $derived(
    i18n.t.dismissalMessage
      .replace('{hr}', proposer?.name ?? i18n.t.roles.hr_manager)
      .replace('{name}', target?.name ?? '?')
      .replace('{role}', target ? i18n.t.roles[target.role] : '?'),
  )

  // Bloco: sem fechar no fundo nem no Esc — a proposta só some com uma decisão explícita.
  async function decide(approved: boolean) {
    busy = true
    failed = false
    try {
      await ondecide(proposal, approved)
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
    aria-labelledby="dismissal-title"
    aria-describedby="dismissal-message"
  >
    <div class="icon" aria-hidden="true">⚠</div>
    <h2 id="dismissal-title">{i18n.t.dismissalTitle}</h2>
    <p id="dismissal-message">{message}</p>
    <blockquote>
      <strong>{i18n.t.dismissalReason}</strong>
      <span data-testid="dismissal-reason">{proposal.reason}</span>
    </blockquote>
    {#if failed}<p role="alert" class="error">{i18n.t.loadError}</p>{/if}
    <div class="actions">
      <button type="button" class="ghost" disabled={busy} onclick={() => decide(false)}>{i18n.t.dismissalReject}</button
      >
      <button type="button" class="danger" disabled={busy} onclick={() => decide(true)}
        >{i18n.t.dismissalApprove}</button
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
    background: rgba(239, 83, 80, 0.15);
    color: #ef5350;
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
    margin: 0 0 18px;
    padding: 10px 12px;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: var(--bg);
    border-left: 3px solid #ffca28;
    border-radius: 6px;
    font-size: 0.92rem;
    white-space: pre-wrap;
  }
  .error {
    color: #ef5350;
  }
  .actions {
    display: flex;
    gap: 10px;
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
  .danger {
    background: #ef5350;
    border-color: #ef5350;
    color: #fff;
  }
</style>
