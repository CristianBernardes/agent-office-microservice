# ADR-047 — Frontend Svelte 5 construído neste repositório (revoga a premissa de autoria externa)

**Status:** Aceito
**Data:** 2026-11-01
**Autores:** Cristian Bernardes

## Contexto

O ADR-015 e o SCRATCHPAD assumiam que o frontend seria feito pelo autor do produto. O autor
decidiu que o frontend também deve ser construído aqui; ele forneceu apenas as imagens
(`frontend/images/`: sprites por papel e plantas do escritório).

## Decisão

- Svelte 5 + TypeScript + Vite; testes com Vitest + Testing Library; `svelte-check` como lint de tipos.
- Sem Phaser: o escritório é um mapa DOM/CSS sobre `escritorio_moderno.png`; cada agente é um
  `div` com sprite-sheet animado por CSS (`steps()`), frames de 48×96 px.
- Tempo real: MQTT sobre WebSocket (`office/agents/{id}/status|thought|action`) via `mqtt.js`;
  dados iniciais pela API REST.
- Configuração só por `VITE_*` em `frontend/.env.example` (URL da API, URL do broker WS, idioma
  padrão, chave Pix). Nada hardcoded.
- i18n pt/en próprio (dicionários tipados), troca em tempo de execução, preferência em `localStorage`.
- Um Dockerfile por microserviço: `frontend/Dockerfile` (build com Node, serviço com nginx); o
  navegador usa as portas externas (70xx), os containers usam as convencionais.

## Consequências

- O ADR-015 permanece válido quanto a CORS/listagem; a parte "frontend feito pelo autor" é revogada.
- Docs que citam Phaser/Zustand ficam obsoletas e serão reescritas.
- Nova etapa de CI (lint, testes, build do frontend).
