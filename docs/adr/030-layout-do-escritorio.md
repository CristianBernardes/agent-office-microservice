# ADR-030 — Layout do escritório

**Status:** Aceito

## Contexto
A tabela `office_layout` (ADR-017) guarda a planta do escritório que o frontend desenha. O frontend é feito pelo usuário; o backend só persiste e serve o JSON.

## Decisão
- Entidade `OfficeLayout(name, layout)`: `layout` é um objeto JSON opaco e não vazio (`layout.invalid` caso contrário).
- Porta `ILayoutRepository` (`save`, `get`), repositórios em memória e Postgres (upsert).
- Rotas `GET /layout/{name}` (404 localizado se não existir) e `PUT /layout/{name}`.

## Consequências
O backend não conhece o formato da planta, então o frontend evolui livremente. Sem validação de schema por escolha (YAGNI).
