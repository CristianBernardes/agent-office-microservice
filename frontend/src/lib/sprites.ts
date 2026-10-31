import type { AgentStatus, Role } from "./types";

export const FRAME_WIDTH = 48;
export const FRAME_HEIGHT = 96;

export type Direction = "right" | "up" | "left" | "down";

// Bloco: cada folha concatena as direções (4: direita, costas, esquerda, frente; 2: direita, esquerda); animar a tira inteira faz o personagem girar.
const DIRECTION_ORDER: Record<number, Direction[]> = {
  4: ["right", "up", "left", "down"],
  2: ["right", "left"],
};

export interface SpriteSheet {
  file: string;
  frames: number;
  total?: number;
  dirs?: number;
}

// Bloco: cada status do agente escolhe uma folha de sprites; frames = largura da tira / 48 px.
const SHEETS: Record<AgentStatus, SpriteSheet> = {
  idle: { file: "aguardando_uma_tarefa", frames: 24, dirs: 4 },
  thinking: { file: "analisando_documentacao_e_adrs", frames: 12, dirs: 2 },
  working: { file: "trabalhando_no_computador", frames: 12, dirs: 2 },
  talking: { file: "participando_de_reunioes", frames: 12, dirs: 2 },
  offline: { file: "agente_inativo_por_muito_tempo", frames: 13 },
};

// Bloco: poses alternativas, para o escritório usar todas as folhas de cada personagem.
const ALT_SHEETS: Partial<Record<AgentStatus, SpriteSheet>> = {
  idle: { file: "interagindo_com_objetos", frames: 24, total: 48, dirs: 4 },
  thinking: { file: "outra_postura_de_trabalho", frames: 12, dirs: 2 },
  working: { file: "outra_postura_de_trabalho", frames: 12, dirs: 2 },
};

const WALKING: SpriteSheet = {
  file: "deslocamento_entre_salas",
  frames: 24,
  dirs: 4,
};

export function spriteFor(
  role: Role,
  status: AgentStatus,
  walking = false,
  alt = false,
  direction: Direction = "down",
): SpriteSheet & { url: string; total: number; start: number; count: number } {
  const sheet = walking
    ? WALKING
    : (alt && ALT_SHEETS[status]) || SHEETS[status];
  const dirs = sheet.dirs ?? 1;
  const count = sheet.frames / dirs;
  const order = DIRECTION_ORDER[dirs] ?? [];
  const index = Math.max(0, order.indexOf(direction));
  return {
    ...sheet,
    total: sheet.total ?? sheet.frames,
    start: index * count,
    count,
    url: `/images/sprites/${role}/${sheet.file}.png`,
  };
}
