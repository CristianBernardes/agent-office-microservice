import { describe, expect, it } from 'vitest'
import { loadConfig } from './config'

const base = {
  VITE_API_URL: 'http://api:1/',
  VITE_MQTT_WS_URL: 'ws://mq:2',
  VITE_DEFAULT_LANGUAGE: 'en',
  VITE_PIX_LABEL: 'Pix',
  VITE_DEFAULT_LLM_MODEL: 'qwen3.6:latest',
  VITE_PAYPAL_URL: 'https://paypal.me/x',
  VITE_DONATION_REMINDER_DAYS: '7',
  VITE_REFRESH_INTERVAL_MS: '5000',
}

describe('loadConfig', () => {
  it('lê o ambiente e remove a barra final da URL', () => {
    expect(loadConfig(base)).toEqual({
      apiUrl: 'http://api:1',
      mqttWsUrl: 'ws://mq:2',
      defaultLanguage: 'en',
      pixLabel: 'Pix',
      defaultLlmModel: 'qwen3.6:latest',
      paypalUrl: 'https://paypal.me/x',
      donationReminderDays: 7,
      refreshIntervalMs: 5000,
    })
  })

  it('falha quando falta variável', () => {
    expect(() => loadConfig({ ...base, VITE_API_URL: '' })).toThrow('VITE_API_URL')
  })

  it('PayPal é opcional e o intervalo deve ser inteiro não negativo', () => {
    expect(loadConfig({ ...base, VITE_PAYPAL_URL: undefined }).paypalUrl).toBe('')
    expect(() => loadConfig({ ...base, VITE_DONATION_REMINDER_DAYS: '-1' })).toThrow('non-negative')
  })

  it('rejeita idioma inválido', () => {
    expect(() => loadConfig({ ...base, VITE_DEFAULT_LANGUAGE: 'fr' })).toThrow('pt')
  })
})
