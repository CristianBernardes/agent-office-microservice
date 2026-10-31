"""Catálogo de mensagens traduzidas (pt/en) para erros de negócio."""

from __future__ import annotations

from src.domain.localization.language import Language

# Bloco: catálogo chave -> idioma -> modelo de texto (str.format).
MESSAGES: dict[str, dict[Language, str]] = {
    "task.cannot_complete": {
        Language.EN: "Task '{title}' is '{status}' and cannot be completed — "
        "only 'in_progress' tasks can be completed.",
        Language.PT: "Tarefa '{title}' está '{status}' e não pode ser concluída — "
        "apenas tarefas 'in_progress' podem ser concluídas.",
    },
    "task.invalid_move": {
        Language.EN: "Task '{title}' cannot move from '{from_status}' to '{to_status}'.",
        Language.PT: "A tarefa '{title}' não pode ir de '{from_status}' para '{to_status}'.",
    },
    "task.move_forbidden": {
        Language.EN: "Role '{role}' is not allowed to move a task "
        "from '{from_status}' to '{to_status}'.",
        Language.PT: "O papel '{role}' não pode mover uma tarefa "
        "de '{from_status}' para '{to_status}'.",
    },
    "task.not_found": {
        Language.EN: "Task with ID '{task_id}' was not found.",
        Language.PT: "Tarefa com ID '{task_id}' não foi encontrada.",
    },
    "artifact.cannot_request_review": {
        Language.EN: "Artifact '{title}' is '{status}' and cannot be sent for review — "
        "only 'draft' artifacts can be reviewed.",
        Language.PT: "Artefato '{title}' está '{status}' e não pode ser enviado para revisão — "
        "apenas artefatos 'draft' podem ser revisados.",
    },
    "artifact.cannot_approve": {
        Language.EN: "Artifact '{title}' is '{status}' and cannot be approved — "
        "only 'in_review' artifacts can be approved.",
        Language.PT: "Artefato '{title}' está '{status}' e não pode ser aprovado — "
        "apenas artefatos 'in_review' podem ser aprovados.",
    },
    "artifact.cannot_archive": {
        Language.EN: "Artifact '{title}' is '{status}' and cannot be archived — "
        "only 'approved' artifacts can be archived.",
        Language.PT: "Artefato '{title}' está '{status}' e não pode ser arquivado — "
        "apenas artefatos 'approved' podem ser arquivados.",
    },
    "artifact.not_found": {
        Language.EN: "Artifact with ID '{artifact_id}' was not found.",
        Language.PT: "Artefato com ID '{artifact_id}' não foi encontrado.",
    },
    "agent.not_found": {
        Language.EN: "Agent with ID '{agent_id}' was not found.",
        Language.PT: "Agente com ID '{agent_id}' não foi encontrado.",
    },
    "agent.offline_cannot_think": {
        Language.EN: "Agent '{name}' is OFFLINE and cannot start thinking.",
        Language.PT: "Agente '{name}' está OFFLINE e não pode iniciar um pensamento.",
    },
    "agent.not_thinking": {
        Language.EN: "Agent '{name}' is '{status}' and is not thinking.",
        Language.PT: "Agente '{name}' está '{status}' e não está pensando.",
    },
    "agent.cannot_receive_task": {
        Language.EN: "Agent '{name}' is '{status}' and cannot receive a new task — "
        "only 'idle' agents can be assigned.",
        Language.PT: "Agente '{name}' está '{status}' e não pode receber uma nova tarefa — "
        "apenas agentes 'idle' podem ser alocados.",
    },
    "agent.no_task_to_complete": {
        Language.EN: "Agent '{name}' is '{status}' and has no task in progress to complete.",
        Language.PT: "Agente '{name}' está '{status}' e não possui uma tarefa em andamento "
        "para concluir.",
    },
    "agent.invalid_trait": {
        Language.EN: "Personality trait '{trait_name}' must be between 0.0 and 1.0, "
        "got: {trait_value}",
        Language.PT: "O traço de personalidade '{trait_name}' deve estar entre 0.0 e 1.0, "
        "recebido: {trait_value}",
    },
    "tool.permission_denied": {
        Language.EN: "Role '{role}' is not allowed to use tool '{tool}'.",
        Language.PT: "O papel '{role}' não tem permissão para usar a ferramenta '{tool}'.",
    },
    "tool.not_implemented": {
        Language.EN: "Tool '{tool}' does not have a handler implemented yet in this round.",
        Language.PT: "A ferramenta '{tool}' ainda não possui um handler implementado "
        "nesta rodada do projeto.",
    },
}


# Bloco: traduz uma chave para o idioma pedido; chave desconhecida devolve a própria chave.
def translate(message_key: str, language: Language, **params: object) -> str:
    templates = MESSAGES.get(message_key)
    if templates is None:
        return message_key
    template = templates.get(language) or templates[Language.EN]
    return template.format(**params)
