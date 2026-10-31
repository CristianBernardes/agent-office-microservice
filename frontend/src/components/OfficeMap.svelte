<script lang="ts">
  import AgentSprite from './AgentSprite.svelte'
  import { i18n } from '../lib/i18n.svelte'
  import { MAP_HEIGHT, MAP_WIDTH, placeAgents } from '../lib/layout'
  import type { Agent } from '../lib/types'

  let {
    agents,
    thoughts,
    selectedId,
    onselect,
  }: {
    agents: Agent[]
    thoughts: Record<string, string>
    selectedId: string | null
    onselect: (agentId: string) => void
  } = $props()
  const placements = $derived(placeAgents(agents))
</script>

<section class="map-wrap" aria-label={i18n.t.office}>
  <div class="map" style:aspect-ratio={`${MAP_WIDTH} / ${MAP_HEIGHT}`}>
    {#each placements as { agent, left, top } (agent.agent_id)}
      <button
        type="button"
        class="agent"
        class:selected={selectedId === agent.agent_id}
        style:left={`${left}%`}
        style:top={`${top}%`}
        title={`${agent.name} — ${i18n.t.agentStatus[agent.status]}`}
        onclick={() => onselect(agent.agent_id)}
      >
        {#if thoughts[agent.agent_id]}
          <span class="bubble" role="status">{thoughts[agent.agent_id]}</span>
        {/if}
        <AgentSprite {agent} />
        <span class="name">{agent.name}</span>
      </button>
    {/each}
  </div>
  {#if agents.length === 0}
    <p class="empty">{i18n.t.noAgents}</p>
  {/if}
</section>

<style>
  .map-wrap { position: relative; }
  .map {
    position: relative; width: 100%;
    background: url('/images/sprites/office/escritorio_moderno.png') center / 100% 100% no-repeat;
    image-rendering: pixelated; border-radius: 8px; overflow: hidden;
  }
  .agent {
    position: absolute; transform: translate(-50%, -100%) scale(0.7); transform-origin: bottom center;
    display: flex; flex-direction: column; align-items: center;
    background: none; border: 0; padding: 0; color: inherit; cursor: pointer;
  }
  .agent.selected .name { background: var(--accent); }
  .name {
    font-size: 12px; background: rgba(0, 0, 0, 0.7); color: #fff; padding: 1px 6px;
    border-radius: 4px; white-space: nowrap; margin-top: 2px;
  }
  .bubble {
    position: absolute; bottom: 110%; width: max-content; max-width: 220px;
    background: #fff; color: #111; font-size: 12px; padding: 6px 8px; border-radius: 8px;
    overflow: hidden; display: -webkit-box; -webkit-line-clamp: 4; line-clamp: 4; -webkit-box-orient: vertical;
  }
  .empty { text-align: center; opacity: 0.7; }
</style>
