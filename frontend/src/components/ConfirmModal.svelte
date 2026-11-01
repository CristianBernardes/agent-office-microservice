<script lang="ts">
  let {
    title,
    message,
    confirmLabel,
    cancelLabel,
    onconfirm,
    oncancel,
  }: {
    title: string
    message: string
    confirmLabel: string
    cancelLabel: string
    onconfirm: () => void
    oncancel: () => void
  } = $props()

  function onkeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') oncancel()
  }

  function focusFirst(node: HTMLElement) {
    node.focus()
  }
</script>

<svelte:window {onkeydown} />

<div class="backdrop" role="presentation" onclick={(e) => e.target === e.currentTarget && oncancel()}>
  <div
    class="modal"
    role="alertdialog"
    aria-modal="true"
    aria-labelledby="confirm-title"
    aria-describedby="confirm-message"
  >
    <div class="icon" aria-hidden="true">⚠</div>
    <h2 id="confirm-title">{title}</h2>
    <p id="confirm-message">{message}</p>
    <div class="actions">
      <button type="button" class="ghost" onclick={oncancel} use:focusFirst>{cancelLabel}</button>
      <button type="button" class="primary" onclick={onconfirm}>{confirmLabel}</button>
    </div>
  </div>
</div>

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    z-index: 20;
    display: grid;
    place-items: center;
    background: rgba(8, 10, 15, 0.7);
    backdrop-filter: blur(3px);
  }
  .modal {
    width: min(440px, calc(100vw - 32px));
    padding: 28px 24px 22px;
    text-align: center;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.55);
  }
  .icon {
    width: 48px;
    height: 48px;
    margin: 0 auto 12px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: rgba(255, 193, 7, 0.15);
    color: #ffc107;
    font-size: 24px;
  }
  h2 {
    margin: 0 0 8px;
    font-size: 1.15rem;
  }
  p {
    margin: 0 0 22px;
    line-height: 1.5;
    opacity: 0.85;
    font-size: 0.95rem;
  }
  .actions {
    display: flex;
    gap: 10px;
    justify-content: center;
  }
  button {
    flex: 1;
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid var(--border);
    color: inherit;
  }
  .ghost {
    background: transparent;
  }
  .ghost:hover {
    background: rgba(255, 255, 255, 0.06);
  }
  .primary {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
  }
  .primary:hover {
    filter: brightness(1.12);
  }
  button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
