import { fireEvent, render, screen, waitFor } from "@testing-library/svelte";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ChatPanel from "./ChatPanel.svelte";
import DismissalModal from "./DismissalModal.svelte";
import DonationModal from "./DonationModal.svelte";
import TaskEditModal from "./TaskEditModal.svelte";
import HireForm from "./HireForm.svelte";
import GoalForm from "./GoalForm.svelte";
import KanbanBoard from "./KanbanBoard.svelte";
import LanguageSwitcher from "./LanguageSwitcher.svelte";
import TaskForm from "./TaskForm.svelte";
import TeamBoard from "./TeamBoard.svelte";
import { i18n } from "../lib/i18n.svelte";
import type { Agent, ChatMessage, DismissalProposal, Task } from "../lib/types";

const agent: Agent = {
  agent_id: "a1",
  name: "Ana",
  role: "dev_senior",
  status: "working",
  model: "m",
} as unknown as Agent;
const task: Task = {
  task_id: "t1",
  title: "Implementar API",
  status: "in_progress",
  priority: "high",
  assigned_to: "a1",
} as unknown as Task;

beforeEach(() => i18n.set("pt"));

describe("componentes", () => {
  it("LanguageSwitcher troca o idioma", async () => {
    const onchange = vi.fn();
    render(LanguageSwitcher, { onchange });
    await fireEvent.click(screen.getByRole("button", { name: "EN" }));
    expect(screen.getByRole("alertdialog")).toBeTruthy();
    expect(i18n.language).toBe("pt");
    await fireEvent.click(
      screen.getByRole("button", { name: "Trocar idioma" }),
    );
    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect(i18n.language).toBe("en");
    expect(onchange).toHaveBeenCalledWith("en");
  });

  it("LanguageSwitcher não troca se o aviso for recusado", async () => {
    i18n.set("pt");
    const onchange = vi.fn();
    render(LanguageSwitcher, { onchange });
    await fireEvent.click(screen.getByRole("button", { name: "EN" }));
    await fireEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect(i18n.language).toBe("pt");
    expect(onchange).not.toHaveBeenCalled();
  });

  it("GoalForm envia o texto e limpa o campo", async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined);
    render(GoalForm, { onsubmit });
    const box = screen.getByRole("textbox");
    await fireEvent.input(box, { target: { value: "Criar produto X" } });
    await fireEvent.submit(box.closest("form")!);
    expect(onsubmit).toHaveBeenCalledWith("Criar produto X");
  });

  it("TaskForm envia título, descrição e prioridade", async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined);
    render(TaskForm, { hasAgents: true, onsubmit });
    await fireEvent.input(screen.getByLabelText("Título"), {
      target: { value: "Produto X" },
    });
    await fireEvent.submit(screen.getByRole("button").closest("form")!);
    expect(onsubmit).toHaveBeenCalledWith("Produto X", "", "medium");
  });

  it("TaskForm bloqueia sem agentes", () => {
    render(TaskForm, { hasAgents: false, onsubmit: vi.fn() });
    expect(screen.getByRole("button")).toHaveProperty("disabled", true);
  });

  it("KanbanBoard move a task usando o responsável como ator", async () => {
    const onmove = vi.fn().mockResolvedValue(undefined);
    render(KanbanBoard, { tasks: [task], agents: [agent], onmove });
    await fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "done" },
    });
    expect(onmove).toHaveBeenCalledWith(task, "done", agent);
  });

  it("KanbanBoard mostra cargo do responsável, contagem e alerta de WIP", () => {
    const t2 = {
      ...task,
      status: "in_progress" as const,
      assigned_to: agent.agent_id,
    };
    render(KanbanBoard, {
      tasks: [t2, { ...t2, task_id: "x2" }],
      agents: [agent],
      onmove: vi.fn(),
      wipLimits: { in_progress: 1 },
    });
    expect(screen.getByTestId("count-in_progress").textContent).toBe("2/1");
    expect(document.body.textContent).toContain(
      `Ana· ${i18n.t.roles.dev_senior}`,
    );
    expect(screen.getByTestId("flow-metrics")).toBeTruthy();
  });

  it("TeamBoard mostra quem está com qual task", () => {
    render(TeamBoard, {
      agents: [agent],
      tasks: [task],
      selectedId: null,
      onselect: vi.fn(),
    });
    expect(screen.getByText("Ana")).toBeTruthy();
    expect(screen.getByTestId("assigned-task").textContent).toContain(
      "Implementar API",
    );
  });

  it("ChatPanel mostra remetente e conteúdo", () => {
    const message = {
      message_id: "m1",
      sender_id: "a1",
      recipient_id: null,
      kind: "decision",
      content: "Usaremos FastAPI",
    } as unknown as ChatMessage;
    render(ChatPanel, { messages: [message], agents: [agent] });
    expect(screen.getByText("Usaremos FastAPI")).toBeTruthy();
    expect(screen.getByText("Ana")).toBeTruthy();
  });

  it("DonationModal usa Pix em pt e PayPal em en", async () => {
    const view = render(DonationModal, {
      paypalUrl: "https://paypal.me/x",
      pixLabel: "Pix",
      onclose: vi.fn(),
    });
    expect(screen.getByRole("img")).toBeTruthy();
    expect(screen.getByRole("link")).toHaveProperty(
      "href",
      "https://paypal.me/x",
    );
    i18n.set("en");
    view.rerender({
      paypalUrl: "https://paypal.me/x",
      pixLabel: "Pix",
      onclose: vi.fn(),
    });
    expect(await screen.findByRole("link")).toHaveProperty(
      "href",
      "https://paypal.me/x",
    );
  });

  it("HireForm envia nome, cargo e modelo", async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined);
    render(HireForm, { defaultModel: "qwen", onsubmit });
    await fireEvent.input(screen.getByLabelText("Nome"), {
      target: { value: "Ana" },
    });
    await fireEvent.change(screen.getByLabelText("Cargo"), {
      target: { value: "tech_lead" },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Contratar" }));
    expect(onsubmit).toHaveBeenCalledWith({
      name: "Ana",
      role: "tech_lead",
      llm_model: "qwen",
    });
  });

  it("HireForm oferece seleção quando há modelos disponíveis", async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined);
    render(HireForm, {
      defaultModel: "qwen",
      models: ["llama", "qwen"],
      onsubmit,
    });
    await fireEvent.input(screen.getByLabelText("Nome"), {
      target: { value: "Ana" },
    });
    await fireEvent.change(screen.getByLabelText("Modelo (Ollama)"), {
      target: { value: "llama" },
    });
    await fireEvent.click(screen.getByRole("button", { name: "Contratar" }));
    expect(onsubmit).toHaveBeenCalledWith({
      name: "Ana",
      role: "dev_senior",
      llm_model: "llama",
    });
  });

  it("HireForm contrata o time padrão", async () => {
    const onsubmit = vi.fn().mockResolvedValue(undefined);
    render(HireForm, { defaultModel: "qwen", onsubmit });
    await fireEvent.click(
      screen.getByRole("button", { name: "Contratar time padrão" }),
    );
    await waitFor(() => expect(onsubmit).toHaveBeenCalledTimes(6));
  });
});

describe("poderes do dono do produto e demissões", () => {
  it("TeamBoard demite só depois da confirmação", async () => {
    const onfire = vi.fn().mockResolvedValue(undefined);
    render(TeamBoard, {
      agents: [agent],
      tasks: [],
      selectedId: null,
      onselect: vi.fn(),
      onfire,
    });
    await fireEvent.click(screen.getByRole("button", { name: /Demitir: Ana/ }));
    expect(onfire).not.toHaveBeenCalled();
    await fireEvent.click(screen.getByRole("button", { name: "Demitir" }));
    await waitFor(() => expect(onfire).toHaveBeenCalledWith(agent));
  });

  it("TeamBoard cancela a demissão", async () => {
    const onfire = vi.fn();
    render(TeamBoard, {
      agents: [agent],
      tasks: [],
      selectedId: null,
      onselect: vi.fn(),
      onfire,
    });
    await fireEvent.click(screen.getByRole("button", { name: /Demitir: Ana/ }));
    await fireEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(onfire).not.toHaveBeenCalled();
  });

  it("KanbanBoard move o cartão ao soltá-lo em outra coluna", async () => {
    const onmove = vi.fn().mockResolvedValue(undefined);
    render(KanbanBoard, { tasks: [task], agents: [agent], onmove });
    const data = new Map<string, string>();
    const dataTransfer = {
      setData: (k: string, v: string) => data.set(k, v),
      getData: (k: string) => data.get(k) ?? "",
      effectAllowed: "",
    };
    await fireEvent.dragStart(
      screen.getByText("Implementar API").closest("article")!,
      {
        dataTransfer,
      },
    );
    await fireEvent.drop(screen.getByTestId("column-done"), { dataTransfer });
    expect(onmove).toHaveBeenCalledWith(task, "done", agent);
  });

  it("KanbanBoard usa o PO como ator quando o responsável foi demitido", async () => {
    const onmove = vi.fn().mockResolvedValue(undefined);
    const po = { ...agent, agent_id: "po", role: "product_owner" } as Agent;
    const fired = { ...agent, status: "offline" } as Agent;
    render(KanbanBoard, { tasks: [task], agents: [fired, po], onmove });
    await fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "done" },
    });
    expect(onmove).toHaveBeenCalledWith(task, "done", po);
  });

  it("KanbanBoard ordena por prioridade dentro da coluna", () => {
    const low = {
      ...task,
      task_id: "l",
      title: "Baixa",
      priority: "low",
    } as Task;
    const urgent = {
      ...task,
      task_id: "u",
      title: "Urgente!",
      priority: "urgent",
    } as Task;
    render(KanbanBoard, {
      tasks: [low, urgent],
      agents: [agent],
      onmove: vi.fn(),
    });
    const titles = screen
      .getAllByRole("article")
      .map((card) => card.querySelector("strong")?.textContent);
    expect(titles).toEqual(["Urgente!", "Baixa"]);
  });

  it("TaskEditModal envia só o que mudou (responsável e prioridade)", async () => {
    const onsave = vi.fn().mockResolvedValue(undefined);
    const onclose = vi.fn();
    const other = { ...agent, agent_id: "a2", name: "Bia" } as Agent;
    render(TaskEditModal, { task, agents: [agent, other], onsave, onclose });
    const [owner, priority] = screen.getAllByRole("combobox");
    await fireEvent.change(owner, { target: { value: "a2" } });
    await fireEvent.change(priority, { target: { value: "urgent" } });
    await fireEvent.click(screen.getByRole("button", { name: "Salvar" }));
    await waitFor(() =>
      expect(onsave).toHaveBeenCalledWith(task, {
        owner: "a2",
        priority: "urgent",
      }),
    );
    expect(onclose).toHaveBeenCalled();
  });

  it("TaskEditModal não chama a API sem mudanças", async () => {
    const onsave = vi.fn();
    const onclose = vi.fn();
    render(TaskEditModal, { task, agents: [agent], onsave, onclose });
    await fireEvent.click(screen.getByRole("button", { name: "Salvar" }));
    expect(onsave).not.toHaveBeenCalled();
    expect(onclose).toHaveBeenCalled();
  });

  it("ChatPanel deixa o cliente responder ao time", async () => {
    const onsend = vi.fn().mockResolvedValue(undefined);
    render(ChatPanel, { messages: [], agents: [agent], canSend: true, onsend });
    const box = screen.getByRole("textbox");
    await fireEvent.input(box, { target: { value: "Foque no Pix" } });
    await fireEvent.click(screen.getByRole("button", { name: "Enviar" }));
    await waitFor(() => expect(onsend).toHaveBeenCalledWith("Foque no Pix"));
    expect((box as HTMLInputElement).value).toBe("");
  });

  it("ChatPanel bloqueia o envio sem objetivo aberto", () => {
    render(ChatPanel, {
      messages: [],
      agents: [agent],
      canSend: false,
      onsend: vi.fn(),
    });
    expect(screen.getByRole("textbox")).toHaveProperty("disabled", true);
  });

  const proposal: DismissalProposal = {
    proposal_id: "p1",
    agent_id: "a1",
    proposed_by: "hr",
    reason: "Entregas atrasadas",
    status: "pending",
    created_at: "2026-01-01T00:00:00Z",
    decided_at: null,
  };
  const hr = {
    ...agent,
    agent_id: "hr",
    name: "Rita",
    role: "hr_manager",
  } as Agent;

  it("DismissalModal mostra o motivo do RH e aprova", async () => {
    const ondecide = vi.fn().mockResolvedValue(undefined);
    render(DismissalModal, {
      props: { proposal, target: agent, proposer: hr, ondecide },
    });
    expect(screen.getByRole("alertdialog")).toBeTruthy();
    expect(document.body.textContent).toContain("Rita propõe demitir Ana");
    expect(screen.getByTestId("dismissal-reason").textContent).toBe(
      "Entregas atrasadas",
    );
    await fireEvent.click(
      screen.getByRole("button", { name: "Aprovar demissão" }),
    );
    await waitFor(() => expect(ondecide).toHaveBeenCalledWith(proposal, true));
  });

  it("DismissalModal rejeita e fala inglês quando o idioma é en", async () => {
    i18n.set("en");
    const ondecide = vi.fn().mockResolvedValue(undefined);
    render(DismissalModal, {
      props: { proposal, target: agent, proposer: hr, ondecide },
    });
    expect(document.body.textContent).toContain("Rita proposes dismissing Ana");
    await fireEvent.click(
      screen.getByRole("button", { name: "Keep on the team" }),
    );
    await waitFor(() => expect(ondecide).toHaveBeenCalledWith(proposal, false));
  });

  it("DismissalModal não fecha no Esc e avisa quando a decisão falha", async () => {
    const ondecide = vi.fn().mockRejectedValue(new Error("x"));
    render(DismissalModal, {
      props: { proposal, target: agent, proposer: hr, ondecide },
    });
    await fireEvent.keyDown(window, { key: "Escape" });
    expect(screen.getByRole("alertdialog")).toBeTruthy();
    await fireEvent.click(
      screen.getByRole("button", { name: "Aprovar demissão" }),
    );
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
  });
});
