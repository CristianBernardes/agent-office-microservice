import type { AgentStatus, Role } from './types'

export const FRAME_WIDTH = 48
export const FRAME_HEIGHT = 96

export interface SpriteSheet {
  file: string
  frames: number
}

// Bloco: cada status do agente escolhe uma folha de sprites; frames = largura da tira / 48 px.
const SHEETS: Record<AgentStatus, SpriteSheet> = {
  idle: { file: 'aguardando_uma_tarefa', frames: 24 },
  thinking: { file: 'analisando_documentacao_e_adrs', frames: 12 },
  working: { file: 'trabalhando_no_computador', frames: 12 },
  talking: { file: 'participando_de_reunioes', frames: 12 },
  offline: { file: 'agente_inativo_por_muito_tempo', frames: 13 },
}

const WALKING: SpriteSheet = { file: 'deslocamento_entre_salas', frames: 24 }

export function spriteFor(
  role: Role,
  status: AgentStatus,
  walking = false,
): SpriteSheet & { url: string } {
  const sheet = walking ? WALKING : SHEETS[status]
  return { ...sheet, url: `/images/sprites/${role}/${sheet.file}.png` }
}
