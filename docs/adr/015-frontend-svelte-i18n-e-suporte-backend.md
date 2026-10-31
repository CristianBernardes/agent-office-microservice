# ADR-015 — Frontend Svelte (pt/en) e suporte de backend (listagem + CORS)

**Status:** Aceito
**Data:** 2026-10-31
**Autores:** Cristian Bernardes

## Contexto

O frontend foi decidido como Svelte + TypeScript (Rodada 3). Os sprites dos 9 papéis já existem em
`frontend/images/sprites/{role}/{estado}.png` (tiras de frames 48×96, 24 frames por animação de 1152 px).
O backend não tinha como listar agentes nem aceitava requisições de outra origem.

## Decisão

- `frontend/`: Svelte 5 + TypeScript + Vite + Vitest. Sem Phaser/escritório completo nesta rodada
  (YAGNI): primeiro corte = painel com os agentes animados, contratar, despachar objetivo e demitir.
- Sprites consumidos **direto de `frontend/images/sprites/`** via `import.meta.glob` (sem duplicar assets).
  O mapeamento status → animação fica em um módulo puro e testado (`sprites.ts`):
  idle→`aguardando_uma_tarefa`, thinking→`analisando_documentacao_e_adrs`,
  working→`trabalhando_no_computador`, talking→`participando_de_reunioes`,
  offline→`agente_inativo_por_muito_tempo`.
- i18n pt/en desde o início (ADR-012): dicionários tipados, idioma inicial pelo navegador,
  seletor na tela, e envio de `Accept-Language` à API para que os erros venham localizados.
- URL da API em `VITE_API_BASE_URL` (zero hardcode).
- Backend: `GET /agents` (reuso de `list_all`) e CORS configurado por `CORS_ALLOWED_ORIGINS`
  (lista separada por vírgula; padrão = origem do Vite local).

## Consequências

- Tempo real via MQTT-WebSocket fica para uma rodada futura; por ora o painel faz polling leve.
