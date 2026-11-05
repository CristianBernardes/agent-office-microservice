-- Amplia o domínio agent_role com novos cargos especializados.
ALTER DOMAIN agent_role DROP CONSTRAINT agent_role_check;
ALTER DOMAIN agent_role ADD CONSTRAINT agent_role_check CHECK (VALUE IN (
    'product_owner', 'scrum_master', 'tech_lead', 'dev_senior', 'dev_junior',
    'qa_engineer', 'data_analyst', 'hr_manager', 'product_consultant',
    'dev_mid', 'database_administrator', 'devops_engineer', 'site_reliability_engineer',
    'ux_ui_designer', 'business_analyst', 'software_architect', 'security_engineer',
    'test_automation_engineer', 'data_engineer', 'ai_engineer', 'ml_engineer',
    'systems_analyst', 'product_designer', 'technical_support', 'infrastructure_analyst',
    'data_quality_analyst', 'engineering_manager'));
