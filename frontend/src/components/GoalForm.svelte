<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'

  let { onsubmit }: { onsubmit: (text: string) => Promise<void> } = $props()
  let text = $state('')
  let sent = $state(false)
  let failed = $state(false)

  async function submit(event: SubmitEvent) {
    event.preventDefault()
    const value = text.trim()
    if (!value) return
    sent = false
    failed = false
    try {
      await onsubmit(value)
      text = ''
      sent = true
    } catch {
      failed = true
    }
  }
</script>

<form class="panel" onsubmit={submit}>
  <h2>{i18n.t.goalTitle}</h2>
  <textarea rows="3" bind:value={text} placeholder={i18n.t.goalPlaceholder} aria-label={i18n.t.goalTitle}></textarea>
  <button type="submit" disabled={!text.trim()}>{i18n.t.goalSubmit}</button>
  {#if sent}<p role="status">{i18n.t.goalSent}</p>{/if}
  {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
</form>

<style>
  textarea {
    width: 100%;
    box-sizing: border-box;
    background: var(--bg);
    color: inherit;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px;
  }
  button {
    margin-top: 8px;
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
