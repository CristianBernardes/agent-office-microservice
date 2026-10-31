"""Seed do time e do backlog inicial (Rodada 90).

Lê a URL e os modelos por papel do `backend/.env` (nada hardcoded): contrata os
11 agentes e cria as 15 tarefas do comitê. Uso: `python scripts/seed_team.py`.
"""

import json
import os
import urllib.request
from pathlib import Path


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip()
    return values


ENV = load_env(Path(__file__).resolve().parent.parent / "backend" / ".env")
API = os.environ.get("API_URL", f"http://localhost:{os.environ.get('HOST_PORT_BACKEND', '7001')}")


def model_for(env_key: str) -> str:
    return ENV.get(env_key) or ENV["OLLAMA_MODEL"]


def call(path, body):
    req = urllib.request.Request(
        API + path, json.dumps(body).encode(), {"content-type": "application/json"}
    )
    return json.load(urllib.request.urlopen(req))


TEAM = [
    ("Helena", "product_owner", model_for("AGENT_PO_MODEL")),
    ("Marcos", "scrum_master", model_for("AGENT_SM_MODEL")),
    ("Rafael", "tech_lead", model_for("AGENT_TECH_LEAD_MODEL")),
    ("Bruno", "dev_senior", model_for("AGENT_DEV_SENIOR_MODEL")),
    ("Camila", "dev_senior", model_for("AGENT_DEV_SENIOR_MODEL")),
    ("Diego", "dev_junior", model_for("AGENT_DEV_JUNIOR_MODEL")),
    ("Larissa", "dev_junior", model_for("AGENT_DEV_JUNIOR_MODEL")),
    ("Patrícia", "qa_engineer", model_for("AGENT_QA_MODEL")),
    ("Thiago", "data_analyst", model_for("AGENT_DATA_MODEL")),
    ("Fernanda", "hr_manager", model_for("AGENT_HR_MODEL")),
    ("Gustavo", "product_consultant", model_for("AGENT_CONSULTANT_MODEL")),
]
po = None
for name, role, model in TEAM:
    agent = call("/agents", {"name": name, "role": role, "llm_model": model})
    if role == "product_owner":
        po = agent
print("agentes:", len(TEAM))

RULES = (
    "Regras: não inventar pesquisas, fontes, números ou resultados; documentar em docs/ (Markdown); "
    "sem e-books, cursos, infoprodutos, sites institucionais, prompts ou SaaS sem validação."
)
TASKS = [
    ("high", "Investigar dores reais e negligenciadas do mercado brasileiro",
     "Pesquisar problemas recorrentes que geram perda de tempo, dinheiro, oportunidades ou produtividade. Investigar reclamações, comunidades, avaliações negativas e comportamentos reais. Identificar dores com evidências verificáveis, frequência relevante e potencial de pagamento. Proibido inventar necessidades ou usar hipóteses como fatos."),
    ("high", "Identificar oportunidades inéditas e mercados mal atendidos",
     "Investigar soluções existentes no Brasil e no exterior, identificando problemas ainda não resolvidos satisfatoriamente. Priorizar mecanismos originais ou combinações de funcionalidades com diferenciação demonstrável. Não declarar uma ideia inédita sem pesquisa de concorrentes, substitutos e alternativas manuais."),
    ("high", "Investigar por que consumidores pagariam R$ 39,90",
     "Analisar o comportamento de compra do público-alvo, a urgência da dor, o custo atual do problema e alternativas disponíveis. Formular hipóteses de disposição de pagamento e propor testes reais com potenciais compradores. Não confundir interesse declarado com intenção efetiva de compra."),
    ("high", "Gerar 20 propostas de produtos digitais funcionais",
     "Propor 20 soluções digitais diferentes, descrevendo público, problema, mecanismo de solução, diferencial, frequência de uso e motivo para pagar R$ 39,90. Excluir e-books, cursos, infoprodutos, coleções de prompts, sites institucionais, clones de aplicativos e SaaS sem validação. Priorizar ferramentas que entreguem resultados concretos."),
    ("high", "Realizar análise competitiva e eliminar ideias genéricas",
     "Investigar concorrentes diretos, indiretos e soluções substitutas de cada proposta. Comparar preço, recursos, avaliações, reclamações e diferenciais. Eliminar ideias saturadas ou facilmente substituíveis por ferramentas gratuitas, salvo quando houver vantagem relevante comprovável. Documentar fontes, lacunas e grau de confiança."),
    ("high", "Criar matriz científica de priorização das oportunidades",
     "Avaliar cada proposta por intensidade da dor, frequência, diferenciação, evidências de demanda, disposição de pagamento, custo de desenvolvimento, distribuição e risco jurídico. Definir pesos e critérios objetivos, apresentar pontuações justificadas e selecionar as três melhores candidatas. Penalizar dados ausentes e premissas não verificadas. Depende das tarefas 01 a 05."),
    ("medium", "Validar as três melhores ideias com consumidores reais",
     "Planejar entrevistas, demonstrações de protótipos e testes de intenção de compra com pessoas do público-alvo. Definir perguntas neutras, amostra, métricas, critérios de aprovação e reprovação. Não simular entrevistas nem inventar clientes, feedbacks ou resultados. Sem acesso a consumidores, entregar o plano executável e registrar validação pendente."),
    ("medium", "Testar o preço de R$ 39,90 e a viabilidade econômica",
     "Definir experimentos de oferta e compra real para verificar se o público aceita pagar R$ 39,90. Estimar taxas de pagamento, impostos, infraestrutura, suporte, reembolsos e aquisição de clientes. Calcular margem de contribuição e ponto de equilíbrio. A meta de cinco vendas diárias é hipótese comercial, nunca resultado garantido."),
    ("medium", "Definir a proposta vencedora e seus critérios de sucesso",
     "Consolidar evidências das pesquisas e validações para recomendar uma única solução. Documentar problema, público, proposta de valor, mecanismo original, diferenciação, modelo de cobrança, riscos, métricas e hipóteses pendentes. Se nenhuma ideia atingir os critérios mínimos, recomendar novas pesquisas em vez de autorizar o desenvolvimento."),
    ("medium", "Projetar a arquitetura técnica do produto validado",
     "Somente após aprovação da validação, definir arquitetura proporcional ao MVP, componentes, contratos, armazenamento, segurança, privacidade e infraestrutura. Aplicar SOLID, Clean Code, arquitetura limpa e Design Patterns quando justificáveis. Documentar decisões e trade-offs em ADRs. Evitar complexidade e tecnologias desnecessárias."),
    ("medium", "Desenvolver um MVP que resolva a dor de ponta a ponta",
     "Implementar apenas as funcionalidades essenciais para entregar o resultado principal prometido. O produto deve executar uma ação útil, não apenas apresentar informações. Estabelecer critérios de aceite verificáveis, testes automatizados, tratamento de erros, observabilidade básica e documentação. Sem funcionalidades sem vínculo com necessidades validadas."),
    ("medium", "Projetar uma experiência de uso simples e imediata",
     "Criar uma experiência que permita ao comprador compreender o produto e obter o primeiro resultado com o mínimo de etapas. Priorizar clareza, acessibilidade, responsividade e redução de atritos. Validar os fluxos com usuários reais. Evitar cadastros, configurações e telas que não sejam indispensáveis."),
    ("medium", "Executar testes de qualidade, segurança e aceitação",
     "Validar fluxos críticos, resultados produzidos, integridade de dados, falhas previsíveis, segurança e experiência do usuário. Realizar testes unitários, de integração e ponta a ponta conforme o risco. Documentar defeitos e corrigir bloqueantes antes da comercialização. Não declarar o produto pronto apenas porque o código compila."),
    ("low", "Planejar a aquisição das primeiras cinco vendas diárias",
     "Criar estratégia de distribuição para alcançar compradores reais, com canais prioritários, mensagens comerciais, demonstrações e experimentos de conversão. Estimar visitantes necessários conforme taxas de conversão e custos de aquisição. Priorizar canais orgânicos e experimentos baratos antes de publicidade. Não prometer vendas nem criar depoimentos fictícios."),
    ("low", "Planejar lançamento controlado e melhoria contínua",
     "Definir lançamento para um grupo inicial, métricas de ativação, conversão, satisfação, reembolso, suporte e receita líquida. Estabelecer critérios objetivos para continuar, ajustar ou interromper o projeto. Organizar melhorias a partir de dados reais, sem transformar automaticamente o produto em assinatura SaaS."),
]
for priority, title, desc in TASKS:
    call(
        "/tasks",
        {
            "actor_id": po["agent_id"] if "agent_id" in po else po["id"],
            "actor_role": "product_owner",
            "title": title,
            "description": f"{desc}\n\n{RULES}",
            "priority": priority,
        },
    )
print("tarefas:", len(TASKS))
