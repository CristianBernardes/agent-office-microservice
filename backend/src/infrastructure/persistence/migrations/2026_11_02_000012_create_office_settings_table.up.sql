-- Configurações do escritório (chave/valor), ex.: bloqueio de criação de tarefas pelos agentes.
CREATE TABLE office_settings (
    key   TEXT PRIMARY KEY,
    value JSONB NOT NULL
);
INSERT INTO office_settings (key, value) VALUES ('agents_can_create_tasks', 'true'::jsonb);
