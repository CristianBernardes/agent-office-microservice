<script lang="ts">
  import { FRAME_HEIGHT, FRAME_WIDTH, spriteFor } from '../lib/sprites'
  import type { Agent } from '../lib/types'

  let { agent }: { agent: Agent } = $props()
  const sheet = $derived(spriteFor(agent.role, agent.status))
</script>

<span
  class="sprite"
  data-testid="sprite"
  data-sprite={sheet.url}
  style:--url={`url(${sheet.url})`}
  style:--frames={sheet.frames}
  style:--w={`${FRAME_WIDTH}px`}
  style:--h={`${FRAME_HEIGHT}px`}
></span>

<style>
  .sprite {
    display: block;
    width: var(--w);
    height: var(--h);
    background: var(--url) 0 0 / calc(var(--frames) * 100%) 100% no-repeat;
    image-rendering: pixelated;
    animation: play 1.2s steps(var(--frames), jump-none) infinite;
  }
  @keyframes play { to { background-position-x: 100%; } }
  @media (prefers-reduced-motion: reduce) { .sprite { animation: none; } }
</style>
