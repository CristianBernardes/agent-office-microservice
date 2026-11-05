DELETE FROM agents WHERE role NOT IN (
    'product_owner', 'scrum_master', 'tech_lead', 'dev_senior', 'dev_junior',
    'qa_engineer', 'data_analyst', 'hr_manager', 'product_consultant');
ALTER DOMAIN agent_role DROP CONSTRAINT agent_role_check;
ALTER DOMAIN agent_role ADD CONSTRAINT agent_role_check CHECK (VALUE IN (
    'product_owner', 'scrum_master', 'tech_lead', 'dev_senior', 'dev_junior',
    'qa_engineer', 'data_analyst', 'hr_manager', 'product_consultant'));
