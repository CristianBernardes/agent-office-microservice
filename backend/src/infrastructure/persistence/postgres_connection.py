"""Gerenciamento da pool de conexões assíncronas com o PostgreSQL.

Centraliza a criação e o encerramento da pool do ``asyncpg``, para que a camada de
apresentação (bootstrap do FastAPI) controle o ciclo de vida da conexão sem que
repositórios individuais precisem se preocupar em abrir/fechar conexões.
"""

from __future__ import annotations

import asyncpg


# Bloco: fábrica de pool de conexões PostgreSQL.
# Mantida como uma função simples (não uma classe com estado global) para deixar
# explícito, em cada ponto de uso, de onde a pool vem — reforçando a injeção de
# dependência em vez de um singleton implícito escondido no módulo.
async def create_postgres_pool(database_url: str) -> asyncpg.Pool:
    """Cria e retorna uma pool de conexões assíncronas com o PostgreSQL."""
    return await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=10)
