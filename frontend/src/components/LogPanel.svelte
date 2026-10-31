<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { LogLine } from '../lib/logs'
  import type { Agent } from '../lib/types'

  let { lines, agents }: { lines: LogLine[]; agents: Agent[] } = $props()

  const nameOf = (id: string | null) => agents.find((a) => a.agent_id === id)?.name ?? i18n.t.system
  const time = (iso: string) => new Date(iso).toLocaleTimeString(i18n.language)
</script>

<section class="panel" aria-label={i18n.t.logs}>
  <h2>{i18n.t.logs}</h2>
  {#if lines.length === 0}
    <p class="empty">{i18n.t.noLogs}</p>
  {:else}
    <ul>
      {#each lines as line (line.id)}
        <li>
          <time>{time(line.at)}</time>
          <strong>{nameOf(line.agentId)}</strong>
          <span class="text">{line.text}</span>
        </li>
      {/each}
    </ul>
  {/if}
</section>

<style>
  ul { list-style: none; margin: 0; padding: 0; max-height: 300px; overflow: auto; font-family: ui-monospace, monospace; }
  li { display: flex; gap: 8px; padding: 3px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
  time { opacity: 0.6; flex: none; }
  strong { flex: none; }
  .text { opacity: 0.85; word-break: break-word; }
  .empty { opacity: 0.7; }
</style>
