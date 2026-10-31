import { describe, expect, it } from 'vitest'
import { donationMethod, markShown, readLastShown, shouldShowReminder } from './donation'

describe('donation', () => {
  it('escolhe Pix em português e PayPal em inglês quando configurado', () => {
    expect(donationMethod('pt', 'https://p')).toBe('pix')
    expect(donationMethod('en', 'https://p')).toBe('paypal')
    expect(donationMethod('en', '')).toBe('pix')
  })

  it('mostra na primeira visita e depois do intervalo', () => {
    const now = new Date('2026-01-10T00:00:00Z')
    expect(shouldShowReminder(null, now, 7)).toBe(true)
    expect(shouldShowReminder('lixo', now, 7)).toBe(true)
    expect(shouldShowReminder('2026-01-05T00:00:00Z', now, 7)).toBe(false)
    expect(shouldShowReminder('2026-01-03T00:00:00Z', now, 7)).toBe(true)
  })

  it('intervalo 0 mostra sempre', () => {
    const now = new Date()
    expect(shouldShowReminder(now.toISOString(), now, 0)).toBe(true)
  })

  it('persiste a última exibição', () => {
    localStorage.clear()
    markShown(new Date('2026-01-01T00:00:00Z'))
    expect(readLastShown()).toBe('2026-01-01T00:00:00.000Z')
  })
})
