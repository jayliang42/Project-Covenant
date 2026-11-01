// Progressive enhancement for every page. Pages are fully readable without it;
// this adds language switching, local progress, quizzes and settings.
import * as store from './store';
import type { LangMode, State } from './store';

type Text = { zh: string; en?: string };
interface LessonInfo { id: string; title: Text; unit: string; minutes: number; url: string }
interface TrackInfo { id: string; color: string; title: Text; url: string; lessons: LessonInfo[]; units: { id: string; title: Text; lessons: string[] }[] }

const data: { tracks: TrackInfo[] } = JSON.parse(document.getElementById('app-data')?.textContent || '{"tracks":[]}');
const $$ = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document) => Array.from(root.querySelectorAll<T & Element>(sel)) as T[];
const esc = (s = '') => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]!);
const ui = (zh: string, en: string) => `<span data-ui="zh">${esc(zh)}</span><span data-ui="en">${esc(en)}</span>`;
const bi = (t: Text) =>
  t.en ? `<span data-lang="zh" class="bi-zh">${esc(t.zh)}</span><span data-lang="en" class="bi-en">${esc(t.en)}</span>` : `<span data-lang="both">${esc(t.zh)}</span>`;
const trackById = (id?: string) => data.tracks.find((t) => t.id === id);
const doneIn = (t: TrackInfo, s: State) => t.lessons.filter((l) => s.completed[l.id]).length;
const nextIn = (t: TrackInfo, s: State) => t.lessons.find((l) => !s.completed[l.id]);

// ---------- toast ----------
let toastTimer: number | undefined;
function toast(zh: string, en: string) {
  const el = document.querySelector<HTMLElement>('[data-toast]');
  if (!el) return;
  el.innerHTML = ui(zh, en);
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => el.classList.remove('show'), 2600);
}

// ---------- settings ----------
const LANG_LABEL: Record<LangMode, string> = { zh: '中文', both: '中英', en: 'EN' };
function applySettings(s: State) {
  const d = document.documentElement;
  d.dataset.langMode = s.settings.lang;
  d.dataset.theme = s.settings.theme;
  d.dataset.size = s.settings.size;
  d.dataset.hasTrack = s.track ? 'yes' : 'no';
  if (s.track) d.dataset.track = s.track;
  else delete d.dataset.track;
  d.lang = s.settings.lang === 'en' ? 'en' : 'zh-Hans';
  $$('[data-lang-label]').forEach((el) => (el.textContent = LANG_LABEL[s.settings.lang]));
  $$('[data-set-lang]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.setLang === s.settings.lang)));
  $$('[data-set-theme]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.setTheme === s.settings.theme)));
  $$('[data-set-size]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.setSize === s.settings.size)));
}

document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement;
  const lang = target.closest<HTMLElement>('[data-set-lang]');
  if (lang) store.update((s) => (s.settings.lang = lang.dataset.setLang as LangMode));
  if (target.closest('[data-cycle-lang]')) {
    const order: LangMode[] = ['zh', 'both', 'en'];
    store.update((s) => (s.settings.lang = order[(order.indexOf(s.settings.lang) + 1) % 3]));
  }
  const theme = target.closest<HTMLElement>('[data-set-theme]');
  if (theme) store.update((s) => (s.settings.theme = theme.dataset.setTheme as State['settings']['theme']));
  const size = target.closest<HTMLElement>('[data-set-size]');
  if (size) store.update((s) => (s.settings.size = size.dataset.setSize as State['settings']['size']));

  const choose = target.closest<HTMLElement>('[data-choose-track], [data-set-track]');
  if (choose) {
    const id = choose.dataset.chooseTrack || choose.dataset.setTrack!;
    store.update((s) => (s.track = id));
    if (choose.dataset.setTrack) toast('已设为我的路径', 'Set as my path');
  }
});

// ---------- progress everywhere ----------
function renderProgress(s: State) {
  for (const t of data.tracks) {
    const done = doneIn(t, s);
    const total = t.lessons.length;
    $$(`[data-track-progress="${t.id}"]`).forEach((ring) => {
      const fg = ring.querySelector<SVGCircleElement>('.ring-fg');
      const c = Number(fg?.dataset.circ || 0);
      fg?.setAttribute('stroke-dashoffset', String(total ? c * (1 - done / total) : c));
      const label = ring.querySelector('[data-ring-label]');
      if (label) label.textContent = `${done}/${total}`;
    });
    $$(`[data-track-count="${t.id}"]`).forEach((el) => (el.textContent = done ? `${done}/${total}` : ''));
    const next = nextIn(t, s);
    for (const u of t.units) {
      const ud = u.lessons.filter((id) => s.completed[id]).length;
      $$(`[data-unit-progress="${t.id}:${u.id}"]`).forEach((el) => {
        el.style.setProperty('--p', u.lessons.length ? String(ud / u.lessons.length) : '0');
        const label = el.querySelector('[data-unit-label]');
        if (label) label.textContent = `${ud}/${u.lessons.length}`;
      });
    }
    for (const l of t.lessons) {
      $$(`[data-lesson-node="${l.id}"]`).forEach((el) => {
        el.classList.toggle('done', Boolean(s.completed[l.id]));
        el.classList.toggle('current', next?.id === l.id);
      });
    }
  }
  const lessons = data.tracks.flatMap((x) => x.lessons).filter((l) => s.completed[l.id]);
  const stat = (k: string, v: number) => $$(`[data-stat="${k}"]`).forEach((el) => (el.textContent = String(v)));
  stat('week', store.daysThisWeek(s));
  stat('done', lessons.length);
  stat('minutes', lessons.reduce((a, l) => a + l.minutes, 0));
  $$('[data-track-card]').forEach((el) => el.classList.toggle('is-mine', el.dataset.trackCard === s.track));
  $$('[data-set-track]').forEach((el) => el.toggleAttribute('hidden', el.dataset.setTrack === s.track));
  $$('[data-is-my-track]').forEach((el) => el.toggleAttribute('hidden', el.dataset.isMyTrack !== s.track));
}

// ---------- home dashboard ----------
function renderHome(s: State) {
  const box = document.querySelector<HTMLElement>('[data-continue]');
  if (!box) return;
  const t = trackById(s.track);
  if (!t) return;
  const next = nextIn(t, s);
  const done = doneIn(t, s);
  document.documentElement.style.setProperty('--accent', t.color);
  $$('[data-home-track]').forEach((el) => (el.innerHTML = bi(t.title)));
  $$('[data-home-track-link]').forEach((el) => el.setAttribute('href', t.url));
  if (next) {
    const unit = t.units.find((u) => u.id === next.unit);
    box.innerHTML = `
      <p class="eyebrow">${done ? ui('继续学习', 'Continue') : ui('从这里开始', 'Start here')}</p>
      <h2 class="continue-title">${bi(next.title)}</h2>
      <p class="muted">${unit ? bi(unit.title) : ''} · ${ui(`约 ${next.minutes} 分钟`, `${next.minutes} min`)}</p>
      <a class="btn btn-primary" href="${next.url}">${done ? ui('继续', 'Continue') : ui('开始第一课', 'Start lesson 1')}</a>`;
  } else if (t.lessons.length) {
    box.innerHTML = `
      <p class="eyebrow">${ui('这条路径已完成', 'Path complete')}</p>
      <h2 class="continue-title">${ui('你已经读完了目前的所有课程', "You've finished every lesson so far")}</h2>
      <p class="muted">${ui('新课程会陆续加入。也可以看看下一条路径。', 'New lessons are on the way. Or explore the next path.')}</p>
      <a class="btn btn-primary" href="${t.url}">${ui('回顾这条路径', 'Review this path')}</a>`;
  }
}

// ---------- lesson page ----------
function setupLesson() {
  const article = document.querySelector<HTMLElement>('[data-lesson-id]');
  if (!article) return;
  const id = article.dataset.lessonId!;
  if (store.get().last !== id) store.update((s) => (s.last = id));
  const btn = document.querySelector<HTMLButtonElement>('[data-complete]');
  const after = document.querySelector<HTMLElement>('[data-after-complete]');
  const paint = (s: State) => {
    const done = Boolean(s.completed[id]);
    btn?.classList.toggle('is-done', done);
    btn?.setAttribute('aria-pressed', String(done));
    after?.toggleAttribute('hidden', !done);
  };
  btn?.addEventListener('click', () => {
    const done = !store.get().completed[id];
    store.setComplete(id, done);
    if (done) {
      toast('完成了！做得好', 'Lesson complete — well done');
      after?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });
  store.subscribe(paint);
  paint(store.get());
}

// ---------- quick check ----------
function setupQuizzes() {
  $$('[data-quiz]').forEach((quiz) => {
    const answer = Number(quiz.dataset.answer);
    const options = $$<HTMLButtonElement>('[data-option]', quiz);
    options.forEach((opt) =>
      opt.addEventListener('click', () => {
        const right = Number(opt.dataset.option) === answer;
        options.forEach((o) => {
          o.disabled = true;
          if (Number(o.dataset.option) === answer) o.classList.add('correct');
        });
        if (!right) opt.classList.add('wrong');
        quiz.classList.add(right ? 'answered-right' : 'answered-wrong');
        quiz.querySelector('[data-quiz-result]')?.removeAttribute('hidden');
      }),
    );
  });
}

// ---------- me page ----------
function setupMe() {
  document.querySelector('[data-export]')?.addEventListener('click', () => {
    const blob = new Blob([store.exportJson()], { type: 'application/json' });
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `covenant-learn-${store.today()}.json` });
    a.click();
    URL.revokeObjectURL(a.href);
  });
  document.querySelector<HTMLInputElement>('[data-import]')?.addEventListener('change', async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    try {
      store.importJson(await file.text());
      toast('已恢复学习记录', 'Progress restored');
    } catch {
      toast('这不是有效的备份文件', 'That is not a valid backup file');
    }
  });
  const reset = document.querySelector<HTMLButtonElement>('[data-reset]');
  reset?.addEventListener('click', () => {
    if (reset.dataset.armed) {
      store.reset();
      delete reset.dataset.armed;
      reset.classList.remove('armed');
      toast('学习记录已清除', 'Progress cleared');
    } else {
      reset.dataset.armed = '1';
      reset.classList.add('armed');
      setTimeout(() => (delete reset.dataset.armed, reset.classList.remove('armed')), 4000);
    }
  });
}

function renderAll(s: State) {
  applySettings(s);
  renderProgress(s);
  renderHome(s);
}

store.subscribe(renderAll);
renderAll(store.get());
setupLesson();
setupQuizzes();
setupMe();

// Keep tabs in sync if progress changes in another tab/window.
window.addEventListener('storage', (e) => {
  if (e.key === store.KEY) store.refresh();
});
