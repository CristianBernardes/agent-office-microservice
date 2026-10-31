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
  languageWarning: string
  charts: Record<'button' | 'title' | 'flow' | 'lead' | 'aging' | 'empty' | 'close', string>
  restPhrases: string[]
  thinkPhrases: string[]
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
  languageWarning:
    'Atenção: trocar o idioma faz o time escrever os próximos arquivos .md em outro idioma e pode corromper ou misturar os arquivos já escritos. Deseja continuar?',
  charts: {
    button: '📊 Gráficos',
    title: 'Gráficos Kaizen',
    flow: 'Cartões por coluna (fluxo)',
    lead: 'Lead time das tarefas concluídas',
    aging: 'Idade dos cartões em andamento',
    empty: 'Sem dados ainda.',
    close: 'Fechar',
  },
  restPhrases: ['☕ Vou tomar um café…', '😮‍💨 Preciso respirar um pouco', '🚶 Esticando as pernas', '💧 Pausa para beber água'],
  thinkPhrases: ['🤔 Deixa eu pensar nisso…', '💭 Será que há um jeito mais simples?', '📝 Organizando as ideias', '🧠 Revendo o que fizemos'],
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
    'Quero ser transparente: sou um pai que cuida da saúde da filha (que tem várias alergias) e acabei me endividando com esses custos. Preciso de ajuda de verdade, mesmo sendo um projeto open source — mas sem usar minha filha como apelo emocional: o projeto vale por si e a doação é totalmente voluntária. Qualquer valor ajuda. Obrigado!',
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
    testing: 'Em teste',
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
  languageWarning:
    'Warning: changing the language makes the team write the next .md files in another language and may corrupt or mix the files already written. Do you want to continue?',
  charts: {
    button: '📊 Charts',
    title: 'Kaizen charts',
    flow: 'Cards per column (flow)',
    lead: 'Lead time of completed tasks',
    aging: 'Age of in-progress cards',
    empty: 'No data yet.',
    close: 'Close',
  },
  restPhrases: ['☕ Grabbing a coffee…', '😮‍💨 I need a breather', '🚶 Stretching my legs', '💧 Water break'],
  thinkPhrases: ['🤔 Let me think about this…', '💭 Is there a simpler way?', '📝 Sorting out my ideas', '🧠 Reviewing what we did'],
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
    "I want to be upfront: I'm a dad caring for my daughter's health (she has several allergies) and these costs have put me in debt. I genuinely need help, even though this is an open source project — but I don't want to use my daughter as an emotional hook: the project stands on its own and donating is entirely voluntary. Any amount helps. Thank you!",
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
    testing: 'Testing',
    in_review: 'In review',
    done: 'Done',
    blocked: 'Blocked',
  },
  priority: { low: 'Low', medium: 'Medium', high: 'High', urgent: 'Urgent' },
}

export const dictionaries = { pt, en } as const
