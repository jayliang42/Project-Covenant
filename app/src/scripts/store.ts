// Local-only learning state. Nothing leaves the device; there are no accounts.
// The same key is read by the inline boot script in AppLayout.astro.

export const KEY = 'covenant-learn:v1';

export type LangMode = 'zh' | 'en' | 'both';
export interface State {
  v: 1;
  track?: string;
  /** lessonId -> ISO date completed */
  completed: Record<string, string>;
  /** last opened lesson id */
  last?: string;
  /** distinct local dates (YYYY-MM-DD) with any completed lesson */
  days: string[];
  settings: { lang: LangMode; theme: 'system' | 'light' | 'dark'; size: 'm' | 'l' | 'xl' };
}

const fresh = (): State => ({ v: 1, completed: {}, days: [], settings: { lang: 'zh', theme: 'system', size: 'm' } });

export function load(): State {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (raw && raw.v === 1) return { ...fresh(), ...raw, settings: { ...fresh().settings, ...raw.settings } };
  } catch {
    /* storage unavailable or corrupted: start fresh */
  }
  return fresh();
}

let state = load();
const listeners = new Set<(s: State) => void>();

export const get = () => state;
export function update(fn: (s: State) => void) {
  fn(state);
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* private mode etc.: keep working in memory */
  }
  listeners.forEach((l) => l(state));
}
/** Re-read after another tab changed storage (no write back, so tabs never ping-pong). */
export function refresh() {
  state = load();
  listeners.forEach((l) => l(state));
}
export const subscribe = (fn: (s: State) => void) => (listeners.add(fn), () => listeners.delete(fn));

export const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

export function setComplete(id: string, done: boolean) {
  update((s) => {
    if (done) {
      s.completed[id] = new Date().toISOString();
      const t = today();
      if (!s.days.includes(t)) s.days = [...s.days, t].slice(-400);
    } else delete s.completed[id];
  });
}

/** Days studied in the current week (Mon–Sun). Gentle stat; no streak pressure. */
export function daysThisWeek(s = state) {
  const now = new Date();
  const monday = new Date(now);
  monday.setHours(0, 0, 0, 0);
  monday.setDate(now.getDate() - ((now.getDay() + 6) % 7));
  return s.days.filter((d) => new Date(`${d}T00:00:00`) >= monday).length;
}

export function exportJson() {
  return JSON.stringify(state, null, 2);
}
export function importJson(text: string) {
  const data = JSON.parse(text);
  if (!data || data.v !== 1 || typeof data.completed !== 'object') throw new Error('not a Covenant Learn backup');
  update((s) => Object.assign(s, fresh(), data, { settings: { ...fresh().settings, ...data.settings } }));
}
export function reset() {
  update((s) => Object.assign(s, fresh(), { settings: s.settings }));
}
