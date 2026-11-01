# ADR-054 — Responsabilidades por cargo e poderes do dono do produto

**Status:** Aceito
**Data:** 2026-11-01
**Autores:** Cristian Bernardes

## Contexto

Só devs e Tech Lead recebiam tarefas automaticamente; uma tarefa de "contratar" ou de "analisar
dados" caía em um dev. Além disso, o dono do produto (o usuário) não podia reatribuir tarefas,
redefinir prioridades, arrastar cartões livremente nem demitir pelo frontend.

## Decisão

- **Roteamento por área** (`domain/services/task_routing.py`, puro e determinístico): lista fixa de
  palavras-chave pt/en por cargo (RH: contratar/hire; Analista de Dados: dados/SQL/data; Consultor:
  mercado/concorrentes/market; Tech Lead: arquitetura/deploy; Dev: implementar/API). Casa no início
  de palavra e ignora acentos. A etiqueta `[cargo]` criada pelas reuniões vence as palavras-chave.
- **Executores** (`EXECUTOR_ROLES`): devs, Tech Lead, Analista de Dados, RH e Consultor executam e
  movem cartões na matriz (`task_workflow`); QA testa/revisa; PO/SM planejam e coordenam.
- Sem área reconhecida, cai nos cargos-reserva (Dev Sênior, Dev Júnior, Tech Lead), escolhendo o
  menos carregado. Vale ao sair do backlog (`MoveTaskUseCase`) e na atribuição do ciclo de trabalho.
- **Poderes do dono**: `owner_override` no `POST /tasks/{id}/move` ignora a matriz (qualquer coluna);
  `PUT /tasks/{id}/owner` e `PUT /tasks/{id}/priority` reatribuem e repriorizam. O frontend permite
  arrastar cartões, editar responsável/prioridade em modal e demitir (com confirmação).
- Demitir devolve ao fluxo as tarefas abertas ("a fazer", sem responsável) e publica o status.

## Consequências

Cada cargo assume o que é da sua área; o usuário tem a palavra final. Palavras-chave exigem
manutenção da lista; a alternativa (classificar com LLM) foi descartada por custo e variabilidade.
