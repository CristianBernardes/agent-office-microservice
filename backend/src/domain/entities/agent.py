"""Entidade de domínio ``Agent`` e os tipos que a compõem.

Representa um agente de IA com um papel (``Role``) no time simulado, um estado de
execução (``AgentStatus``) e um perfil de personalidade (``Personality``, nos moldes
do modelo Big Five). A entidade é propositalmente agnóstica a LLM, MQTT ou banco de
dados — essas responsabilidades pertencem à camada de infraestrutura, conectada via
injeção de dependência nas camadas superiores (ver ADR-007).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError
from src.domain.value_objects.identifiers import AgentId, TaskId


# Bloco: papéis disponíveis para um agente no time simulado.
# O conjunto fechado de papéis é intencional (ver ADR-003): cada papel determina,
# em camadas de infraestrutura, o prompt e as ferramentas do agente, mas a entidade
# de domínio não precisa (e não deve) conhecer esses detalhes.
class Role(str, Enum):
    PRODUCT_OWNER = "product_owner"
    SCRUM_MASTER = "scrum_master"
    TECH_LEAD = "tech_lead"
    DEV_SENIOR = "dev_senior"
    DEV_JUNIOR = "dev_junior"
    QA_ENGINEER = "qa_engineer"
    DATA_ANALYST = "data_analyst"
    HR_MANAGER = "hr_manager"
    PRODUCT_CONSULTANT = "product_consultant"


# Bloco: estados possíveis de um agente (ver RFC-003 para transições detalhadas).
class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    TALKING = "talking"
    OFFLINE = "offline"


# Bloco: perfil de personalidade do agente, inspirado no modelo Big Five.
# Cada traço varia entre 0.0 (mínimo) e 1.0 (máximo). A validação dos limites é
# responsabilidade do próprio value object, nunca de quem o instancia.
@dataclass(frozen=True, slots=True)
class Personality:
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

    def __post_init__(self) -> None:
        for trait_name, trait_value in (
            ("openness", self.openness),
            ("conscientiousness", self.conscientiousness),
            ("extraversion", self.extraversion),
            ("agreeableness", self.agreeableness),
            ("neuroticism", self.neuroticism),
        ):
            if not 0.0 <= trait_value <= 1.0:
                raise ValueError(
                    f"O traço de personalidade '{trait_name}' deve estar entre 0.0 e 1.0, "
                    f"recebido: {trait_value}"
                )


# Bloco: entidade de domínio ``Agent``.
# Mantém apenas as regras de negócio diretamente ligadas ao ciclo de vida de um
# agente. Qualquer decisão sobre "o que fazer" (prompt, LLM, ferramentas) é
# responsabilidade de camadas superiores, nunca desta entidade.
@dataclass(slots=True)
class Agent:
    agent_id: AgentId
    name: str
    role: Role
    personality: Personality
    llm_model: str
    status: AgentStatus = field(default=AgentStatus.IDLE)
    current_task_id: TaskId | None = field(default=None)

    def start_thinking(self) -> None:
        """Move o agente para o estado de pensamento (processamento via LLM)."""
        if self.status == AgentStatus.OFFLINE:
            raise InvalidStateTransitionError(
                f"Agente '{self.name}' está OFFLINE e não pode iniciar um pensamento."
            )
        self.status = AgentStatus.THINKING

    def assign_task(self, task_id: TaskId) -> None:
        """Atribui uma tarefa ao agente, movendo-o para o estado de trabalho.

        Só é permitido atribuir uma nova tarefa quando o agente está ``IDLE``,
        evitando que um agente ocupado receba trabalho concorrente de forma
        silenciosa (ver RFC-003).
        """
        if self.status != AgentStatus.IDLE:
            raise InvalidStateTransitionError(
                f"Agente '{self.name}' está '{self.status.value}' e não pode receber "
                "uma nova tarefa — apenas agentes 'idle' podem ser alocados."
            )
        self.current_task_id = task_id
        self.status = AgentStatus.WORKING

    def complete_task(self) -> None:
        """Conclui a tarefa atual do agente, retornando-o ao estado ``IDLE``."""
        if self.status != AgentStatus.WORKING:
            raise InvalidStateTransitionError(
                f"Agente '{self.name}' está '{self.status.value}' e não possui uma "
                "tarefa em andamento para concluir."
            )
        self.current_task_id = None
        self.status = AgentStatus.IDLE

    def go_offline(self) -> None:
        """Marca o agente como indisponível (ex.: demitido do time)."""
        self.status = AgentStatus.OFFLINE
        self.current_task_id = None
