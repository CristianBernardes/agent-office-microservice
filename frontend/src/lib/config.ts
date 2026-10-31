import type { Language } from './types'

export interface AppConfig {
  apiUrl: string
  mqttWsUrl: string
  defaultLanguage: Language
  pixLabel: string
  paypalUrl: string
  donationReminderDays: number
  refreshIntervalMs: number
}

type Env = Record<string, string | undefined>

// Bloco: toda configuração vem do ambiente (VITE_*); ausência é erro, nunca um default embutido.
function required(env: Env, key: string): string {
  const value = env[key]
  if (!value) throw new Error(`Missing required env var ${key}`)
  return value
}

function nonNegativeInt(env: Env, key: string): number {
  const value = Number(required(env, key))
  if (!Number.isInteger(value) || value < 0) throw new Error(`${key} must be a non-negative integer`)
  return value
}

export function loadConfig(env: Env): AppConfig {
  const language = required(env, 'VITE_DEFAULT_LANGUAGE')
  if (language !== 'pt' && language !== 'en') {
    throw new Error(`VITE_DEFAULT_LANGUAGE must be "pt" or "en", got "${language}"`)
  }
  return {
    apiUrl: required(env, 'VITE_API_URL').replace(/\/+$/, ''),
    mqttWsUrl: required(env, 'VITE_MQTT_WS_URL'),
    defaultLanguage: language,
    pixLabel: required(env, 'VITE_PIX_LABEL'),
    paypalUrl: env.VITE_PAYPAL_URL ?? '',
    donationReminderDays: nonNegativeInt(env, 'VITE_DONATION_REMINDER_DAYS'),
    refreshIntervalMs: nonNegativeInt(env, 'VITE_REFRESH_INTERVAL_MS'),
  }
}
