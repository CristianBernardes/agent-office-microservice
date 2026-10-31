import type { Agent, Role } from './types'

export const MAP_WIDTH = 1586
export const MAP_HEIGHT = 992

export interface Seat {
  x: number
  y: number
}

// Bloco: assento de cada papel no mapa escritorio_moderno.png (pixels do centro dos pés).
const SEATS: Record<Role, Seat> = {
  product_owner: { x: 230, y: 215 },
  scrum_master: { x: 790, y: 560 },
  tech_lead: { x: 1395, y: 235 },
  dev_senior: { x: 570, y: 235 },
  dev_junior: { x: 742, y: 235 },
  qa_engineer: { x: 912, y: 235 },
  data_analyst: { x: 247, y: 495 },
  hr_manager: { x: 140, y: 640 },
  product_consultant: { x: 1340, y: 540 },
}

const SPREAD_PX = 56

export interface Placement {
  agent: Agent
  left: number
  top: number
  variant: number
}

// Bloco: giro de matiz do sprite por ordem dentro do papel, para colegas do mesmo cargo serem distintos.
export const HUE_STEP_DEGREES = 75
export const hueFor = (variant: number): number => (variant * HUE_STEP_DEGREES) % 360

// Bloco: agentes do mesmo papel ficam lado a lado; retorna % do mapa para posicionar via CSS.
export function placeAgents(agents: readonly Agent[]): Placement[] {
  const seen = new Map<Role, number>()
  return agents.map((agent) => {
    const index = seen.get(agent.role) ?? 0
    seen.set(agent.role, index + 1)
    const seat = SEATS[agent.role]
    return {
      agent,
      left: ((seat.x + index * SPREAD_PX) / MAP_WIDTH) * 100,
      top: (seat.y / MAP_HEIGHT) * 100,
      variant: index,
    }
  })
}

export interface Meeting {
  walker: string
  target: string
}

// Bloco: escolhe quem anda até quem; só agentes ativos e livres participam.
export function pickMeeting(
  agents: readonly Agent[],
  busy: ReadonlySet<string>,
  random: () => number,
): Meeting | null {
  const free = agents.filter((a) => a.status !== 'offline' && !busy.has(a.agent_id))
  if (free.length < 2) return null
  const walker = free[Math.floor(random() * free.length)]
  const others = free.filter((a) => a !== walker)
  const target = others[Math.floor(random() * others.length)]
  return { walker: walker.agent_id, target: target.agent_id }
}

// Bloco: ponto de encontro ao lado do colega, em % do mapa.
export function meetingPoint(left: number, top: number): { left: number; top: number } {
  return { left: left + (60 / MAP_WIDTH) * 100, top }
}
