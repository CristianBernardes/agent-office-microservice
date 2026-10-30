# SCRATCHPAD — Flow Saboteurs

> Estado vivo entre sessões. Comece cada sessão com: *"Leia o SCRATCHPAD e me diga o que está pendente."* Termine com: *"Atualize o SCRATCHPAD com o que foi feito."*
> Regras de conversa: [boas_praticas_de_conversa_com_o_copilot.md](./boas_praticas_de_conversa_com_o_copilot.md)

## Objetivo atual

Bug corrigido: profissional treinado em área não pegava card da área no dia de conclusão do treinamento. Próxima feature a definir.

## Próxima sessão

Feature PAUSAS_ESPONTANEAS_E_VIDA_PROPRIA concluída. Bug de treinamento corrigido. Próxima feature a definir.

### Decisões de design (seção 15 do plano — respondidas em 2026-10-25)

1. **Expediente**: 480 min por dia de jogo.
2. **Pausas durante reunião**: permitidas (reunião não congela tudo).
3. **Barra do dia**: visível para todos ao mesmo tempo (painel geral).
4. **Truco**: "Jogo de Cartas" (neutro, funciona em PT/EN/ES).

### Etapa 1 — Tempo em minutos ✅

- [x] `GameConfig.workdayMinutes = 480` + constantes de pausa
- [x] `LedgerKind.idleTime`; `DayTimeLedger` + `TimeBlock` + `TimeCategory`
- [x] `GameState.dayTimeLedger`; `DailyWorkPlanner` escala capacidade pelo `productivityFactor`
- [x] 21 testes novos; 1511 testes passando — commit `1ebb40e`

### Etapa 2 — Necessidades e perfis ✅

- [x] `PauseKind` (10 pausas) + `PauseKindMeta` (duração, participantes)
- [x] `ProfessionalNeeds` (imutável, 6 necessidades, `applyRelief`, `dominant`)
- [x] `NeedsProfile` + `NeedsRates`: taxas e pausas favoritas dos 11 cavalos
- [x] `NeedsCalculator`: `advance` (modificadores situacionais), `pauseChance`, `pauseWeights`, `applyPauseRelief`
- [x] 32 testes novos; 1543 testes passando — commit `09a6c71`

### Etapas seguintes (plano seção 13)

### Etapa 3 — Pausas simples ✅

- [x] `PauseRecord` (imutável: profissional, tipo, dia, duração, custo)
- [x] `PauseStrategy` interface + `PauseAttempt` sealed (`PauseGranted` / `PauseDeclined`)
- [x] `CoffeePause` e `RestroomPause` (estratégias concretas)
- [x] `PauseRegistry` (catálogo de estratégias por `PauseKind`)
- [x] `PauseService.run(state, day)` — processa todos os contratados; usa `RandomSource` separado do motor
- [x] `GameState` +`professionalNeeds` +`pauseLog`
- [x] `DailySimulator._advanceNeeds` + integração do `PauseService` (campo opcional)
- [x] `EnginePartsConfig.pauseRandom`; `GameEngine` cria `pauseRng` determinístico (`rng.hashCode ^ 0xDEADBEEF`)
- [x] 9 testes novos; 1552 testes passando — commit `5133ef7`
### Etapa 4 — Economia e métricas ✅

- [x] `FlowMetrics` +`idleMinutesTotal`, +`idleMinutesByPro`, +`occupancyRate`, +`topIdler` (opcionais)
- [x] `FlowMetricsCalculator.compute` aceita `DayTimeLedger?` e `hiredCount` e calcula métricas de ociosidade
- [x] `BoardSynchronizer.flowMetrics/liveMetrics/synced/refresh/appendEvent` propagam ledger e hiredCount
- [x] Teste de economia atualizado: verifica ledger de salário + caixa ≤ esperado (pausas podem cobrar extra)
- [x] 7 testes novos; 1559 testes passando — commit `f4b8d0b`

### Etapa 5 — Pausas coletivas ✅

- [x] `CardGamePause` — quórum 4; recruta `alwaysAcceptsInvite` primeiro, depois aleatório
- [x] `CakePause` — todos os disponíveis participam
- [x] `GossipPause` — 2–3 participantes aleatórios
- [x] `MeditationPause` — só o Coach Trovão convoca; todos os disponíveis participam
- [x] `PauseRegistry` registra as 4 novas estratégias
- [x] `PauseService._apply` registra ledger/needs/custo para todos os participantes
- [x] 16 testes novos; 1575 testes passando — commit `f8599d6`
### Etapa 6 — Humor e relações ✅

- [x] `PauseMoodService.apply` — participantes ficam `loyal`; excluídos de bolo/cardGame ficam `frustrated`
- [x] `PauseMoodService.clearEffects` — limpa efeitos no início de cada dia
- [x] `GameState.pauseMoodEffects` — mapa de efeitos temporários de humor
- [x] `BotMoodCalculator.moodOf` — consulta `pauseMoodEffects` com prioridade máxima
- [x] `DailySimulator._simulateDay` — chama `clearEffects` no início do dia
- [x] `PauseService._apply` — chama `moodService.apply` após cada pausa
- [x] 6 testes novos; 1581 testes passando — commit `3a05ef4`
### Etapa 7 — UI ✅

- [x] Strings i18n PT/EN/ES: 10 tipos de pausa, `pauseStatusMinutes`, `dayBar*`, `idleSummary*`
- [x] `AppColors` +`dayBarProductive/Pause/Meeting/Idle` +`pauseBadge/pauseBadgeText`
- [x] `pause_kind_labels.dart` — helper `pauseKindLabelFor(l10n, kind)`
- [x] `PauseStatusBadge` — badge âmbar no avatar com emoji da pausa e tooltip
- [x] `DayBarWidget` — barra de 480 min com segmentos coloridos por categoria
- [x] `TeamSheetData` +`pauseLog` +`dayTimeLedger`
- [x] `TeamSheet` integra badge no avatar e barra do dia abaixo de cada contratado
- [x] `BoardScreen._readTeamSheet` passa `pauseLog` e `dayTimeLedger` do `GameState`
- [x] ARB whitelist atualizada (`pauseStatusMinutes`, `pauseKindBreathBreak`)
- [x] 1581 testes passando — commit `2655378`
### Etapa 8 — IA e fala ✅

- [x] `PauseSpeechBank` — banco local de falas por `PauseKind` e idioma (PT/EN/ES), mínimo 3 frases por entrada
- [x] `PauseReactor` — gera fala do iniciador (ou participante aleatório em coletivas, 30%); respeita `BotMemory`
- [x] `SessionStreams` +`pause` stream (`PauseReaction`)
- [x] `SessionTickHandler._announcePauses` — detecta novas pausas no log e emite reações
- [x] `GameSession/LocalGameSession` expõe `pauseReactions` stream
- [x] `BoardController` subscreve `pauseReactions` e exibe `showPauseSnackBar`
- [x] `pause_snackbar.dart` — SnackBar âmbar com emoji e fala do profissional
- [x] 10 testes novos; 1591 testes passando — commit `304c189`
### Etapa 9 — Gestor reage ✅

- [x] `PolicyKind.pauseSchedule` — nova política que reduz chance de pausa em 50%
- [x] `PauseService._policyFactor` — implementado (antes retornava 1.0 fixo)
- [x] `EndPauseService` — encerra pausas ativas do dia, aplica penalidade de moral/confiança
- [x] `CallBackToWorkAbility` (Dean) — habilidade que chama todos de volta; recusa se não há pausas ativas
- [x] `AngelParams` +`callBackCooldownDays=1`, +`callBackChargesPerRound=5`, +`gems=19`
- [x] Dean agora tem 8 habilidades (era 7)
- [x] i18n: `policyPauseSchedule` em PT/EN/ES
- [x] Golden test: hashes e digests atualizados (pausas afetam o jogo)
- [x] 6 testes novos; 1597 testes passando — commit `07cc1c0`
### Etapa 10 — Calibração ✅

- [x] `pause_calibration_test.dart` — 7 testes: ociosidade ≤ 50%, ao menos 1 pausa coletiva, parâmetros dentro dos limites
- [x] Parâmetros validados: `pauseBaseChancePerDay=0.35`, `pauseMaxPerDayPerPro=3`, `pauseMinGapMinutes=60`
- [x] 1604 testes passando — commit `b2a3854`
- [x] Etapa 8 — IA e fala ✅
- [x] Etapa 9 — Gestor reage ✅
- [x] Etapa 10 — Calibração ✅

### Bug fix — Treinamento: profissional não pegava card da área treinada no dia de conclusão ✅

- **Causa raiz**: `completePendingTrainings` era chamado pelo `SessionTickHandler` **após** `advance()`, então no dia exato de conclusão o planner rodava com `trainedDomains` ainda vazio.
- **Correção**: `DailySimulator._simulateDay` agora chama `training.completePendingTrainings(state, day)` **antes** de `releaseIneligibleReservations` e do planner. `TrainingService` adicionado como campo do `DailySimulator` (default `const TrainingService()`).
- **Testes**: `trained_domain_card_pickup_test.dart` (3 testes) + `assign_card_dialog_test.dart` (1 teste) — 1608 testes passando — commit `3d85dd7`

### VIDA_PROPRIA_FASE2 — Feature A: Ausências em Reunião ✅

- `MeetingAbsenceService.sortAbsences` — sorteia ausentes com chance base + bônus frustrated
- `AbsenceReasonBank` — banco PT/EN/ES de desculpas por personagem
- `MeetingState` +`absentProfessionalIds` +`absenceReasons`
- `MeetingService.trigger()` chama o serviço e adiciona ChatLine por ausente
- `AccordApplier` ignora votos de ausentes
- `GameConfig`: `meetingAbsentChance=0.15`, `meetingAbsentFrustratedBonus=0.15`, `meetingAbsentMaxPerMeeting=2`
- i18n PT/EN/ES: strings de ausência por personagem
- 4 testes novos; golden hashes atualizados — commit `61750d0`

### VIDA_PROPRIA_FASE2 — Features B+C+D+E: Folgas, Distrações, Conflitos, Problemas Técnicos ✅

- **Feature B — Folgas Surpresa**: `DayOffService.sortDayOffs` no 1º dia de cada rodada; `Professional.unavailableUntilDay/unavailableReason`; `StaffService` preserva reserva de folga; `DailySimulator` filtra folga do pool do planner
- **Feature C — Distrações Digitais**: `PhoneVideoPause` + `UrgentCallPause` registradas no `PauseRegistry`; `phoneVideo` e `urgentCall` agora têm estratégias concretas
- **Feature D — Conflitos Interpessoais**: `ProfessionalConflict` (par canônico); `ConflictService.sortConflicts` no 1º dia de cada rodada; `applyConflictPenalties` aplica penalidade de moral por par em conflito trabalhando junto; `GameState.conflictingPairs`
- **Feature E — Problemas Técnicos**: `TechProblemService.run` sorteia pausa `urgentCall` diária para profissionais com estresse alto
- **Infra**: `SeededRandomSource.seed` exposto; `humanizationRng` derivado deterministicamente (`rngSeed ^ 0xCAFE_BABE`); `DailySimulator.humanizationRandom` separado do motor principal
- **Config**: `conflictChancePerRound=0.08`, `conflictMaxPerRound=2`, `conflictMoralePenaltyPerPair=2`, `techProblemBaseChance=0.05`, `techProblemStressMultiplier=0.15`, `techProblemMinMinutes=15`, `techProblemMaxMinutes=45`
- i18n PT/EN/ES: strings de conflito (`conflictColdShoulder`, `conflictMeetingTension`, `conflictEmailWar`, `conflictCreditDispute`)
- 20 testes novos; golden hashes e digests atualizados; 1628 testes passando

## Andamento das sessões

Marque ao concluir (`[x]`) e anote o commit. Detalhes de cada tarefa e arquivos: seção 6 do plano.

### Etapa 1 — Gorse Bele (seção 4)
- [x] 1.1 `GorseBeleParams` com valores atuais — commit `0fd3c4d`
- [x] 1.2 Avaliação por dia + valores novos + `omenDay`/`lastEvaluatedDay`/`clearOmen` — commit `65009ed`
- [x] 1.3a Domínio do aviso prévio (bloqueios em D+1, cancelamento/adiamento) + árbitro de IA consultado em D e consumido em D+1 — commit `c24405a`
- [x] 1.3b UI: banner "rondando…" e overlay mais curto — commit `3e04c80`
- [x] 1.4 Simulação de 10 rodadas e calibração — commit `4dc9789` (vencedor: 25–50%, limiar 50%, intervalo 5d → 1.0 aparição/rodada)
- [x] 1.5a Configurações: persistir/escolher Calma/Normal/Caos — commit `f753dc1`
- [x] 1.5b Aplicar o modo nos parâmetros e na sabotagem — commit `51e214a`

### Etapa 2 — Adiantar dias (seção 5)
- [x] 2.1 `skipDays` no relógio + teste de fração de dia — commit `bbd01a6`
- [x] 2.2 `session_fast_forward_handler` + teste de equivalência — commit `3d4512a`
- [x] 2.3 `FastForwardButton` — commit `d6e48a1`

### Etapa 3 — Loja (seção 2)
- [x] 3.1 `ShopScreen` + `exchange_tab` + botão "Quiz" na home — commit `cb1242a`
- [x] 3.2 `angels_tab` + religar `shop_button`, `gems_entry_button` e `CarriedCashBadge` — commit `2883b8c`
- [x] 3.3 Remover `GemsScreen` e atualizar testes — commit `c688345`

### Etapa 4 — Treinamento (seção 3)
- [x] 4.1 Simulação de equilíbrio (coringa × especialista) + parâmetros em `EconomyParams` — commit `a504a7a`
- [x] 4.2 `training_catalog` — commit `0f4c8a4`
- [x] 4.3a Modelo e regra (`trainedDomains`, elegibilidade, demissão, possessão) — commit `f6a3c55`
- [x] 4.3b `TrainingService`, salário, `GameEngine.trainProfessional` — commit `1950ec3`
- [x] 4.4 Sessão e eventos — commit `d43cbb2`
- [x] 4.5 UI no `TeamSheet` — commit `ac3f6cc`

### Etapa 5 — Parte A (Kaizen Game)
- [x] A.3 WIP dinâmico — commit `aa20e33`
  - `WipAdjustmentRecord` + `GameState.wipAdjustmentLog`
  - `AccordApplier._adjustWip` registra no log
  - `WipRecalibrateTrigger` (WIP acima + bloqueios → sugere recalibrar)
  - `MeetingReason.wipRecalibrateWithBlocks` + strings PT/EN/ES
  - `DailySimulator._applyWipStressPenalty` (moral cai com WIP stress)
  - `MoveAppliedWithWarning('stop_starting')` ao puxar do backlog com entregáveis próximos
  - `MoveResult.newStateOrNull` getter unificado
  - 14 testes novos; golden hashes atualizados; 1434 testes passando
- [x] A.4 Reunião com ações e donos — commit `71768c3`
  - `MeetingAction` (dono, prazo, done/overdue)
  - `ActionAccord` + `VulnerabilityAccord` (universais em qualquer tipo de reunião)
  - `AccordKind.action` + `AccordKind.vulnerability`
  - `AccordCatalog._universal` para os dois novos tipos
  - `AccordApplier._registerAction` + `_applyVulnerability`
  - `GameState.pendingActions` + `GameState.transparentUntilDay`
  - `MeetingRecord.actions`
  - `MeetingService.conclude`: popula ata, verifica ações vencidas, penalidade de reunião vazia
  - `GameConfig`: 3 novas constantes de A.4
  - Strings PT/EN/ES; accord_labels e accord_dialogs atualizados
  - 19 testes novos; golden hashes atualizados; 1453 testes passando
- [x] A.2 Cauda de lead time — commit a ser gerado
  - `LeadTimePercentiles` (p50/p85/p95) + `flowEfficiency` em `FlowMetrics`
  - `FlowMetricsCalculator`: percentis por interpolação R7, flow efficiency
  - `PostMortemRecord` + `PostMortemBuilder` (5 Porquês a partir do log)
  - `TailLeadTimeTrigger` (dispara uma vez por card acima do p85)
  - `MeetingReason.tailLeadTime`
  - `GameState.postMortemLog`
  - `GameEngine.killCard` + `reclassifyCard` + `recordPostMortem`
  - `GameCard.copyWith(clearDueDay: true)`
  - `GameConfig`: 5 novas constantes de A.2
  - Strings PT/EN/ES
  - 23 testes novos
- [x] A.1 Dependências — commit a ser gerado
  - `DependencySlaChecker` (SLA de dependência: dentro, no limite, estourado)
  - `AgingDependencyTrigger` (bloqueio de dependência acima do SLA)
  - `DependencyWipTrigger` (WIP de dependências excedido)
  - `MeetingReason.agingDependency` + `MeetingReason.dependencyWipExceeded`
  - `GameConfig`: 3 novas constantes de A.1
  - `MeetingAdvisor` atualizado com os 3 novos triggers
  - Strings PT/EN/ES
  - 12 testes novos; 1488 testes passando

## Decisões tomadas

- Loja só com Câmbio e Poderes; **treinamento é comprado só no `TeamSheet`**, sem aba na Loja (3.3).
- Treino pago com a tesouraria da partida, exige economia ligada; sem cancelamento/reembolso na v1.
- Gorse Bele: sorteio **uma vez por dia de jogo**, aviso prévio D→D+1, padrão **cancelar** (`maxAdiamentos = 0`), intervalo 5 dias, limiar 50% (valores finais saem da simulação 1.4).
- Adiantar dias: `skipDays` + 1 dia por vez com paradas; aviso prévio é condição de parada, **não** desabilita o botão. "Fim do sprint" = **fim da rodada** (10 dias).
- A partida não é salva hoje: `trainedDomains` e avanço em curso ficam em memória.
- **Decisão 1 (Quiz):** botão próprio na home — adotada a proposta do plano.
- **Decisão 2 (Treinamento):** pago com dinheiro da partida (tesouraria) — adotada a proposta do plano.
- **Decisão 3 (Gorse Bele):** Calma/Normal/Caos basta como configuração — adotada a proposta do plano.
- **Decisão 4 (Adiantar):** opções +1 / +3 dias bastam; sem "até o fim da rodada" na v1 — adotada a proposta do plano.

## Decisões em aberto (seção 7 do plano)

Todas resolvidas — ver "Decisões tomadas" acima.

Podem começar sem resposta: **1.1–1.4 e 2.1–2.2**.

## Armadilhas já identificadas

- Probabilidade por dia não pode coexistir com sorteio por tick: por isso a 1.1 mantém os valores atuais e os novos entram na 1.2.
- `GorseBeleEventState.copyWith` usa `??` e não zera campos: `omenDay` precisa de `clearOmen`.
- O árbitro de IA consome a decisão "no próximo tick": adaptar para consultar em D e consumir em D+1, com fallback offline (isso é a **1.3a**; na 1.2 a IA fica de fora).
- O teste de equivalência reinvoca `fastForward` com os dias restantes (o avanço para no aviso prévio).
- Especialista não pega cards de outra área: o ganho do treino é acesso, não velocidade (ver 3.2).

## Revisão final do plano (2026-10-15): o que mudou e por quê

Segunda leitura completa do plano. Decisões tomadas:

| # | Achado | Decisão | Motivo |
|---|--------|---------|--------|
| 1 | A sessão 1.2 acumulava estado novo, avaliação diária, valores novos, reescrita de testes **e** adaptação da IA: grande demais e arriscada. | A IA e o aviso prévio saem da 1.2 e vão para a **1.3a**. Na 1.2 a aparição ocorre no dia do sorteio, com o juiz offline síncrono. | Mantém o jogo funcional entre as sessões e respeita 1 tarefa por sessão. O SCRATCHPAD estava inconsistente com isso e foi corrigido. |
| 2 | "Reunião sugerida obrigatória" como condição de parada do avanço não existe como conceito no código; parar em toda sugestão interromperia o avanço o tempo todo. | Para **uma vez por nova sugestão**; a 2.2 valida na prática se só as urgentes devem parar. | Evita adiantar ficar inútil. Deixado como ponto de validação, não como regra fechada, porque depende de como `MeetingSuggestion` se comporta. |
| 3 | O cabeçalho do plano ainda dizia "proposta para alinhamento". | Trocado por "revisado e aprovado para começar", com link ao SCRATCHPAD. | Quem abrir o plano deve ver o estado real. |
| 4 | `MeetingSchedule` usa `_clock.now()` (tempo real), não dia de jogo. | **Sem mudança.** Reunião tem duração em tempo real; só o dia de jogo é adiantado, e a reunião já cobra dias via `penalize`. | Verificado no código: não afeta o avanço. |

**Não mudei de propósito:** nomes e valores de parâmetros (dependem das simulações 1.4 e 4.1) e a divisão das etapas 3 e 4 (já em sessões pequenas). **Risco residual:** nomes de métodos/classes novos no plano são propostas; a sessão que os cria confirma no código antes de usar.

## Convenções a lembrar ([guia](./boas_praticas_de_conversa_com_o_copilot.md#convenções-do-projeto-que-o-copilot-deve-respeitar))

Telas por pasta · sem lógica em widget · I/O atrás de interface · cores só em `AppColors` · strings nos três `.arb` · domínio puro com `Random` e relógio injetados.

## Checklist de fim de sessão

- [ ] `make format` executado (obrigatório antes de qualquer commit)
- [ ] `make ci` passa (get + l10n + format-check + analyze + test)
- [ ] Strings novas nos três `.arb` (`pt`, `en`, `es`)
- [ ] Nenhuma cor fora do `AppColors`; nenhuma regra de jogo em widget
- [ ] Documentação de jogador atualizada se a regra mudou (README, `how_to_play`)
- [ ] Este SCRATCHPAD atualizado (feito, pendente, decisões)
- [ ] Commit pequeno citando a seção do plano + `git push`

## Log

| Data | Sessão | Resumo | Commit |
|------|--------|--------|--------|
| 2026-10-15 | — | Plano criado e revisado (arquivo de plano removido); nenhuma implementação iniciada | — |
| 2026-10-15 | — | Segunda revisão: 1.2 dividida (IA/aviso → 1.3a), parada por sugestão de reunião refinada, status do plano atualizado | — |
| 2026-10-15 | 2.1 | `skipDays` em `GameClockControl` e `RealTimeGameClock`; testes de fração de dia e acúmulo independente de `penalize`; `ManualGameClock` atualizado | `bbd01a6` |
| 2026-10-15 | 2.2 | `SessionFastForwardHandler` (função `fastForward` + sealed `FastForwardResult`); `GameEngine.clockControl`; `GameSession.fastForward`; `LocalGameSession` com `_isFastForwarding` e tick ignorado durante avanço; 12 testes | `3d4512a` |
| 2026-10-15 | style | Aplica dart format nos arquivos da Gorse Bele (formatação pura) | `568fb04` |
| 2026-10-15 | 2.3 | `FastForwardButton` widget; `BoardController.fastForward`; integrado no `_BoardAppBar`; strings nos 3 `.arb`; 5 testes de widget | `d6e48a1` |
| 2026-10-15 | 1.5a | `GorseBeleMode` enum; `GameSettings.gorseBeleMode`; `SettingsController.setGorseBeleMode`; `SharedPreferencesSettingsStore` persiste modo; seletor de 3 chips na `SettingsScreen`; strings nos 3 `.arb` | `f753dc1` |
| 2026-10-15 | 1.5b | `GorseBeleParams.forMode()`; `SessionTickHandler` aceita `gorseBeleMode`; `LocalGameSession` propaga modo; `LobbyScreen` recebe `gorseBeleMode`; `HomeScreen` passa `settings.gorseBeleMode` | `51e214a` |
| 2026-10-15 | 3.1 | `ShopScreen` + `ExchangeTab` com diálogo de confirmação; botão Quiz (`Icons.quiz`) na home abre `QuizScreen`; strings nos 3 `.arb`; 5 testes de widget + 1 teste na home | `cb1242a` |
| 2026-10-15 | 3.2 | `AngelsTab` extrai `_AngelCatalog` de `GemsScreen`; `ShopScreen` usa `AngelsTab`; `shop_button`, `gems_entry_button` e `CarriedCashBadge.onTap` abrem `ShopScreen` | `2883b8c` |
| 2026-10-15 | 3.3 | Remove `GemsScreen` e `gems_quiz_flow_test.dart`; migra testes de câmbio e vitrine para `shop_screen_test.dart` | `c688345` |
| 2026-10-15 | 4.1 | Parâmetros de treino em `EconomyParams`; script `training_balance_simulation.dart` (6 perfis × 4 combinações); break-even dia 3–4 — parâmetros aprovados | `a504a7a` |
| 2026-10-15 | 4.2 | `TrainingCatalog` com 12 pares próximos, tabela simétrica, `distance()` e `cost()`; 9 testes | `0f4c8a4` |
| 2026-10-15 | 4.3a | `Professional`: +`trainedDomains`, +`trainingDomain`, `copyWith` com `clearTrainingDomain/UntilDay`; `CardEligibility` considera `trainedDomains`; `StaffService.fireProfessional` limpa campos; `GorseBelePossession.candidates` exclui quem treina | `f6a3c55` |
| 2026-10-15 | 4.4 | `GameSession.trainProfessional`; `LocalGameSession` implementa e emite `professionalTrainingStarted`; `SessionTickHandler` chama `completePendingTrainings` por dia e emite `professionalTrainingCompleted`; `GameEventType` +2 tipos; mocks atualizados | `d43cbb2` |
| 2026-10-15 | 4.5 | Botão "Treinar" no `TeamSheet`; `_TrainingDialog` com lista de áreas, custo, distância e motivo de bloqueio; `board_screen.dart` delega para `GameSession.trainProfessional`; `AppColors.mutedText` no lugar de `Colors.grey`; strings nos 3 `.arb` | `ac3f6cc` |
| 2026-10-24 | troca-parcial | `GemRules.clampSelection`; `ExchangeQuote`; `CashToGemsExchanger.exchange(int)` + `canExchange` + `quote`; `ExchangeConfirmDialog` extraído; `ExchangeAmountPicker` (slider + Máx); `ExchangeTab` → StatefulWidget (seleção inicial 1 gema R4, clamp R7); strings nos 3 `.arb`; 36 testes | `5a8e2e1` |
| 2026-10-25 | B (parcial) | Parte B do KAIZEN: `AbsurdTaskComposer` (8 áreas × PT/EN/ES); `CardPromptBuilder` e `CreativeSeedPicker` integrados ao `CardGenerator`; `_generic`/`_recycled` removidos; `SeriesMarkerDetector` corrigido (v1/parte1 não casam) e integrado ao parser; `cardAvoidListSize` 8→40, `maxRegenerationAttempts` 3→5; testes: `series_marker_detector_test`, `absurd_task_composer_test`, parser com série, generator com composer; 1420 testes passando. Pendente: expansão de templates (≥30/área) | `d646ffb` |
| 2026-10-25 | B (templates) | 8 arquivos `*_catalog_templates.dart` (214 templates novos em PT/EN/ES, 3 passos, 30+ por área); `kCardTemplates` os anexa; commita `card_prompt_builder.dart` e `creative_seed_picker.dart`, que faltavam no `d646ffb`; testes: detector de série por palavra inteira, `card_factory_test` usa `kCardTemplates.length`, loop do banco esgotado limitado a +60; 1420 testes passando | `5c9f026` |
| 2026-10-25 | A.3 | WIP dinâmico: `WipAdjustmentRecord` + `GameState.wipAdjustmentLog`; `AccordApplier._adjustWip` registra no log; `WipRecalibrateTrigger` (WIP acima + bloqueios → sugere recalibrar); `MeetingReason.wipRecalibrateWithBlocks` + strings PT/EN/ES; `DailySimulator._applyWipStressPenalty`; `MoveAppliedWithWarning('stop_starting')` ao puxar com entregáveis próximos; `MoveResult.newStateOrNull`; 14 testes novos; golden hashes atualizados; 1434 testes passando | `aa20e33` |
| 2026-10-25 | A.4 | Reunião com ações e donos: `MeetingAction`; `ActionAccord` + `VulnerabilityAccord` (universais); `AccordKind.action/vulnerability`; `AccordCatalog._universal`; `AccordApplier._registerAction/_applyVulnerability`; `GameState.pendingActions/transparentUntilDay`; `MeetingRecord.actions`; `MeetingService.conclude` com ata de ações, verificação de vencidas e penalidade de reunião vazia; 3 constantes em `GameConfig`; strings PT/EN/ES; 19 testes novos; golden hashes atualizados; 1453 testes passando | `71768c3` |
| 2026-10-25 | A.2 + A.1 | Cauda de lead time e dependências: `LeadTimePercentiles` (p50/p85/p95) + `flowEfficiency` em `FlowMetrics`; `FlowMetricsCalculator` com percentis R7; `PostMortemRecord` + `PostMortemBuilder` (5 Porquês); `TailLeadTimeTrigger`; `GameState.postMortemLog`; `GameEngine.killCard/reclassifyCard/recordPostMortem`; `GameCard.copyWith(clearDueDay)`; `DependencySlaChecker` (SLA dentro/limite/estourado); `AgingDependencyTrigger`; `DependencyWipTrigger`; `MeetingReason` +3 valores; `MeetingAdvisor` +3 triggers; `GameConfig` +8 constantes; strings PT/EN/ES; 35 testes novos; 1488 testes passando | `4428620` |
| 2026-10-25 | UI (A.4 + A.2) | `PendingActionsPanel` (chips com dono/prazo/status no board); diálogos para `ActionAccord` (personagem + descrição + prazo) e `VulnerabilityAccord` (personagem + duração) em `accord_dialogs.dart`; `board_screen.dart` integra o painel; strings PT/EN/ES: `pendingActionsTitle/Empty/Owner/Due/Overdue/Done`, `accordActionDescription/DueDays`, `accordVulnerabilityDuration`; `MockGameSession.currentGameState` corrigido no teste; 1488 testes passando | `dc1ea18` |
| 2026-10-25 | fix | Auditoria KAIZEN + SCRATCHPAD: todos os itens implementados. Correção de bug: `CardGenerator` criava dois `SeededRandomSource.fromTime()` independentes (sementes distintas para `_composer` e `_promptBuilder`). Migrado para `factory` + construtor privado com `effectiveRandom` compartilhado; 1490 testes passando | `87d1ae4` |
| 2026-10-25 | Pausas E1 | Etapa 1 das pausas espontâneas: `GameConfig` +7 constantes de pausa (`workdayMinutes=480`, `pauseBaseChancePerDay`, `pauseMaxPerDayPerPro`, `pauseMinGapMinutes`, `pauseCrowdThreshold`, `cardGameQuorum`, `policyPauseSuppressionFactor`); `LedgerKind.idleTime`; `DayTimeLedger` + `TimeBlock` + `TimeCategory` em `lib/domain/pauses/`; `GameState.dayTimeLedger`; `DailyWorkPlanner.plan` aceita `ledger` e escala capacidade pelo `productivityFactor`; `DailySimulator._simulateDay` passa ledger ao planner; 21 testes novos; 1511 testes passando | `1ebb40e` |
| 2026-10-25 | Pausas E2 | Etapa 2 das pausas espontâneas: `PauseKind` (10 pausas) + `PauseKindMeta`; `ProfessionalNeeds` (imutável, 6 necessidades); `NeedsProfile` + `NeedsRates` para os 11 personagens; `NeedsCalculator` (`advance`, `pauseChance`, `pauseWeights`, `applyPauseRelief`); 32 testes novos; 1543 testes passando | `09a6c71` |
| 2026-10-25 | Pausas E3 | Etapa 3 das pausas espontâneas: `PauseRecord`; `PauseStrategy` interface + `PauseAttempt` sealed; `CoffeePause` e `RestroomPause`; `PauseRegistry`; `PauseService.run` com `RandomSource` separado do motor; `GameState` +`professionalNeeds` +`pauseLog`; `DailySimulator._advanceNeeds` + integração opcional do `PauseService`; `EnginePartsConfig.pauseRandom`; `GameEngine` cria `pauseRng` determinístico; 9 testes novos; 1552 testes passando | `5133ef7` |
| 2026-10-25 | Pausas E4 | Etapa 4 das pausas espontâneas: `FlowMetrics` +`idleMinutesTotal/idleMinutesByPro/occupancyRate/topIdler`; `FlowMetricsCalculator.compute` aceita `DayTimeLedger?` e `hiredCount`; `BoardSynchronizer` propaga ledger em `flowMetrics/liveMetrics/synced/refresh/appendEvent`; teste de economia atualizado; 7 testes novos; 1559 testes passando | `f4b8d0b` |
| 2026-10-25 | Pausas E5 | Etapa 5 das pausas espontâneas: `CardGamePause` (quórum 4, recruta alwaysAcceptsInvite primeiro); `CakePause` (todos os disponíveis); `GossipPause` (2–3 aleatórios); `MeditationPause` (só Coach Trovão); `PauseRegistry` +4 estratégias; `PauseService._apply` registra ledger/needs/custo para todos os participantes; 16 testes novos; 1575 testes passando | `f8599d6` |
| 2026-10-25 | Pausas E6 | Etapa 6 das pausas espontâneas: `PauseMoodService` (apply: participantes→loyal, excluídos→frustrated; clearEffects); `GameState.pauseMoodEffects`; `BotMoodCalculator` consulta pauseMoodEffects com prioridade máxima; `DailySimulator` limpa efeitos no início do dia; `PauseService._apply` chama moodService; 6 testes novos; 1581 testes passando | `3a05ef4` |
| 2026-10-25 | Pausas E7 | Etapa 7 das pausas espontâneas: strings i18n PT/EN/ES (10 tipos de pausa + dayBar + idleSummary); `AppColors` +dayBar/pauseBadge; `pause_kind_labels.dart`; `PauseStatusBadge` (badge âmbar no avatar); `DayBarWidget` (barra 480 min colorida); `TeamSheetData` +pauseLog +dayTimeLedger; `TeamSheet` integra badge e barra; `BoardScreen` passa dados de pausa; ARB whitelist atualizada; 1581 testes passando | `2655378` |

## ⚠️ OBSERVAÇÃO OBRIGATÓRIA: PADRÕES DE QUALIDADE E BOAS PRÁTICAS

**Toda implementação deve seguir rigorosamente os princípios de engenharia de software, priorizando qualidade, legibilidade, manutenibilidade, segurança, escalabilidade e consistência arquitetural.**

- **SOLID:** aplique rigorosamente os cinco princípios de SOLID, respeitando responsabilidades bem definidas, baixo acoplamento e alta coesão.
- **Design Patterns:** utilize padrões de projeto quando forem adequados ao problema, evitando complexidade desnecessária, abstrações prematuras e overengineering.
- **Clean Code:** escreva código limpo, legível, expressivo e autodocumentado, com nomes significativos, funções pequenas, responsabilidades únicas e fluxo de execução claro.
- **Formatação obrigatória:** execute `make format` após as alterações para garantir a padronização automática do código. Nunca ignore esse comando.
- **DRY (Don't Repeat Yourself):** evite duplicação de lógica, regras de negócio e código. Extraia componentes reutilizáveis quando houver uma justificativa real.
- **KISS (Keep It Simple, Stupid):** prefira soluções simples, explícitas e fáceis de manter, sem sacrificar a qualidade arquitetural.
- **YAGNI (You Aren't Gonna Need It):** implemente apenas o que é necessário para os requisitos atuais, sem criar funcionalidades ou abstrações especulativas.
- **Separação de responsabilidades:** mantenha as camadas de apresentação, domínio, aplicação e infraestrutura devidamente isoladas, respeitando a arquitetura existente.
- **Princípios de domínio:** preserve as regras de negócio em seus respectivos contextos, evitando espalhá-las entre interfaces, controllers, componentes e serviços genéricos.
- **Consistência arquitetural:** antes de implementar qualquer funcionalidade, analise a estrutura do projeto, identifique os padrões existentes e siga as convenções estabelecidas. Não introduza novas abordagens sem justificativa técnica.
- **Tratamento de erros:** implemente tratamento explícito e apropriado de exceções, estados inválidos, falhas de integração e condições inesperadas. Nunca silencie erros ou utilize valores artificiais para mascarar falhas.
- **Segurança:** valide entradas, respeite as permissões e os limites de confiança, proteja dados sensíveis e aplique o princípio do menor privilégio. Nunca exponha credenciais, tokens ou informações confidenciais.
- **Testes automatizados:** crie ou atualize testes unitários, de integração e de ponta a ponta conforme o escopo e o risco da alteração. Teste também cenários negativos, limites e casos excepcionais.
- **Regressão:** preserve o comportamento existente fora do escopo da mudança. Não remova funcionalidades, regras de negócio ou validações sem autorização explícita.
- **Performance:** evite consultas redundantes, processamento desnecessário, problemas de N+1, renderizações excessivas e alocações evitáveis. Otimize com base em evidências, sem comprometer a legibilidade.
- **Tipagem e contratos:** utilize tipagem forte sempre que disponível, respeite interfaces e contratos existentes e evite tipos genéricos, coerções implícitas e o uso indiscriminado de `any`.
- **Legibilidade e manutenção:** evite funções gigantes, classes com múltiplas responsabilidades, condicionais excessivamente complexas, números mágicos, comentários redundantes e dependências desnecessárias.
- **Dependências:** reutilize as bibliotecas já adotadas pelo projeto sempre que possível. Não adicione dependências externas sem necessidade comprovada e avaliação de seus impactos.
- **Refatoração responsável:** refatore somente o necessário para viabilizar a solução ou melhorar objetivamente a qualidade do código relacionado. Evite alterações abrangentes e não relacionadas ao requisito.
- **Compatibilidade:** respeite as versões das linguagens, frameworks, bibliotecas, APIs e contratos existentes, considerando os impactos sobre os demais módulos e consumidores.
- **Logs e observabilidade:** registre informações úteis para diagnóstico, sem expor dados sensíveis ou gerar ruído excessivo.
- **Documentação:** atualize a documentação técnica quando houver mudanças relevantes em contratos, arquitetura, configurações, fluxos de negócio ou procedimentos de execução.
- **Decisões do dono do produto são incontestáveis:** o que o Cristian decidir deve ser executado exatamente como pedido, sem contestar, reinterpretar, limitar ou "melhorar" por conta própria. Dúvidas de entendimento podem ser perguntadas antes; depois da decisão, só se executa.

### Fluxo obrigatório de trabalho

1. **Analisar:** compreenda os requisitos, investigue o código existente e identifique os componentes e as regras de negócio envolvidos antes de alterar qualquer arquivo.
2. **Planejar:** defina a solução mais simples e consistente com a arquitetura atual, considerando impactos, dependências, riscos e cenários de erro.
3. **Implementar:** desenvolva uma solução coesa, reutilizável quando apropriado, sem duplicações desnecessárias ou desvios dos padrões do projeto.
4. **Validar:** execute `make format` e os testes, linters, verificações de tipos e demais validações disponíveis e pertinentes.
5. **Revisar:** verifique possíveis regressões, problemas de segurança, inconsistências arquiteturais, código morto, alterações não relacionadas e falhas nos cenários excepcionais.
6. **Concluir:** informe objetivamente o que foi implementado, quais validações foram executadas e eventuais limitações ou pendências.

### Regra inegociável

**Nunca considere uma implementação concluída apenas porque funciona no cenário principal.** A solução deve atender aos requisitos, respeitar a arquitetura existente, preservar os comportamentos esperados, possuir testes adequados e passar pelas verificações de qualidade aplicáveis.

Não ignore falhas de testes, não desabilite verificações para fazer o pipeline passar e não declare que uma validação foi executada com sucesso sem ter confirmado seu resultado.

**Commits sem coautoria do Copilot:** nenhum commit pode ter o Copilot (ou qualquer assistente de IA) como coautor. Não inclua trailers `Co-authored-by:` referentes ao Copilot na mensagem de commit. Se a ferramenta adicionar esse trailer automaticamente, remova-o antes de commitar (ou use `git commit --amend` / `git rebase` para retirá-lo de commits já criados e ainda não enviados).

**Qualidade de código não é opcional. Toda alteração deve ser implementada com responsabilidade técnica, simplicidade, consistência e foco na manutenção de longo prazo.**

## COMMITS
**Todos os commits que fizer, este arquivo deve ser atualizado e enviado junto**
---

## VIDA_PROPRIA_FASE2 — Progresso

### Feature A — Ausências em Reunião ✅
- `MeetingState`: adicionados `absentProfessionalIds` e `absenceReasons`
- `lib/domain/meetings/absence_reason_bank.dart`: banco PT/EN/ES por personagem (11 personagens + fallback genérico)
- `lib/domain/meetings/meeting_absence_service.dart`: `sortAbsences()` com chance base 0.15, bônus frustrado 0.15, máx 2 ausentes
- `MeetingService.trigger()`: integrado `MeetingAbsenceService`, adicionados `random` e `language` opcionais
- `GameConfig`: `meetingAbsentChance`, `meetingAbsentFrustratedBonus`, `meetingAbsentMaxPerMeeting`
- ARBs (pt/en/es): chaves de ausência + folga + distração + problema técnico adicionadas
- `test/domain/meetings/meeting_absence_test.dart`: 5 testes passando
