# Fase 4 — Artefatos: Sistema de Geração de Documentos Markdown

> Agentes produzem arquivos `.md` reais, persistidos em disco, versionados e exibidos no frontend em tempo real. Esta fase define o ciclo de vida completo de um artefato.

---

## 🎯 Objetivo

- Implementar o sistema de criação e gestão de artefatos Markdown
- Definir o ciclo de vida: DRAFT → IN_REVIEW → APPROVED → ARCHIVED
- Criar o visualizador de artefatos no frontend
- Garantir que artefatos sejam persistidos em `workspace/projects/{sprint}/`
- Notificar o frontend via MQTT quando artefatos são criados/atualizados

---

## 📁 Estrutura de Artefatos no Disco

```
workspace/
└── projects/
    ├── sprint-1-mvp-autenticacao/
    │   ├── _meta.json                    # Metadados do sprint
    │   ├── backlog.md                    # PO
    │   ├── user-stories.md               # PO
    │   ├── sprint-planning.md            # Scrum Master
    │   ├── adr-001-escolha-de-banco.md   # Tech Lead
    │   ├── adr-002-autenticacao-jwt.md   # Tech Lead
    │   ├── design-doc-auth.md            # Tech Lead
    │   ├── implementacao-login.md        # Dev Sênior
    │   ├── implementacao-registro.md     # Dev Júnior
    │   ├── code-review-login.md          # Dev Sênior
    │   ├── test-plan-auth.md             # QA
    │   ├── bug-report-001-token-expiry.md# QA
    │   ├── analise-conversao.md          # Analista de Dados
    │   ├── kpis-sprint-1.md              # Analista de Dados
    │   ├── onboarding-dev-junior.md      # RH
    │   ├── pesquisa-mercado-auth.md      # Consultor
    │   └── retrospectiva-sprint-1.md     # Scrum Master
    │
    └── sprint-2-dashboard/
        └── ...
```

---

## 📄 Templates de Artefatos

### Backlog (`backlog.md`)

```markdown
# Backlog do Produto — {sprint_name}

**Criado por:** {agent_name} (Product Owner)
**Data:** {date}
**Status:** {status}

---

## 🎯 Visão do Sprint

{vision}

## 📋 Itens do Backlog

### 🔴 Alta Prioridade

| ID | User Story | Critérios de Aceitação | Story Points | Responsável |
|----|-----------|----------------------|-------------|-------------|
| US-001 | Como [persona], quero [ação] para [benefício] | - [ ] Critério 1<br>- [ ] Critério 2 | 5 | Dev Sênior |

### 🟡 Média Prioridade

| ID | User Story | Critérios de Aceitação | Story Points | Responsável |
|----|-----------|----------------------|-------------|-------------|

### 🟢 Baixa Prioridade

| ID | User Story | Critérios de Aceitação | Story Points | Responsável |
|----|-----------|----------------------|-------------|-------------|

---

## 📊 Resumo

- **Total de itens:** {total}
- **Story points totais:** {points}
- **Capacidade do time:** {capacity} pontos/sprint
```

### ADR (`adr-{number}-{title}.md`)

```markdown
# ADR-{number} — {title}

**Status:** Proposto | Aceito | Depreciado | Substituído por ADR-{other}
**Data:** {date}
**Autor:** {agent_name} (Tech Lead)

---

## Contexto

{context}

## Decisão

{decision}

## Consequências

### ✅ Positivas
- {positive_1}
- {positive_2}

### ⚠️ Negativas / Trade-offs
- {negative_1}
- {negative_2}

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|----------------------|
| {alt_1}     | {reason_1}           |
| {alt_2}     | {reason_2}           |
```

### Plano de Testes (`test-plan-{feature}.md`)

```markdown
# Plano de Testes — {feature}

**Criado por:** {agent_name} (QA Engineer)
**Data:** {date}
**Feature:** {feature_name}
**User Story:** {user_story_id}

---

## 🎯 Escopo

{scope}

## ✅ Casos de Teste

### Fluxo Principal (Happy Path)

| ID | Cenário | Pré-condições | Passos | Resultado Esperado | Status |
|----|---------|--------------|--------|-------------------|--------|
| TC-001 | {scenario} | {preconditions} | 1. {step1}<br>2. {step2} | {expected} | ⏳ Pendente |

### Fluxos Alternativos

| ID | Cenário | Resultado Esperado | Status |
|----|---------|-------------------|--------|

### Casos de Borda

| ID | Cenário | Resultado Esperado | Status |
|----|---------|-------------------|--------|

## 🐛 Bugs Encontrados

| ID | Severidade | Descrição | Status |
|----|-----------|-----------|--------|

---

## 📊 Resumo

- **Total de casos:** {total}
- **Passando:** {passing}
- **Falhando:** {failing}
- **Pendentes:** {pending}
```

### Bug Report (`bug-report-{number}-{title}.md`)

```markdown
# Bug Report #{number} — {title}

**Reportado por:** {agent_name} (QA Engineer)
**Data:** {date}
**Severidade:** 🔴 Crítico | 🟠 Alto | 🟡 Médio | 🟢 Baixo
**Status:** Aberto | Em Análise | Corrigido | Fechado

---

## 📋 Descrição

{description}

## 🔄 Passos para Reproduzir

1. {step_1}
2. {step_2}
3. {step_3}

## ✅ Comportamento Esperado

{expected}

## ❌ Comportamento Atual

{actual}

## 🖼️ Evidências

{evidence}

## 🔧 Ambiente

- **Versão:** {version}
- **Navegador/SO:** {environment}

## 💡 Possível Causa

{possible_cause}

---

**Atribuído para:** {assigned_to}
```

---

## 🔄 Ciclo de Vida de um Artefato

```
                    ┌─────────┐
                    │  DRAFT  │ ← Agente cria com write_artifact
                    └────┬────┘
                         │ Agente solicita revisão
                         ▼
                  ┌─────────────┐
                  │  IN_REVIEW  │ ← Tech Lead ou PO revisa
                  └──────┬──────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        ┌──────────┐         ┌─────────────┐
        │ APPROVED │         │  DRAFT      │ ← Volta com comentários
        └────┬─────┘         └─────────────┘
             │
             ▼
        ┌──────────┐
        │ ARCHIVED │ ← Ao final do sprint
        └──────────┘
```

---

## 🐍 Implementação Backend

### WriteArtifactUseCase

```python
# application/artifacts/write_artifact_use_case.py
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime, timezone

from domain.entities.artifact import Artifact, ArtifactType, ArtifactStatus
from domain.interfaces.artifact_repo import IArtifactRepository
from domain.interfaces.message_bus import IMessageBus


@dataclass
class WriteArtifactInput:
    title: str
    content: str
    type: ArtifactType
    path: str
    author_id: UUID
    sprint_id: UUID | None = None


class WriteArtifactUseCase:
    def __init__(
        self,
        artifact_repo: IArtifactRepository,
        message_bus: IMessageBus,
    ):
        self._repo = artifact_repo
        self._bus = message_bus

    async def execute(self, input: WriteArtifactInput) -> Artifact:
        artifact = Artifact(
            id=uuid4(),
            title=input.title,
            content=input.content,
            type=input.type,
            path=input.path,
            author_id=input.author_id,
            sprint_id=input.sprint_id,
            status=ArtifactStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Persiste no banco e no disco
        await self._repo.save(artifact)

        # Notifica via MQTT
        await self._bus.publish(
            topic="office/artifacts/created",
            payload={
                "artifact_id": str(artifact.id),
                "title": artifact.title,
                "type": artifact.type.value,
                "path": artifact.path,
                "status": artifact.status.value,
                "author_id": str(artifact.author_id),
                "sprint_id": str(artifact.sprint_id) if artifact.sprint_id else None,
            },
            qos=1,
        )

        return artifact
```

### MarkdownArtifactWriter (infraestrutura)

```python
# infrastructure/filesystem/markdown_artifact_writer.py
import os
from pathlib import Path

from domain.entities.artifact import Artifact


class MarkdownArtifactWriter:
    def __init__(self, workspace_root: str = "workspace"):
        self._root = Path(workspace_root)

    async def write(self, artifact: Artifact) -> None:
        path = self._root / artifact.path
        path.parent.mkdir(parents=True, exist_ok=True)

        # Adiciona frontmatter YAML
        content = self._add_frontmatter(artifact)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _add_frontmatter(self, artifact: Artifact) -> str:
        frontmatter = f"""---
id: {artifact.id}
title: {artifact.title}
type: {artifact.type.value}
status: {artifact.status.value}
author_id: {artifact.author_id}
sprint_id: {artifact.sprint_id or ""}
created_at: {artifact.created_at.isoformat()}
updated_at: {artifact.updated_at.isoformat()}
---

"""
        return frontmatter + artifact.content
```

---

## ⚛️ Implementação Frontend

### ArtifactViewer.tsx

```tsx
// features/artifacts/ArtifactViewer.tsx
import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useArtifactsStore } from '../../core/store/artifactsStore';
import { ArtifactStatus } from '../../types';

interface Props {
  artifactId: string;
}

export function ArtifactViewer({ artifactId }: Props) {
  const artifact = useArtifactsStore(s => s.artifacts.get(artifactId));

  if (!artifact) return <div>Artefato não encontrado</div>;

  return (
    <div className="artifact-viewer">
      <header className="artifact-header">
        <h2>{artifact.title}</h2>
        <StatusBadge status={artifact.status} />
        <span className="artifact-meta">
          Por {artifact.author_name} • {formatDate(artifact.updated_at)}
        </span>
      </header>

      <div className="artifact-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {artifact.content}
        </ReactMarkdown>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: ArtifactStatus }) {
  const config = {
    draft:     { label: 'Rascunho',   color: 'gray'   },
    in_review: { label: 'Em Revisão', color: 'yellow' },
    approved:  { label: 'Aprovado',   color: 'green'  },
    archived:  { label: 'Arquivado',  color: 'blue'   },
  };

  const { label, color } = config[status];
  return <span className={`badge badge-${color}`}>{label}</span>;
}
```

### ArtifactList.tsx

```tsx
// features/artifacts/ArtifactList.tsx
import React from 'react';
import { useArtifactsStore } from '../../core/store/artifactsStore';
import { ArtifactType } from '../../types';

const TYPE_ICONS: Record<ArtifactType, string> = {
  backlog:         '📋',
  sprint_planning: '🗓️',
  adr:             '📐',
  design_doc:      '🏗️',
  implementation:  '💻',
  test_plan:       '🧪',
  bug_report:      '🐛',
  analysis:        '📊',
  retrospective:   '🔄',
  user_story:      '👤',
  onboarding:      '🤝',
};

export function ArtifactList() {
  const { artifacts, selectedId, selectArtifact } = useArtifactsStore();

  return (
    <div className="artifact-list">
      <h3>📁 Artefatos do Sprint</h3>
      {Array.from(artifacts.values()).map(artifact => (
        <div
          key={artifact.id}
          className={`artifact-item ${selectedId === artifact.id ? 'selected' : ''}`}
          onClick={() => selectArtifact(artifact.id)}
        >
          <span className="artifact-icon">{TYPE_ICONS[artifact.type]}</span>
          <span className="artifact-title">{artifact.title}</span>
          <StatusBadge status={artifact.status} />
        </div>
      ))}
    </div>
  );
}
```

---

## ✅ Checklist da Fase 4

- [ ] `Artifact` entity com todos os campos
- [ ] `ArtifactType` enum com todos os tipos
- [ ] `ArtifactStatus` enum (DRAFT, IN_REVIEW, APPROVED, ARCHIVED)
- [ ] `IArtifactRepository` interface
- [ ] `WriteArtifactUseCase` implementado
- [ ] `ReviewArtifactUseCase` implementado
- [ ] `ApproveArtifactUseCase` implementado
- [ ] `MarkdownArtifactWriter` (escreve em disco com frontmatter)
- [ ] `PostgresArtifactRepository` (persiste metadados no banco)
- [ ] Templates Markdown para cada tipo de artefato
- [ ] MQTT: publicar `office/artifacts/created` e `office/artifacts/updated`
- [ ] Frontend: `ArtifactViewer` com renderização Markdown
- [ ] Frontend: `ArtifactList` com ícones por tipo
- [ ] Frontend: `artifactsStore` Zustand sincronizado via MQTT
- [ ] Testes unitários: `WriteArtifactUseCase`
- [ ] Testes de integração: agente cria artefato → aparece no frontend
