# RFC-004 — Contrato da API HTTP

**Status:** Aceito
**Data:** 2026-11-01
**Autor:** Cristian Bernardes

## Resumo
Contrato das rotas HTTP consumidas pelo frontend. Routers são camadas finas: validam entrada, chamam um caso de uso e traduzem `DomainError` em status HTTP.

## Convenções
- **Idioma:** o cabeçalho `Accept-Language` (`pt` ou `en`) localiza mensagens de erro; sem ele vale `APP_LANGUAGE`.
- **Erros:** `{"detail": "<mensagem localizada>"}`. 404 não encontrado, 409 transição inválida, 422 validação.
- **Identificadores:** UUID. Datas em ISO-8601 UTC.
- Documentação interativa em `/docs` (OpenAPI).

## Rotas
| Método | Caminho | Descrição |
|---|---|---|
| GET | `/health` | Saúde do serviço |
| GET/POST | `/agents` | Lista / contrata agente |
| POST | `/agents/{id}/fire`, `/agents/{id}/think` | Demite / aciona raciocínio |
| GET/POST | `/agents/{id}/memories`, POST `/recall` | Memória do agente e busca semântica |
| GET | `/agents/{id}/relationships` | Vínculos (ADR-027) |
| GET/POST | `/tasks` | Kanban |
| POST | `/tasks/{id}/assign`, `/complete`, `/move` | Transições (matriz por papel) |
| GET | `/tasks/{id}/transitions` | Histórico |
| POST/GET | `/goals` | Objetivo do usuário (dispara reunião) |
| POST | `/messages`; GET `/sessions/{id}/messages` | Chat |
| GET | `/goals/{id}/meetings` | Reuniões do objetivo |
| POST | `/meetings`, `/meetings/{id}/finish` | Cerimônias (ADR-033) |
| POST | `/research` | Pesquisa gera artefato `.md` (ADR-034) |
| GET/PUT | `/layout/{name}` | Layout do escritório (ADR-030) |
| GET | `/activity` | Feed de atividade |

## Compatibilidade
Mudanças que quebrem este contrato exigem nova RFC; campos novos opcionais são permitidos.
