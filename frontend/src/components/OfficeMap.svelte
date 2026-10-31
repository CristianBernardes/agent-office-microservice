<script lang="ts">
  import AgentSprite from './AgentSprite.svelte'
  import { i18n } from '../lib/i18n.svelte'
  import { onMount } from 'svelte'
  import { MAP_HEIGHT, MAP_WIDTH, hueFor, meetingPoint, pickMeeting, placeAgents } from '../lib/layout'
  import type { Agent } from '../lib/types'

  let {
    agents,
    thoughts,
    selectedId,
    onselect,
    wanderIntervalMs = 0,
    walkMs = 3000,
    chatMs = 5000,
  }: {
    agents: Agent[]
    thoughts: Record<string, string>
    selectedId: string | null
    onselect: (agentId: string) => void
    wanderIntervalMs?: number
    walkMs?: number
    chatMs?: number
  } = $props()
  const placements = $derived(placeAgents(agents))

  // Bloco: caminhadas — um agente vai até um colega, conversa e volta à sua mesa.
  type Trip = { left: number; top: number; phase: 'walking' | 'chatting' | 'returning' }
  let trips = $state<Record<string, Trip>>({})
  const timers = new Set<ReturnType<typeof setTimeout>>()
  const later = (fn: () => void, ms: number) => {
    const t = setTimeout(() => {
      timers.delete(t)
      fn()
    }, ms)
    timers.add(t)
  }

  function startMeeting() {
    const meeting = pickMeeting(agents, new Set(Object.keys(trips)), Math.random)
    if (!meeting) return
    const dest = placements.find((p) => p.agent.agent_id === meeting.target)
    if (!dest) return
    const point = meetingPoint(dest.left, dest.top)
    const { walker } = meeting
    trips[walker] = { ...point, phase: 'walking' }
    later(() => (trips[walker] = { ...point, phase: 'chatting' }), walkMs)
    later(() => {
      const seat = placements.find((p) => p.agent.agent_id === walker)
      if (seat) trips[walker] = { left: seat.left, top: seat.top, phase: 'returning' }
    }, walkMs + chatMs)
    later(() => delete trips[walker], 2 * walkMs + chatMs)
  }

  // Bloco: a cada ciclo cada agente alterna entre a pose padrão e a alternativa (defasado por agente).
  let poseTick = $state(0)

  onMount(() => {
    const interval = wanderIntervalMs > 0 ? setInterval(startMeeting, wanderIntervalMs) : undefined
    const poses = wanderIntervalMs > 0 ? setInterval(() => poseTick++, wanderIntervalMs) : undefined
    return () => {
      clearInterval(interval)
      clearInterval(poses)
      timers.forEach(clearTimeout)
    }
  })
</script>

<section class="map-wrap" aria-label={i18n.t.office}>
  <div class="map" style:aspect-ratio={`${MAP_WIDTH} / ${MAP_HEIGHT}`}>
    {#each placements as { agent, left, top, variant } (agent.agent_id)}
      {@const trip = trips[agent.agent_id]}
      <button
        type="button"
        class="agent"
        class:selected={selectedId === agent.agent_id}
        class:moving={!!trip}
        style:--walk={`${walkMs}ms`}
        style:left={`${trip?.left ?? left}%`}
        style:top={`${trip?.top ?? top}%`}
        title={`${agent.name} — ${i18n.t.roles[agent.role]} — ${i18n.t.agentStatus[agent.status]}`}
        onclick={() => onselect(agent.agent_id)}
      >
        {#if thoughts[agent.agent_id]}
          <span class="bubble" role="status">{thoughts[agent.agent_id]}</span>
        {/if}
        <AgentSprite
          agent={trip?.phase === 'chatting' ? { ...agent, status: 'talking' } : agent}
          walking={trip?.phase === 'walking' || trip?.phase === 'returning'}
          hue={hueFor(variant)}
          alt={(poseTick + variant) % 2 === 1}
        />
        <span class="name">{agent.name}</span>
        <span class="role">{i18n.t.roles[agent.role]}</span>
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
  .agent.moving { transition: left var(--walk) linear, top var(--walk) linear; z-index: 2; }
  .role { font-size: 10px; background: rgba(0, 0, 0, 0.55); color: #ddd; padding: 0 5px; border-radius: 4px; white-space: nowrap; }
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
