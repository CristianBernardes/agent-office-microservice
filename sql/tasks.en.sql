-- Initial backlog (15 tasks) in English. created_by NULL = created by the user.
-- Usage: psql "$DATABASE_URL" -f sql/tasks.en.sql  (see sql/README.md)

BEGIN;

INSERT INTO tasks (task_id, title, description, status, priority, position)
VALUES
    (gen_random_uuid(), 'Investigate real, overlooked pain points in the Brazilian market',
     'Research recurring problems that waste time, money, opportunities or productivity. Investigate complaints, communities, negative reviews and real behavior. Identify pains with verifiable evidence, relevant frequency and willingness to pay. Inventing needs or treating hypotheses as facts is forbidden.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'high', 0),
    (gen_random_uuid(), 'Identify novel opportunities and underserved markets',
     'Investigate existing solutions in Brazil and abroad, identifying problems not yet satisfactorily solved. Prioritize original mechanisms or feature combinations with demonstrable differentiation. Do not call an idea novel without researching competitors, substitutes and manual alternatives.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'high', 1),
    (gen_random_uuid(), 'Investigate why consumers would pay R$ 39.90',
     'Analyze the target audience''s buying behavior, the urgency of the pain, the current cost of the problem and available alternatives. Formulate willingness-to-pay hypotheses and propose real tests with potential buyers. Do not confuse stated interest with actual purchase intent.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'high', 2),
    (gen_random_uuid(), 'Generate 20 functional digital product proposals',
     'Propose 20 different digital solutions, describing audience, problem, solution mechanism, differentiator, frequency of use and the reason to pay R$ 39.90. Exclude e-books, courses, info-products, prompt collections, corporate websites, app clones and unvalidated SaaS. Prioritize tools that deliver concrete results.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'high', 3),
    (gen_random_uuid(), 'Run a competitive analysis and eliminate generic ideas',
     'Investigate direct and indirect competitors and substitutes for each proposal. Compare price, features, reviews, complaints and differentiators. Eliminate saturated ideas or ideas easily replaced by free tools, unless a provable relevant advantage exists. Document sources, gaps and confidence level.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'high', 4),
    (gen_random_uuid(), 'Build a scientific prioritization matrix for the opportunities',
     'Score each proposal by pain intensity, frequency, differentiation, demand evidence, willingness to pay, development cost, distribution and legal risk. Define weights and objective criteria, present justified scores and select the three best candidates. Penalize missing data and unverified assumptions. Depends on tasks 01 to 05.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'high', 5),
    (gen_random_uuid(), 'Validate the three best ideas with real consumers',
     'Plan interviews, prototype demos and purchase-intent tests with people from the target audience. Define neutral questions, sample size, metrics, and pass/fail criteria. Do not simulate interviews or invent customers, feedback or results. Without access to consumers, deliver the executable plan and record validation as pending.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'medium', 6),
    (gen_random_uuid(), 'Test the R$ 39.90 price and economic viability',
     'Define offer and real-purchase experiments to check whether the audience accepts paying R$ 39.90. Estimate payment fees, taxes, infrastructure, support, refunds and customer acquisition. Compute contribution margin and break-even point. The goal of five sales per day is a commercial hypothesis, never a guaranteed result.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'medium', 7),
    (gen_random_uuid(), 'Define the winning proposal and its success criteria',
     'Consolidate research and validation evidence to recommend a single solution. Document problem, audience, value proposition, original mechanism, differentiation, pricing model, risks, metrics and pending hypotheses. If no idea meets the minimum criteria, recommend further research instead of authorizing development.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'medium', 8),
    (gen_random_uuid(), 'Design the technical architecture of the validated product',
     'Only after validation is approved, define an architecture proportional to the MVP, components, contracts, storage, security, privacy and infrastructure. Apply SOLID, Clean Code, clean architecture and Design Patterns where justified. Record decisions and trade-offs in ADRs. Avoid unnecessary complexity and technologies.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'medium', 9),
    (gen_random_uuid(), 'Build an MVP that solves the pain end to end',
     'Implement only the essential features needed to deliver the main promised result. The product must perform a useful action, not just display information. Establish verifiable acceptance criteria, automated tests, error handling, basic observability and documentation. No features unrelated to validated needs.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'medium', 10),
    (gen_random_uuid(), 'Design a simple, immediate user experience',
     'Create an experience that lets the buyer understand the product and get a first result in as few steps as possible. Prioritize clarity, accessibility, responsiveness and friction reduction. Validate the flows with real users. Avoid sign-ups, settings and screens that are not indispensable.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'medium', 11),
    (gen_random_uuid(), 'Run quality, security and acceptance tests',
     'Validate critical flows, produced results, data integrity, foreseeable failures, security and user experience. Run unit, integration and end-to-end tests according to risk. Document defects and fix blockers before commercialization. Do not declare the product ready just because the code compiles.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'medium', 12),
    (gen_random_uuid(), 'Plan acquisition of the first five daily sales',
     'Create a distribution strategy to reach real buyers, with priority channels, sales messaging, demos and conversion experiments. Estimate the visitors needed given conversion rates and acquisition costs. Prioritize organic channels and cheap experiments before advertising. Do not promise sales or create fictitious testimonials.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'low', 13),
    (gen_random_uuid(), 'Plan a controlled launch and continuous improvement',
     'Define a launch to an initial group, with activation, conversion, satisfaction, refund, support and net revenue metrics. Set objective criteria to continue, adjust or stop the project. Organize improvements from real data, without automatically turning the product into a SaaS subscription.

Rules: do not invent research, sources, numbers or results; document in docs/ (Markdown); no e-books, courses, info-products, corporate websites, prompts or unvalidated SaaS.',
     'backlog', 'low', 14);

COMMIT;
