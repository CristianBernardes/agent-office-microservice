"""Identificadores tipados (value objects) usados nas entidades do domínio.

Cada identificador é um wrapper imutável sobre ``uuid.UUID``. O objetivo é evitar o
chamado "primitive obsession": sem esses tipos, seria possível passar o ID de uma
tarefa onde se espera o ID de um agente sem qualquer erro em tempo de
desenvolvimento, já que ambos seriam apenas ``UUID``. Com tipos distintos, o `mypy`
captura esse erro antes mesmo de o código rodar.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


# Bloco: identificador tipado de agente.
# Encapsula um UUID e expõe uma fábrica (`generate`) para criação de novos
# identificadores, mantendo a geração de UUID como um detalhe interno do value
# object em vez de espalhada pelo código que cria agentes.
@dataclass(frozen=True, slots=True)
class AgentId:
    value: UUID

    @staticmethod
    def generate() -> AgentId:
        """Cria um novo identificador de agente, aleatório."""
        return AgentId(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


# Bloco: identificador tipado de tarefa.
@dataclass(frozen=True, slots=True)
class TaskId:
    value: UUID

    @staticmethod
    def generate() -> TaskId:
        """Cria um novo identificador de tarefa, aleatório."""
        return TaskId(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


# Bloco: identificador tipado de artefato.
@dataclass(frozen=True, slots=True)
class ArtifactId:
    value: UUID

    @staticmethod
    def generate() -> ArtifactId:
        """Cria um novo identificador de artefato, aleatório."""
        return ArtifactId(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)
