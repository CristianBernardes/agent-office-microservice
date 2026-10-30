"""Configuração centralizada do backend, lida a partir de variáveis de ambiente.

Nenhum valor de configuração (URL de banco, host MQTT, URL do Ollama, etc.) pode
ser fixado diretamente no código-fonte — tudo é resolvido a partir de variáveis de
ambiente (arquivo `.env` em desenvolvimento), conforme a premissa inegociável de
"zero hardcode" do projeto. Os valores padrão aqui definidos são apenas um
fallback para desenvolvimento local sem `.env`, nunca credenciais de produção.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# Bloco: definição de todas as configurações do serviço.
# Agrupa num único ponto todas as variáveis de ambiente consumidas pelo backend,
# com tipos explícitos — qualquer variável ausente ou malformada falha de forma
# clara na inicialização do serviço, em vez de causar um erro obscuro em tempo
# de execução mais adiante.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Banco de dados
    database_url: str = "postgresql://agm:agm@localhost:7034/agm"

    # Barramento MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 7083

    # Ollama — sempre externo ao Docker Compose deste projeto (ver ADR-009)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "nemotron-3.5-bolt:latest"
    ollama_embedding_model: str = "nomic-embed-text:latest"

    # HTTP da API do backend
    api_host: str = "0.0.0.0"
    api_port: int = 8000


# Bloco: cache de instância única de configuração.
# Evita reler e revalidar as variáveis de ambiente a cada injeção de dependência.
@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única (singleton por processo) de ``Settings``."""
    return Settings()
