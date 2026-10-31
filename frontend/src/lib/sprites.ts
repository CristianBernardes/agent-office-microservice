import type { AgentStatus, Role } from './types'

export const FRAME_WIDTH = 48
export const FRAME_HEIGHT = 96

export interface SpriteSheet {
  file: string
  frames: number
  total?: number
}

// Bloco: cada status do agente escolhe uma folha de sprites; frames = largura da tira / 48 px.
const SHEETS: Record<AgentStatus, SpriteSheet> = {
  idle: { file: 'aguardando_uma_tarefa', frames: 24 },
  thinking: { file: 'analisando_documentacao_e_adrs', frames: 12 },
  working: { file: 'trabalhando_no_computador', frames: 12 },
  talking: { file: 'participando_de_reunioes', frames: 12 },
  offline: { file: 'agente_inativo_por_muito_tempo', frames: 13 },
}

// Bloco: poses alternativas (interagindo_com_objetos: só os 24 primeiros quadros são do personagem; o resto é o carrinho), para o escritório usar todas as folhas de cada personagem.
const ALT_SHEETS: Partial<Record<AgentStatus, SpriteSheet>> = {
  idle: { file: 'interagindo_com_objetos', frames: 24, total: 48 },
  thinking: { file: 'outra_postura_de_trabalho', frames: 12 },
  working: { file: 'outra_postura_de_trabalho', frames: 12 },
}

const WALKING: SpriteSheet = { file: 'deslocamento_entre_salas', frames: 24 }

export function spriteFor(
  role: Role,
  status: AgentStatus,
  walking = false,
  alt = false,
): SpriteSheet & { url: string; total: number } {
  const sheet = walking ? WALKING : ((alt && ALT_SHEETS[status]) || SHEETS[status])
  return { ...sheet, total: sheet.total ?? sheet.frames, url: `/images/sprites/${role}/${sheet.file}.png` }
}
