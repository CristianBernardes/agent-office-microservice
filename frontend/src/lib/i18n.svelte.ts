import { dictionaries, type Messages } from "./messages";
import type { Language } from "./types";

const STORAGE_KEY = "agent-office:language";

function isLanguage(value: unknown): value is Language {
  return value === "pt" || value === "en";
}

// Bloco: idioma salvo no navegador vence o padrão da configuração.
export function resolveInitialLanguage(
  fallback: Language,
  storage: Pick<Storage, "getItem">,
): Language {
  const saved = storage.getItem(STORAGE_KEY);
  return isLanguage(saved) ? saved : fallback;
}

class I18n {
  language = $state<Language>("pt");

  init(fallback: Language, storage: Pick<Storage, "getItem"> = localStorage) {
    this.language = resolveInitialLanguage(fallback, storage);
  }

  get t(): Messages {
    return dictionaries[this.language];
  }

  set(language: Language, storage: Pick<Storage, "setItem"> = localStorage) {
    this.language = language;
    storage.setItem(STORAGE_KEY, language);
  }
}

export const i18n = new I18n();
