<script lang="ts">
  import { onMount } from 'svelte'
  import ChatPanel from './components/ChatPanel.svelte'
  import DonationModal from './components/DonationModal.svelte'
  import HireForm from './components/HireForm.svelte'
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
  import type { Agent, HireAgentInput, Priority, Task, TaskStatus } from './lib/types'

  const config = loadConfig(import.meta.env)
  i18n.init(config.defaultLanguage, localStorage)
  const api = createApiClient(config.apiUrl, () => i18n.language)
  const store = new OfficeStore()
  let models = $state<string[]>([])

  let showDonation = $state(shouldShowReminder(readLastShown(), new Date(), config.donationReminderDays))
  const lines = $derived(mergeLogs(store.logs, store.activity))

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
    const actor = store.agents.find((x) => x.role === 'product_owner') ?? store.agents[0]
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
    })
    store.replaceTask(updated)
  }

  onMount(() => {
    store.load(api).catch(() => {})
    api.listModels().then((list) => (models = list)).catch(() => {})
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
  <LanguageSwitcher />
  <button type="button" class="support" onclick={() => (showDonation = true)}>{i18n.t.support}</button>
</header>

<main>
  <OfficeMap
    agents={store.agents}
    thoughts={store.thoughts}
    selectedId={store.selectedAgentId}
    wanderIntervalMs={config.wanderIntervalMs}
    onselect={(id) => store.select(id)}
  />
  <HireForm defaultModel={config.defaultLlmModel} {models} onsubmit={hireAgent} />
  <div class="grid">
    <GoalForm onsubmit={createGoal} />
    <TaskForm hasAgents={store.agents.length > 0} onsubmit={createTask} />
  </div>
  <div class="grid">
    <TeamBoard agents={store.agents} tasks={store.tasks} selectedId={store.selectedAgentId} onselect={(id) => store.select(id)} />
    wanderIntervalMs={config.wanderIntervalMs}
    <ChatPanel messages={store.messages} agents={store.agents} />
    <LogPanel {lines} agents={store.agents} />
  </div>
  <KanbanBoard tasks={store.tasks} agents={store.agents} onmove={moveTask} wipLimits={config.wipLimits} />
  {#if store.error}<p role="alert">{i18n.t.loadError}</p>{/if}
</main>

{#if showDonation}
  <DonationModal paypalUrl={config.paypalUrl} pixLabel={config.pixLabel} onclose={closeDonation} />
{/if}

<style>
  header { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-bottom: 1px solid var(--border); }
  h1 { font-size: 18px; margin: 0; margin-right: auto; }
  .conn { font-size: 12px; color: #ef5350; }
  .conn.on { color: #66bb6a; }
  .support { background: transparent; color: inherit; border: 1px solid var(--accent); border-radius: 6px; padding: 4px 10px; cursor: pointer; }
  main { display: flex; flex-direction: column; gap: 16px; padding: 16px; max-width: 1600px; margin: 0 auto; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
</style>
