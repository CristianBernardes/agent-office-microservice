import type { AgentStatus, MessageKind, Priority, Role, TaskStatus } from './types'

export interface Messages {
  appTitle: string
  office: string
  board: string
  activity: string
  language: string
  connected: string
  disconnected: string
  noAgents: string
  noActivity: string
  loadError: string
  metrics: Record<'wip' | 'throughput' | 'leadTime' | 'leadP85' | 'cycleTime' | 'aging' | 'wipLimit' | 'wipExceeded', string>
  hireTitle: string
  hireName: string
  hireRole: string
  hireModel: string
  hireSubmit: string
  hireDone: string
  hireTeam: string
  goalTitle: string
  goalPlaceholder: string
  goalSubmit: string
  goalSent: string
  support: string
  donationTitle: string
  donationPix: string
  donationPaypal: string
  donationPaypalButton: string
  donationThanks: string
  donationLater: string
  close: string
  thoughtLabel: string
  chat: string
  taskFormTitle: string
  taskName: string
  taskDescription: string
  taskCreate: string
  taskNeedsAgent: string
  taskCreated: string
  noMessages: string
  logs: string
  noLogs: string
  team: string
  noTasks: string
  unassigned: string
  progress: string
  system: string
  messageKind: Record<MessageKind, string>
  roles: Record<Role, string>
  agentStatus: Record<AgentStatus, string>
  taskStatus: Record<TaskStatus, string>
  priority: Record<Priority, string>
}

export const pt: Messages = {
  appTitle: 'Escritório de Agentes',
  office: 'Escritório',
  board: 'Quadro Kanban',
  activity: 'Atividade',
  language: 'Idioma',
  connected: 'Tempo real conectado',
  disconnected: 'Tempo real desconectado',
  noAgents: 'Nenhum agente contratado.',
  noActivity: 'Nenhuma atividade ainda.',
  loadError: 'Não foi possível carregar os dados.',
  metrics: {
    wip: 'WIP (em andamento + revisão)',
    throughput: 'Vazão (concluídas)',
    leadTime: 'Lead time médio',
    leadP85: 'Lead time P85',
    cycleTime: 'Cycle time médio',
    aging: 'Cartão mais antigo em andamento',
    wipLimit: 'Limite de WIP',
    wipExceeded: 'Limite de WIP excedido',
  },
  hireTitle: 'Contratar agente',
  hireName: 'Nome',
  hireRole: 'Cargo',
  hireModel: 'Modelo (Ollama)',
  hireSubmit: 'Contratar',
  hireDone: 'Agente contratado!',
  hireTeam: 'Contratar time padrão',
  goalTitle: 'Novo objetivo',
  goalPlaceholder: 'Descreva o que o time deve entregar…',
  goalSubmit: 'Enviar ao time',
  goalSent: 'Objetivo enviado!',
  support: 'Apoiar o projeto',
  donationTitle: 'Apoie o Agent Office',
  donationPix: 'Escaneie o QR code com o app do seu banco para doar via Pix.',
  donationPaypal: 'Doe pelo PayPal.',
  donationPaypalButton: 'Doar com PayPal',
  donationThanks:
    'Projeto open source criado por um pai para ajudar a custear a saúde da filha, que tem várias alergias. Qualquer ajuda é muito bem-vinda. Obrigado!',
  donationLater: 'Agora não',
  close: 'Fechar',
  thoughtLabel: 'Pensando',
  chat: 'Conversas do time',
  taskFormTitle: 'Nova tarefa para o time',
  taskName: 'Título',
  taskDescription: 'O que deve ser entregue? O time estuda, decide, quebra em subtarefas e escreve os .md.',
  taskCreate: 'Criar e enviar ao time',
  taskNeedsAgent: 'Contrate um agente antes de criar tarefas.',
  taskCreated: 'Tarefa criada e enviada ao time!',
  noMessages: 'Nenhuma conversa ainda.',
  logs: 'Logs em tempo real',
  noLogs: 'Aguardando eventos…',
  team: 'Time e tarefas',
  noTasks: 'Sem tarefas atribuídas',
  unassigned: 'Sem responsável',
  progress: 'Andamento',
  system: 'Sistema',
  messageKind: { chat: 'Conversa', thought: 'Pensamento', system: 'Sistema', question: 'Pergunta', decision: 'Decisão' },
  roles: {
    product_owner: 'Product Owner',
    scrum_master: 'Scrum Master',
    tech_lead: 'Tech Lead',
    dev_senior: 'Dev Sênior',
    dev_junior: 'Dev Júnior',
    qa_engineer: 'QA',
    data_analyst: 'Analista de Dados',
    hr_manager: 'RH',
    product_consultant: 'Consultor de Produto',
  },
  agentStatus: {
    idle: 'Ocioso',
    thinking: 'Pensando',
    working: 'Trabalhando',
    talking: 'Conversando',
    offline: 'Offline',
  },
  taskStatus: {
    backlog: 'Backlog',
    todo: 'A fazer',
    in_progress: 'Em andamento',
    in_review: 'Em revisão',
    done: 'Concluído',
    blocked: 'Bloqueado',
  },
  priority: { low: 'Baixa', medium: 'Média', high: 'Alta', urgent: 'Urgente' },
}

export const en: Messages = {
  appTitle: 'Agent Office',
  office: 'Office',
  board: 'Kanban board',
  activity: 'Activity',
  language: 'Language',
  connected: 'Realtime connected',
  disconnected: 'Realtime disconnected',
  noAgents: 'No agents hired.',
  noActivity: 'No activity yet.',
  loadError: 'Could not load data.',
  metrics: {
    wip: 'WIP (in progress + review)',
    throughput: 'Throughput (done)',
    leadTime: 'Average lead time',
    leadP85: 'Lead time P85',
    cycleTime: 'Average cycle time',
    aging: 'Oldest card in progress',
    wipLimit: 'WIP limit',
    wipExceeded: 'WIP limit exceeded',
  },
  hireTitle: 'Hire an agent',
  hireName: 'Name',
  hireRole: 'Role',
  hireModel: 'Model (Ollama)',
  hireSubmit: 'Hire',
  hireDone: 'Agent hired!',
  hireTeam: 'Hire default team',
  goalTitle: 'New goal',
  goalPlaceholder: 'Describe what the team should deliver…',
  goalSubmit: 'Send to the team',
  goalSent: 'Goal sent!',
  support: 'Support the project',
  donationTitle: 'Support Agent Office',
  donationPix: 'Scan the QR code with your bank app to donate via Pix.',
  donationPaypal: 'Donate through PayPal.',
  donationPaypalButton: 'Donate with PayPal',
  donationThanks:
    "Open source project built by a dad to help cover his daughter's healthcare; she has several allergies. Any help is very welcome. Thank you!",
  donationLater: 'Not now',
  close: 'Close',
  thoughtLabel: 'Thinking',
  chat: 'Team conversations',
  taskFormTitle: 'New task for the team',
  taskName: 'Title',
  taskDescription: 'What should be delivered? The team studies, decides, splits into subtasks and writes the .md files.',
  taskCreate: 'Create and send to the team',
  taskNeedsAgent: 'Hire an agent before creating tasks.',
  taskCreated: 'Task created and sent to the team!',
  noMessages: 'No conversations yet.',
  logs: 'Live logs',
  noLogs: 'Waiting for events…',
  team: 'Team and tasks',
  noTasks: 'No assigned tasks',
  unassigned: 'Unassigned',
  progress: 'Progress',
  system: 'System',
  messageKind: { chat: 'Chat', thought: 'Thought', system: 'System', question: 'Question', decision: 'Decision' },
  roles: {
    product_owner: 'Product Owner',
    scrum_master: 'Scrum Master',
    tech_lead: 'Tech Lead',
    dev_senior: 'Senior Dev',
    dev_junior: 'Junior Dev',
    qa_engineer: 'QA',
    data_analyst: 'Data Analyst',
    hr_manager: 'HR',
    product_consultant: 'Product Consultant',
  },
  agentStatus: {
    idle: 'Idle',
    thinking: 'Thinking',
    working: 'Working',
    talking: 'Talking',
    offline: 'Offline',
  },
  taskStatus: {
    backlog: 'Backlog',
    todo: 'To do',
    in_progress: 'In progress',
    in_review: 'In review',
    done: 'Done',
    blocked: 'Blocked',
  },
  priority: { low: 'Low', medium: 'Medium', high: 'High', urgent: 'Urgent' },
}

export const dictionaries = { pt, en } as const
