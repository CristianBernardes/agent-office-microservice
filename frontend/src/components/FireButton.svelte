<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Agent } from '../lib/types'
  import ConfirmModal from './ConfirmModal.svelte'

  let { agent, onfire }: { agent: Agent; onfire: (agent: Agent) => Promise<void> } = $props()

  let confirming = $state(false)
  let failed = $state(false)

  // Bloco: demitir é irreversível na tela, então passa sempre pela confirmação.
  async function confirm() {
    confirming = false
    failed = false
    try {
      await onfire(agent)
    } catch {
      failed = true
    }
  }
</script>

<button type="button" class="fire" onclick={() => (confirming = true)} aria-label={`${i18n.t.fire}: ${agent.name}`}>
  {i18n.t.fire}
</button>
{#if failed}<span role="alert" class="error">{i18n.t.loadError}</span>{/if}
{#if confirming}
  <ConfirmModal
    title={i18n.t.fireTitle}
    message={i18n.t.fireMessage.replace('{name}', agent.name)}
    confirmLabel={i18n.t.fireConfirm}
    cancelLabel={i18n.t.cancel}
    onconfirm={confirm}
    oncancel={() => (confirming = false)}
  />
{/if}

<style>
  .fire {
    background: transparent;
    color: #ef5350;
    border: 1px solid #ef5350;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 12px;
    cursor: pointer;
  }
  .fire:hover {
    background: rgba(239, 83, 80, 0.15);
  }
  .error {
    color: #ef5350;
    font-size: 12px;
    margin-left: 6px;
  }
</style>
