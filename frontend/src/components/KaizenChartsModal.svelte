<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import { formatDuration, kaizenCharts, type Bar } from '../lib/metrics'
  import type { Task } from '../lib/types'

  let { tasks, now, onclose }: { tasks: Task[]; now: number; onclose: () => void } = $props()
  const charts = $derived(kaizenCharts(tasks, now))
  const max = (bars: Bar[]) => Math.max(1, ...bars.map((b) => b.value))
  const labelOf = (label: string) =>
    label in i18n.t.taskStatus ? i18n.t.taskStatus[label as keyof typeof i18n.t.taskStatus] : label
</script>

{#snippet chart(title: string, bars: Bar[], format: (v: number) => string)}
  <h3>{title}</h3>
  {#if bars.length === 0}
    <p class="empty">{i18n.t.charts.empty}</p>
  {:else}
    {#each bars as bar (bar.label)}
      <div class="row">
        <span class="label" title={labelOf(bar.label)}>{labelOf(bar.label)}</span>
        <span class="track"><span class="fill" style:width={`${(bar.value / max(bars)) * 100}%`}></span></span>
        <span class="value">{format(bar.value)}</span>
      </div>
    {/each}
  {/if}
{/snippet}

<div class="backdrop" role="presentation">
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="charts-title" data-testid="kaizen-charts">
    <h2 id="charts-title">{i18n.t.charts.title}</h2>
    {@render chart(i18n.t.charts.flow, charts.wip, String)}
    {@render chart(i18n.t.charts.lead, charts.leadTimes, formatDuration)}
    {@render chart(i18n.t.charts.aging, charts.agings, formatDuration)}
    <button type="button" onclick={onclose}>{i18n.t.charts.close}</button>
  </div>
</div>

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: grid;
    place-items: center;
    z-index: 10;
  }
  .modal {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    width: min(640px, 92vw);
    max-height: 85vh;
    overflow: auto;
  }
  h3 {
    margin: 14px 0 6px;
    font-size: 14px;
  }
  .row {
    display: grid;
    grid-template-columns: 140px 1fr 60px;
    gap: 8px;
    align-items: center;
    font-size: 12px;
    margin: 3px 0;
  }
  .label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .track {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    height: 10px;
  }
  .fill {
    display: block;
    height: 100%;
    background: var(--accent);
    border-radius: 4px;
  }
  .value {
    text-align: right;
  }
  .empty {
    opacity: 0.7;
    font-size: 12px;
  }
  button {
    display: block;
    margin: 14px auto 0;
    background: transparent;
    color: inherit;
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
  }
</style>
