import { describe, expect, it } from "vitest";
import { MAP_WIDTH, placeAgents } from "./layout";
import type { Agent } from "./types";

const agent = (id: string, role: Agent["role"]): Agent => ({
  agent_id: id,
  name: id,
  role,
  status: "idle",
  llm_model: "m",
});

describe("placeAgents", () => {
  it("posiciona em porcentagem do mapa", () => {
    const [p] = placeAgents([agent("a", "dev_senior")]);
    expect(p.left).toBeCloseTo((570 / MAP_WIDTH) * 100);
    expect(p.top).toBeGreaterThan(0);
  });

  it("desloca agentes repetidos do mesmo papel", () => {
    const [first, second] = placeAgents([
      agent("a", "qa_engineer"),
      agent("b", "qa_engineer"),
    ]);
    expect(second.left).toBeGreaterThan(first.left);
    expect(second.top).toBe(first.top);
  });
});

import { hueFor, meetingPoint, pickBreak, pickMeeting } from "./layout";

describe("vida no escritório", () => {
  const mk = (id: string, status = "idle") =>
    ({ agent_id: id, status }) as never;
  it("hue difere por variante e é determinístico", () => {
    expect(hueFor(0)).toBe(0);
    expect(hueFor(1)).not.toBe(hueFor(2));
    expect(hueFor(1)).toBe(hueFor(1));
  });
  it("pickMeeting exige dois agentes livres", () => {
    expect(pickMeeting([mk("a")], new Set(), () => 0)).toBeNull();
    expect(
      pickMeeting([mk("a"), mk("b", "offline")], new Set(), () => 0),
    ).toBeNull();
    expect(pickMeeting([mk("a"), mk("b")], new Set(["b"]), () => 0)).toBeNull();
    expect(pickMeeting([mk("a"), mk("b")], new Set(), () => 0)).toEqual({
      walker: "a",
      target: "b",
    });
  });
  it("meetingPoint fica ao lado do colega", () => {
    expect(meetingPoint(10, 20).left).toBeGreaterThan(10);
    expect(meetingPoint(10, 20).top).toBe(20);
  });
});

describe("pickBreak", () => {
  const mk = (id: string) => ({ agent_id: id, status: "idle" }) as never;
  it("sorteia uma pausa de descanso ou reflexão para um agente livre", () => {
    expect(pickBreak([mk("a")], new Set(), 4, () => 0)).toEqual({
      agentId: "a",
      kind: "rest",
      index: 0,
    });
    expect(pickBreak([mk("a")], new Set(), 4, () => 0.9)).toEqual({
      agentId: "a",
      kind: "think",
      index: 3,
    });
  });
  it("ignora agentes ocupados e sem frases", () => {
    expect(pickBreak([mk("a")], new Set(["a"]), 4, () => 0)).toBeNull();
    expect(pickBreak([mk("a")], new Set(), 0, () => 0)).toBeNull();
  });
});

describe("directionBetween", () => {
  it("usa o eixo dominante", async () => {
    const { directionBetween } = await import("./layout");
    expect(directionBetween({ left: 0, top: 0 }, { left: 10, top: 2 })).toBe(
      "right",
    );
    expect(directionBetween({ left: 10, top: 0 }, { left: 0, top: 2 })).toBe(
      "left",
    );
    expect(directionBetween({ left: 0, top: 0 }, { left: 1, top: 9 })).toBe(
      "down",
    );
    expect(directionBetween({ left: 0, top: 9 }, { left: 1, top: 0 })).toBe(
      "up",
    );
  });
});
