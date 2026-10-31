<script lang="ts">
  import { i18n } from '../lib/i18n.svelte'
  import type { Language } from '../lib/types'

  let {
    onchange,
    confirmChange = (message: string) => window.confirm(message),
  }: { onchange?: (language: Language) => void; confirmChange?: (message: string) => boolean } = $props()

  const options: Language[] = ['pt', 'en']

  // Bloco: trava — trocar o idioma pode corromper arquivos já escritos, então exige confirmação.
  function choose(lang: Language) {
    if (lang === i18n.language || !confirmChange(i18n.t.languageWarning)) return
    i18n.set(lang)
    onchange?.(lang)
  }
</script>

<div class="switcher" role="group" aria-label={i18n.t.language}>
  {#each options as lang (lang)}
    <button
      type="button"
      class:active={i18n.language === lang}
      aria-pressed={i18n.language === lang}
      onclick={() => choose(lang)}
    >
      {lang.toUpperCase()}
    </button>
  {/each}
</div>

<style>
  .switcher { display: inline-flex; gap: 4px; }
  button {
    border: 1px solid var(--border); background: var(--panel); color: inherit;
    padding: 4px 10px; border-radius: 6px; cursor: pointer; font-weight: 600;
  }
  button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
</style>
