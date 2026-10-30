# ADR-009 — Ollama Externo ao Docker Compose

**Status:** Aceito
**Data:** 2026-10-30
**Autores:** Cristian Bernardes

## Contexto

O Ollama é um servidor de inferência de LLM local. Rodá-lo dentro de um container Docker junto com o
restante da stack traria desvantagens relevantes para este projeto:
- Duplicaria o consumo de GPU/CPU/RAM caso o desenvolvedor já tenha o Ollama rodando no host para
  outros projetos;
- Imagens de container de Ollama são pesadas e, quando configuradas para GPU, exigem runtime Nvidia
  dentro do container — complexidade desnecessária para quem só quer rodar o backend;
- O ciclo de vida de modelos (download, atualização, remoção) já é gerenciado pela instalação nativa
  do Ollama no host do desenvolvedor.

## Decisão

O Ollama **nunca** é declarado como serviço no `docker-compose.yml` deste projeto. Ele deve estar
instalado e em execução **diretamente no host** (ou em outra máquina da rede) do desenvolvedor. O
backend se conecta a ele exclusivamente via HTTP, usando a URL configurada pela variável de ambiente
`OLLAMA_BASE_URL` (ver `.env.example`), nunca com um valor hardcoded no código ou no Compose.

- Em Linux, quando o backend roda em container, a URL típica para alcançar o host é
  `http://172.17.0.1:11434` (IP da bridge padrão do Docker) ou `http://host-gateway:11434`, mapeado
  via `extra_hosts` no serviço do backend.
- Em desenvolvimento local sem container (execução direta via Poetry), a URL típica é
  `http://localhost:11434`.

No `docker-compose.yml` deste projeto, o serviço `backend` sobrescreve explicitamente
`OLLAMA_BASE_URL=http://172.17.0.1:11434` na seção `environment`, garantindo que, mesmo que o
`.env` local do desenvolvedor contenha `localhost` (valor correto apenas para execução fora de
container), o container sempre aponte para o host corretamente — nunca para si mesmo.

## Consequências

### Positivas
- Zero duplicação de recursos de GPU/CPU entre o Ollama do host e o restante da stack.
- Simplifica o `docker-compose.yml` do projeto — ele continua responsável apenas pelos serviços que
  o projeto efetivamente possui (banco, broker, backend).
- O desenvolvedor mantém controle total do ciclo de vida de modelos fora do projeto.

### Negativas / Trade-offs
- Exige que o desenvolvedor tenha o Ollama instalado e em execução manualmente antes de subir o
  Compose — documentado no `README.md` e no `Makefile` (`make check-ollama`, se aplicável).
- A URL de acesso ao Ollama varia entre "rodando em container" e "rodando direto no host", por isso é
  sempre resolvida via `OLLAMA_BASE_URL`, nunca fixada no código.

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|-------------------------|
| Serviço `ollama` dentro do `docker-compose.yml` | Decisão explícita do dono do produto: Ollama deve ser sempre externo, nunca em container, para este projeto. |
| Hardcode da URL do Ollama no código | Viola a premissa inegociável de que toda configuração externa deve vir de `.env`. |
