<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Agent, ChatMessage } from '../lib/types'

  let {
    messages,
    agents,
    canSend = false,
    onsend,
  }: {
    messages: ChatMessage[]
    agents: Agent[]
    canSend?: boolean
    onsend?: (content: string) => Promise<void>
  } = $props()

  let text = $state('')
  let failed = $state(false)

  const nameOf = (id: string | null) => agents.find((a) => a.agent_id === id)?.name ?? i18n.t.system

  // Bloco: o cliente (usuário) responde ao Product Owner pelo chat; a resposta vira contexto do time.
  async function send(event: SubmitEvent) {
    event.preventDefault()
    const value = text.trim()
    if (!value || !onsend) return
    failed = false
    try {
      await onsend(value)
      text = ''
    } catch {
      failed = true
    }
  }
</script>

<section class="panel" aria-label={i18n.t.chat}>
  <h2>{i18n.t.chat}</h2>
  {#if messages.length === 0}
    <p class="empty">{i18n.t.noMessages}</p>
  {:else}
    <ul>
      {#each messages as message (message.message_id)}
        <li class="kind-{message.kind}">
          <header>
            <strong>{nameOf(message.sender_id)}</strong>
            {#if message.recipient_id}<span class="to">→ {nameOf(message.recipient_id)}</span>{/if}
            <span class="badge">{i18n.t.messageKind[message.kind]}</span>
          </header>
          <p>{message.content}</p>
        </li>
      {/each}
    </ul>
  {/if}
  {#if onsend}
    <form onsubmit={send}>
      <input
        bind:value={text}
        placeholder={canSend ? i18n.t.chatPlaceholder : i18n.t.chatNeedsGoal}
        aria-label={i18n.t.chatPlaceholder}
        disabled={!canSend}
      />
      <button type="submit" disabled={!canSend || !text.trim()}>{i18n.t.chatSend}</button>
    </form>
    {#if failed}<p role="alert">{i18n.t.loadError}</p>{/if}
  {/if}
</section>

<style>
  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    max-height: 320px;
    overflow: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  li {
    background: var(--bg);
    border-radius: 8px;
    padding: 8px 10px;
    border-left: 3px solid var(--border);
  }
  li.kind-decision {
    border-left-color: #66bb6a;
  }
  li.kind-question {
    border-left-color: #ffca28;
  }
  li.kind-thought {
    opacity: 0.8;
    font-style: italic;
  }
  header {
    display: flex;
    gap: 6px;
    align-items: center;
    font-size: 12px;
  }
  .to {
    opacity: 0.7;
  }
  .badge {
    margin-left: auto;
    font-size: 11px;
    opacity: 0.7;
  }
  p {
    margin: 4px 0 0;
    font-size: 13px;
    white-space: pre-wrap;
  }
  .empty {
    opacity: 0.7;
  }
  form {
    display: flex;
    gap: 8px;
    margin-top: 10px;
  }
  input {
    flex: 1;
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
    border-radius: 6px;
    padding: 8px 14px;
    cursor: pointer;
  }
  button:disabled,
  input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
