<script lang="ts">
  import { donationMethod } from '../lib/donation'
  import { i18n } from '../lib/i18n.svelte'

  let { paypalUrl, pixLabel, onclose }: { paypalUrl: string; pixLabel: string; onclose: () => void } = $props()

  const method = $derived(donationMethod(i18n.language, paypalUrl))
</script>

<div class="backdrop" role="presentation">
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="donation-title">
    <h2 id="donation-title">{i18n.t.donationTitle}</h2>
    <p>{i18n.t.donationThanks}</p>
    {#if method === 'pix'}
      <p>{i18n.t.donationPix}</p>
      <img src="/images/pix-qr-code.jpeg" alt={`QR code ${pixLabel}`} width="240" />
    {/if}
    {#if paypalUrl}
      <p>{i18n.t.donationPaypal}</p>
      <a class="paypal" href={paypalUrl} target="_blank" rel="noopener noreferrer">
        {i18n.t.donationPaypalButton}
      </a>
    {/if}
    <button type="button" onclick={onclose}>{i18n.t.donationLater}</button>
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
    max-width: 360px;
    text-align: center;
  }
  img {
    border-radius: 8px;
    background: #fff;
    padding: 6px;
  }
  .paypal {
    display: inline-block;
    background: #0070ba;
    color: #fff;
    padding: 10px 18px;
    border-radius: 6px;
    text-decoration: none;
    margin: 8px 0;
  }
  button {
    display: block;
    margin: 12px auto 0;
    background: transparent;
    color: inherit;
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
  }
</style>
