import type { Language } from "./types";

const STORAGE_KEY = "agent-office:donation-last-shown";
const DAY_MS = 24 * 60 * 60 * 1000;

export type DonationMethod = "pix" | "paypal";

// Bloco: português doa por Pix; inglês por PayPal (se o link estiver configurado, senão Pix).
export function donationMethod(
  language: Language,
  paypalUrl: string,
): DonationMethod {
  return language === "en" && paypalUrl ? "paypal" : "pix";
}

export function shouldShowReminder(
  lastShownIso: string | null,
  now: Date,
  reminderDays: number,
): boolean {
  if (!lastShownIso) return true;
  const last = Date.parse(lastShownIso);
  if (Number.isNaN(last)) return true;
  return now.getTime() - last >= reminderDays * DAY_MS;
}

export function readLastShown(
  storage: Pick<Storage, "getItem"> = localStorage,
): string | null {
  return storage.getItem(STORAGE_KEY);
}

export function markShown(
  now: Date,
  storage: Pick<Storage, "setItem"> = localStorage,
): void {
  storage.setItem(STORAGE_KEY, now.toISOString());
}
