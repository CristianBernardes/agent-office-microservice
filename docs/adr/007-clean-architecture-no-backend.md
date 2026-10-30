# ADR-007 — Clean Architecture no Backend

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

O projeto se propõe explicitamente como peça de portfólio técnico, demonstrando SOLID, baixo
acoplamento e alta coesão (ver `docs/SCRATCHPAD.md`). Para isso, a lógica de negócio não pode
depender de frameworks ou de detalhes de infraestrutura (banco, MQTT, HTTP, LLM).

## Decisão

Organizar o backend em quatro camadas concêntricas, com a regra de dependência apontando sempre
para dentro:

```
presentation → application → domain
infrastructure → domain (implementa interfaces definidas no domain)
```

- **`domain/`** — entidades, value objects, eventos e **interfaces** (portas). Zero dependências de
  bibliotecas de terceiros, exceto a biblioteca padrão do Python.
- **`application/`** — casos de uso que orquestram entidades de domínio através das interfaces,
  sem conhecer qualquer implementação concreta (FastAPI, aiomqtt, asyncpg, etc.).
- **`infrastructure/`** — implementações concretas das interfaces do domínio (MQTT, LLM,
  PostgreSQL, sistema de arquivos).
- **`presentation/`** — pontos de entrada (API HTTP via FastAPI) e composição de dependências
  (injeção de dependência via *factories* e `Depends`).

A Injeção de Dependência é o mecanismo que conecta as camadas em tempo de execução: casos de uso
recebem interfaces no construtor; a camada de apresentação decide, via *factories*, qual
implementação concreta injetar.

## Consequências

### Positivas
- Entidades e casos de uso são testáveis unitariamente sem qualquer infraestrutura real (banco,
  rede, broker).
- Troca de implementação (ex.: `OllamaAdapter` → `OpenAiAdapter`, `MqttMessageBus` →
  `InMemoryMessageBus`) não exige alterar `application/` nem `domain/`.

### Negativas / Trade-offs
- Mais arquivos e indireção do que uma abordagem "tudo em um módulo" — aceito como custo necessário
  para atingir os objetivos de qualidade e manutenibilidade do projeto.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Estrutura MVC simples (models/views/controllers) | Não isola a lógica de negócio de detalhes de framework/infraestrutura da mesma forma que Clean Architecture; tende a acoplar regras de negócio a objetos do ORM/framework. |
| "Big ball of mud" orientado a scripts | Inviabiliza testes unitários isolados e viola todos os princípios SOLID exigidos pelo projeto. |
