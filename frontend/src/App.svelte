<script lang="ts">
  import { onMount } from 'svelte'
  import ChatPanel from './components/ChatPanel.svelte'
  import DismissalModal from './components/DismissalModal.svelte'
  import DonationModal from './components/DonationModal.svelte'
  import HireForm from './components/HireForm.svelte'
  import FireButton from './components/FireButton.svelte'
  import GoalForm from './components/GoalForm.svelte'
  import KanbanBoard from './components/KanbanBoard.svelte'
  import LanguageSwitcher from './components/LanguageSwitcher.svelte'
  import LogPanel from './components/LogPanel.svelte'
  import OfficeMap from './components/OfficeMap.svelte'
  import TaskForm from './components/TaskForm.svelte'
  import TeamBoard from './components/TeamBoard.svelte'
  import { createApiClient } from './lib/api'
  import { loadConfig } from './lib/config'
  import { markShown, readLastShown, shouldShowReminder } from './lib/donation'
  import { i18n } from './lib/i18n.svelte'
  import { mergeLogs } from './lib/logs'
  import { OfficeStore } from './lib/office.svelte'
  import { connectRealtime } from './lib/realtime'
  import type { Agent, DismissalProposal, HireAgentInput, Priority, Task, TaskStatus } from './lib/types'

  const config = loadConfig(import.meta.env)
  i18n.init(config.defaultLanguage, localStorage)
  const api = createApiClient(config.apiUrl, () => i18n.language)
  const store = new OfficeStore()
  let models = $state<string[]>([])

  let showDonation = $state(shouldShowReminder(readLastShown(), new Date(), config.donationReminderDays))
  const lines = $derived(mergeLogs(store.logs, store.activity))
  // Bloco: quem foi demitido (offline) sai do escritório, do mapa e da lista do time.
  const team = $derived(store.agents.filter((a) => a.status !== 'offline'))
  const selected = $derived(team.find((a) => a.agent_id === store.selectedAgentId))
  // Bloco: o usuário é o dono do produto; as ações dele são registradas em nome do PO.
  const ownerActor = () => team.find((x) => x.role === 'product_owner') ?? team[0]

  // Bloco: o ciclo de trabalho do backend segue o idioma escolhido na tela (ADR-051).
  const syncLanguage = () => void api.setOfficeLanguage(i18n.language).catch(() => undefined)
  onMount(syncLanguage)

  function closeDonation() {
    markShown(new Date())
    showDonation = false
  }

  async function hireAgent(input: HireAgentInput) {
    await api.hireAgent(input)
    await store.load(api)
  }

  async function createGoal(text: string) {
    await api.createGoal(text)
    await store.load(api)
  }

  // Bloco: a tarefa é criada em nome do Product Owner (ou do primeiro agente) e o texto vira objetivo do time.
  async function createTask(title: string, description: string, priority: Priority) {
    const actor = ownerActor()
    if (!actor) throw new Error('no agent')
    await api.createTask({ title, description, priority, actor_id: actor.agent_id, actor_role: actor.role })
    await api.createGoal(description ? `${title}\n\n${description}` : title)
    await store.load(api)
  }

  async function moveTask(task: Task, to: TaskStatus, actor: Agent) {
    const updated = await api.moveTask(task.task_id, {
      to_status: to,
      actor_id: actor.agent_id,
      actor_role: actor.role,
      owner_override: true,
    })
    store.replaceTask(updated)
  }

  async function updateTask(task: Task, changes: { owner?: string; priority?: Priority }) {
    const actor = ownerActor()
    if (!actor) throw new Error('no agent')
    const who = { actor_id: actor.agent_id, actor_role: actor.role }
    if (changes.owner) store.replaceTask(await api.setTaskOwner(task.task_id, changes.owner, who))
    if (changes.priority) store.replaceTask(await api.setTaskPriority(task.task_id, changes.priority, who))
  }

  async function deleteTask(task: Task) {
    const actor = ownerActor()
    if (!actor) throw new Error('no agent')
    await api.deleteTask(task.task_id, { actor_id: actor.agent_id, actor_role: actor.role })
    store.removeTask(task.task_id)
  }

  async function fireAgent(agent: Agent) {
    await api.fireAgent(agent.agent_id)
    if (store.selectedAgentId === agent.agent_id) store.select(null)
    await store.load(api)
  }

  // Bloco: o RH propõe, o dono do produto decide; aparece uma proposta por vez, a mais antiga.
  const pendingDismissal = $derived(store.dismissals[0])

  async function decideDismissal(proposal: DismissalProposal, approved: boolean) {
    await api.decideDismissal(proposal.proposal_id, approved)
    await store.load(api)
  }

  async function sendMessage(content: string) {
    if (!store.sessionId) throw new Error('no session')
    await api.sendMessage(store.sessionId, content)
    await store.load(api)
  }

  onMount(() => {
    store.load(api).catch(() => {})
    api
      .listModels()
      .then((list) => (models = list))
      .catch(() => {})
    const stop = connectRealtime(config.mqttWsUrl, {
      onEvent: (event) => store.apply(event),
      onConnection: (connected) => (store.connected = connected),
    })
    const timer = setInterval(() => store.load(api).catch(() => {}), config.refreshIntervalMs)
    return () => {
      stop()
      clearInterval(timer)
    }
  })
</script>

<header>
  <h1>{i18n.t.appTitle}</h1>
  <span class="conn" class:on={store.connected}>
    {store.connected ? i18n.t.connected : i18n.t.disconnected}
  </span>
  <LanguageSwitcher onchange={syncLanguage} />
  <button type="button" class="support" onclick={() => (showDonation = true)}>{i18n.t.support}</button>
</header>

<main>
  <OfficeMap
    agents={team}
    thoughts={store.thoughts}
    selectedId={store.selectedAgentId}
    wanderIntervalMs={config.wanderIntervalMs}
    onselect={(id) => store.select(id)}
  />
  {#if selected}
    <div class="panel selected" data-testid="selected-agent">
      <strong>{selected.name}</strong>
      <span>{i18n.t.roles[selected.role]}</span>
      <span class="state">{i18n.t.agentStatus[selected.status]}</span>
      <FireButton agent={selected} onfire={fireAgent} />
    </div>
  {/if}
  <HireForm defaultModel={config.defaultLlmModel} {models} onsubmit={hireAgent} />
  <div class="grid">
    <GoalForm onsubmit={createGoal} />
    <TaskForm hasAgents={team.length > 0} onsubmit={createTask} />
  </div>
  <div class="grid">
    <TeamBoard
      agents={team}
      tasks={store.tasks}
      selectedId={store.selectedAgentId}
      onselect={(id) => store.select(id)}
      onfire={fireAgent}
    />
    <ChatPanel
      messages={store.messages}
      agents={store.agents}
      canSend={store.sessionId !== null}
      onsend={sendMessage}
    />
    <LogPanel {lines} agents={store.agents} />
  </div>
  <KanbanBoard
    tasks={store.tasks}
    agents={store.agents}
    onmove={moveTask}
    onupdate={updateTask}
    ondelete={deleteTask}
    wipLimits={config.wipLimits}
  />
  {#if store.error}<p role="alert">{i18n.t.loadError}</p>{/if}
</main>

{#if pendingDismissal}
  <DismissalModal
    proposal={pendingDismissal}
    target={store.agents.find((a) => a.agent_id === pendingDismissal.agent_id)}
    proposer={store.agents.find((a) => a.agent_id === pendingDismissal.proposed_by)}
    ondecide={decideDismissal}
  />
{/if}

{#if showDonation}
  <DonationModal paypalUrl={config.paypalUrl} pixLabel={config.pixLabel} onclose={closeDonation} />
{/if}

<style>
  header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
  }
  h1 {
    font-size: 18px;
    margin: 0;
    margin-right: auto;
  }
  .conn {
    font-size: 12px;
    color: #ef5350;
  }
  .conn.on {
    color: #66bb6a;
  }
  .support {
    background: transparent;
    color: inherit;
    border: 1px solid var(--accent);
    border-radius: 6px;
    padding: 4px 10px;
    cursor: pointer;
  }
  main {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 16px;
    max-width: 1600px;
    margin: 0 auto;
  }
  .selected {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .selected .state {
    opacity: 0.7;
    font-size: 12px;
    margin-right: auto;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
  }
</style>
