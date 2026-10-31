import { beforeEach, describe, expect, it } from "vitest";
import { dictionaries } from "./messages";
import { i18n, resolveInitialLanguage } from "./i18n.svelte";

describe("i18n", () => {
  beforeEach(() => localStorage.clear());

  it("pt e en têm exatamente as mesmas chaves", () => {
    const keys = (o: object): string[] =>
      Object.entries(o).flatMap(([k, v]) =>
        typeof v === "object" ? keys(v).map((s) => `${k}.${s}`) : [k],
      );
    expect(keys(dictionaries.en).sort()).toEqual(keys(dictionaries.pt).sort());
  });

  it("usa o padrão quando nada foi salvo e o salvo quando existe", () => {
    expect(resolveInitialLanguage("en", localStorage)).toBe("en");
    localStorage.setItem("agent-office:language", "pt");
    expect(resolveInitialLanguage("en", localStorage)).toBe("pt");
    localStorage.setItem("agent-office:language", "xx");
    expect(resolveInitialLanguage("en", localStorage)).toBe("en");
  });

  it("troca o idioma e persiste a preferência", () => {
    i18n.init("pt");
    expect(i18n.t.appTitle).toBe("Escritório de Agentes");
    i18n.set("en");
    expect(i18n.t.appTitle).toBe("Agent Office");
    expect(localStorage.getItem("agent-office:language")).toBe("en");
  });
});
