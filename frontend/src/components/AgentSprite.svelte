<script lang="ts">
  import { FRAME_HEIGHT, FRAME_WIDTH, spriteFor, type Direction } from '../lib/sprites'
  import type { Agent } from '../lib/types'

  let { agent, walking = false, hue = 0, alt = false, direction = 'down' }: { agent: Agent; walking?: boolean; hue?: number; alt?: boolean; direction?: Direction } =
    $props()
  const sheet = $derived(spriteFor(agent.role, agent.status, walking, alt, direction))
</script>

<span
  class="sprite"
  data-testid="sprite"
  data-sprite={sheet.url}
  style:--url={`url(${sheet.url})`}
  style:--frames={sheet.count}
  style:--start={sheet.start}
  style:--total={sheet.total}
  style:--w={`${FRAME_WIDTH}px`}
  style:--h={`${FRAME_HEIGHT}px`}
  style:filter={hue ? `hue-rotate(${hue}deg)` : undefined}
></span>

<style>
  .sprite {
    display: block;
    width: var(--w);
    height: var(--h);
    background: var(--url) calc(var(--start) * var(--w) * -1) 0 / calc(var(--total) * var(--w)) 100% no-repeat;
    image-rendering: pixelated;
    animation: play 1.2s steps(var(--frames), jump-none) infinite;
  }
  @keyframes play { to { background-position-x: calc((var(--start) + var(--frames) - 1) * var(--w) * -1); } }
  @media (prefers-reduced-motion: reduce) { .sprite { animation: none; } }
</style>
