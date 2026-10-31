"""Configuração centralizada do backend, lida a partir de variáveis de ambiente.

Nenhum valor de configuração (URL de banco, host MQTT, URL do Ollama, etc.) pode
ser fixado diretamente no código-fonte — tudo é resolvido a partir de variáveis de
ambiente (arquivo `.env` em desenvolvimento), conforme a premissa inegociável de
"zero hardcode" do projeto. Os valores padrão aqui definidos são apenas um
fallback para desenvolvimento local sem `.env`, nunca credenciais de produção.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.entities.agent import Role
from src.domain.localization.language import Language


# Bloco: definição de todas as configurações do serviço.
# Agrupa num único ponto todas as variáveis de ambiente consumidas pelo backend,
# com tipos explícitos — qualquer variável ausente ou malformada falha de forma
# clara na inicialização do serviço, em vez de causar um erro obscuro em tempo
# de execução mais adiante.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Banco de dados
    database_url: str

    # Backend de persistência: memory | postgres (ADR-014)
    persistence_backend: Literal["memory", "postgres"] = "memory"

    # Barramento MQTT
    mqtt_host: str
    mqtt_port: int

    # Barramento de mensagens: memory | mqtt (ADR-021)
    message_bus_backend: Literal["memory", "mqtt"] = "memory"

    # Autonomia: agentes reagem a objetivos criados (ADR-022)
    autonomy_enabled: bool = False
    work_loop_interval_seconds: float = Field(default=0, ge=0)
    sprint_max_days: int = Field(default=15, ge=1, le=15)
    meeting_rounds: int = Field(default=1, ge=1, le=5)

    # Ollama — sempre externo ao Docker Compose deste projeto (ver ADR-009)
    ollama_base_url: str
    ollama_request_timeout_seconds: float = Field(default=600, gt=0)
    ollama_model: str = "nemotron-3.5-bolt:latest"
    ollama_embedding_model: str = "nomic-embed-text:latest"

    # Idioma do escritório (prompts dos agentes e fallback de erros): pt | en (ADR-012)
    office_language: str = "en"

    # Modelo por papel (Fase 5). Vazio = usa `ollama_model`.
    agent_po_model: str = ""
    agent_sm_model: str = ""
    agent_tech_lead_model: str = ""
    agent_dev_senior_model: str = ""
    agent_dev_junior_model: str = ""
    agent_qa_model: str = ""
    agent_data_model: str = ""
    agent_hr_model: str = ""
    agent_consultant_model: str = ""

    # Busca web (Tavily) — chave pessoal/paga, sem valor padrão de fábrica
    # (ver ADR-011). Ausente por padrão: só é exigida quando a ferramenta
    # `web_search` é efetivamente usada.
    tavily_api_key: str = ""
    tavily_search_url: str = "https://api.tavily.com/search"
    tavily_timeout_seconds: float = 30.0

    # CORS: origens do frontend, separadas por vírgula (ADR-015)
    cors_allowed_origins: str = "http://localhost:5173"

    # HTTP da API do backend
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    def cors_origins(self) -> list[str]:
        """Origens permitidas para CORS (ADR-015), separadas por vírgula, sem vazios."""
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    def language(self) -> Language:
        """Idioma padrão do escritório, normalizado (valor inválido cai em inglês)."""
        return Language.parse(self.office_language)

    def role_models(self) -> dict[Role, str]:
        """Retorna os modelos configurados por papel (apenas os não vazios)."""
        configured = {
            Role.PRODUCT_OWNER: self.agent_po_model,
            Role.SCRUM_MASTER: self.agent_sm_model,
            Role.TECH_LEAD: self.agent_tech_lead_model,
            Role.DEV_SENIOR: self.agent_dev_senior_model,
            Role.DEV_JUNIOR: self.agent_dev_junior_model,
            Role.QA_ENGINEER: self.agent_qa_model,
            Role.DATA_ANALYST: self.agent_data_model,
            Role.HR_MANAGER: self.agent_hr_model,
            Role.PRODUCT_CONSULTANT: self.agent_consultant_model,
        }
        return {role: model for role, model in configured.items() if model}


# Bloco: cache de instância única de configuração.
# Evita reler e revalidar as variáveis de ambiente a cada injeção de dependência.
@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única (singleton por processo) de ``Settings``."""
    # Campos obrigatórios vêm do ambiente (pydantic-settings), não de argumentos.
    return Settings()  # type: ignore[call-arg]
