import os

# Bloco: Settings exige infraestrutura via ambiente (ADR-044); os testes fornecem valores locais.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("MQTT_HOST", "localhost")
os.environ.setdefault("MQTT_PORT", "1883")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
