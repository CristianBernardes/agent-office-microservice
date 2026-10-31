<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Agent, ChatMessage } from '../lib/types'

  let { messages, agents }: { messages: ChatMessage[]; agents: Agent[] } = $props()

  const nameOf = (id: string | null) => agents.find((a) => a.agent_id === id)?.name ?? i18n.t.system
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
</section>

<style>
  ul { list-style: none; margin: 0; padding: 0; max-height: 320px; overflow: auto; display: flex; flex-direction: column; gap: 8px; }
  li { background: var(--bg); border-radius: 8px; padding: 8px 10px; border-left: 3px solid var(--border); }
  li.kind-decision { border-left-color: #66bb6a; }
  li.kind-question { border-left-color: #ffca28; }
  li.kind-thought { opacity: 0.8; font-style: italic; }
  header { display: flex; gap: 6px; align-items: center; font-size: 12px; }
  .to { opacity: 0.7; }
  .badge { margin-left: auto; font-size: 11px; opacity: 0.7; }
  p { margin: 4px 0 0; font-size: 13px; white-space: pre-wrap; }
  .empty { opacity: 0.7; }
</style>
