// Progressive enhancement for every page. Pages are fully readable without it;
// this adds language switching, local progress, quizzes and settings.
import * as store from './store';
import type { LangMode, State } from './store';

type Text = { zh: string; en?: string };
interface LessonInfo { id: string; title: Text; summary: Text; unit: string; minutes: number; url: string }
interface TrackInfo { id: string; color: string; title: Text; url: string; lessons: LessonInfo[]; units: { id: string; title: Text; lessons: string[] }[] }

const RELATED_BRIDGES: Record<string, { id: string; reason: Text }[]> = {
  'curious/01-a-library-of-books': [
    { id: 'seeking/05-manuscripts', reason: { zh: '想查证 · 抄本是怎样保存下来的', en: 'Checking the evidence · How the manuscripts survived' } },
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 每天读经 15 分钟', en: 'Try it · Reading 15 minutes a day' } },
  ],
  'curious/02-many-kinds-of-writing': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '读深一点 · 怎样在旧约里读出基督', en: 'Going deeper · Reading the Old Testament through Christ' } },
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 开始每天读经', en: 'Try it · Start reading every day' } },
  ],
  'curious/03-how-the-bible-came-to-us': [
    { id: 'seeking/05-manuscripts', reason: { zh: '读深一点 · 死海古卷和抄本比对', en: 'Going deeper · The Dead Sea Scrolls and comparing manuscripts' } },
    { id: 'seeking/04-what-history-can-show', reason: { zh: '想查证 · 考古和史料能说明什么', en: 'Checking the evidence · What archaeology and sources can show' } },
  ],
  'curious/04-one-story': [
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · 贯穿全书的圣约', en: 'Going deeper · The covenants that run through the Bible' } },
    { id: 'curious/05-creation-and-fall', reason: { zh: '接着读 · 创造和堕落', en: 'Next · Creation and fall' } },
  ],
  'curious/05-creation-and-fall': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '相关问题 · 世界上为什么有苦难', en: 'Related question · Why is there suffering?' } },
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '相关一课 · 创造天地的主是谁', en: 'Related lesson · Who is the Maker of heaven and earth?' } },
  ],
  'curious/06-who-is-jesus': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '想查证 · 历史学家怎样看耶稣和空坟墓', en: 'Checking the evidence · Historians on Jesus and the empty tomb' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '相关一课 · 基督是谁，做了什么', en: 'Related lesson · Who Christ is and what he did' } },
  ],
  'curious/07-what-jesus-taught': [
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '相关问题 · 恩典和道德努力有什么不同', en: 'Related question · How grace differs from moral effort' } },
    { id: 'new/02-learning-to-pray', reason: { zh: '动手做 · 用主祷文祷告', en: 'Try it · Praying the Lord’s Prayer' } },
  ],
  'seeking/01-questions-are-welcome': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '最常问 · 良善的神和苦难', en: 'Most asked · A good God and suffering' } },
    { id: 'curious/01-a-library-of-books', reason: { zh: '入门 · 圣经是一本怎样的书', en: 'First look · What kind of book the Bible is' } },
  ],
  'seeking/02-why-is-there-suffering': [
    { id: 'curious/05-creation-and-fall', reason: { zh: '背景 · 世界为什么又美又痛', en: 'Background · Why the world is both beautiful and broken' } },
    { id: 'new/02-learning-to-pray', reason: { zh: '动手做 · 在困惑和眼泪中怎样祷告', en: 'Try it · Praying in confusion and tears' } },
  ],
  'seeking/03-does-god-exist': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '接着读 · 历史能说明什么', en: 'Next · What history can show' } },
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '相关一课 · 圣经所说的神是怎样的一位', en: 'Related lesson · Who is the God the Bible speaks of?' } },
  ],
  'seeking/04-what-history-can-show': [
    { id: 'deeper/03-second-temple-world', reason: { zh: '背景 · 第二圣殿时期和罗马帝国', en: 'Background · The Second Temple period and the Roman Empire' } },
    { id: 'seeking/05-manuscripts', reason: { zh: '想查证 · 抄本有没有被改过', en: 'Checking the evidence · Were the manuscripts changed?' } },
  ],
  'seeking/05-manuscripts': [
    { id: 'curious/03-how-the-bible-came-to-us', reason: { zh: '概览 · 正典的形成和现代译本', en: 'Overview · How the canon formed, and modern translations' } },
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '接着读 · “信”是什么意思', en: 'Next · What it means to believe' } },
  ],
  'seeking/06-what-it-means-to-believe': [
    { id: 'new/01-reading-every-day', reason: { zh: '动手做 · 怎样开始每天读圣经', en: 'Try it · How to start reading daily' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '相关一课 · 耶稣基督和他的救恩', en: 'Related lesson · Jesus Christ and his salvation' } },
  ],
  'new/01-reading-every-day': [
    { id: 'curious/02-many-kinds-of-writing', reason: { zh: '读经工具 · 分辨叙事、诗歌和书信', en: 'Reading tool · Telling narrative, poetry, and letters apart' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '读深一点 · 观察、解释、应用', en: 'Going deeper · Observation, interpretation, application' } },
  ],
  'new/02-learning-to-pray': [
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '相关一课 · 我们祷告时呼求的天父', en: 'Related lesson · The Father we pray to' } },
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '相关问题 · 神是良善的，为什么有苦难', en: 'Related question · If God is good, why is there suffering?' } },
  ],
  'new/03-i-believe-in-god-the-father': [
    { id: 'curious/05-creation-and-fall', reason: { zh: '背景 · 创造的美善和人的堕落', en: 'Background · The goodness of creation and the fall' } },
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · 神在历史中立的约', en: 'Going deeper · The covenants God made in history' } },
  ],
  'new/04-jesus-christ-his-only-son': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '读深一点 · 旧约怎样指向基督', en: 'Going deeper · How the Old Testament points to Christ' } },
    { id: 'curious/06-who-is-jesus', reason: { zh: '相关一课 · 四福音书里的耶稣', en: 'Related lesson · Jesus in the four Gospels' } },
  ],
  'new/05-baptism-and-communion': [
    { id: 'deeper/01-covenant-thread', reason: { zh: '读深一点 · “用我血所立的新约”从哪里来', en: 'Going deeper · Where “the new covenant in my blood” comes from' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '动手做 · 和别人一起查经', en: 'Try it · Studying the Bible with others' } },
  ],
  'deeper/01-covenant-thread': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '接着读 · 各个圣约怎样在基督里成全', en: 'Next · How the covenants are fulfilled in Christ' } },
    { id: 'new/05-baptism-and-communion', reason: { zh: '相关一课 · 洗礼和圣餐', en: 'Related lesson · Baptism and the Lord’s Supper' } },
  ],
  'deeper/02-reading-the-ot-through-christ': [
    { id: 'deeper/03-second-temple-world', reason: { zh: '背景 · 第二圣殿时期', en: 'Background · The Second Temple period' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '相关一课 · 信经里的耶稣基督', en: 'Related lesson · Jesus Christ in the Creed' } },
  ],
  'deeper/03-second-temple-world': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '想查证 · 约瑟夫斯、塔西佗和考古铭文', en: 'Checking the evidence · Josephus, Tacitus, and inscriptions' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '动手做 · 用历史背景设计查经问题', en: 'Try it · Using historical background to write study questions' } },
  ],
  'deeper/04-leading-a-study': [
    { id: 'new/01-reading-every-day', reason: { zh: '相关一课 · 先养成自己每天读经的习惯', en: 'Related lesson · Build your own daily reading habit first' } },
    { id: 'curious/02-many-kinds-of-writing', reason: { zh: '读经工具 · 帮组员分清叙事和书信', en: 'Reading tool · Helping a group tell narrative from letters' } },
  ],
};

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
  const noteKeys = Object.keys(s.notes || {}).filter((k) => s.notes[k]?.trim());
  const stat = (k: string, v: number) => $$(`[data-stat="${k}"]`).forEach((el) => (el.textContent = String(v)));
  stat('week', store.daysThisWeek(s));
  stat('done', lessons.length);
  stat('minutes', lessons.reduce((a, l) => a + l.minutes, 0));
  stat('notes', noteKeys.length);
  $$('[data-track-card]').forEach((el) => el.classList.toggle('is-mine', el.dataset.trackCard === s.track));
  $$('[data-set-track]').forEach((el) => el.toggleAttribute('hidden', el.dataset.setTrack === s.track));
  $$('[data-is-my-track]').forEach((el) => el.toggleAttribute('hidden', el.dataset.isMyTrack !== s.track));
  renderMyNotes(s);
}

function renderMyNotes(s: State) {
  const box = document.querySelector<HTMLElement>('[data-my-notes]');
  if (!box) return;
  const allLessons = data.tracks.flatMap((t) => t.lessons.map((l) => ({ track: t, lesson: l })));
  const entries = Object.entries(s.notes || {})
    .filter(([, text]) => text && text.trim())
    .map(([id, text]) => ({
      id,
      text: text.trim(),
      found: allLessons.find((x) => x.lesson.id === id),
    }));
  if (!entries.length) {
    box.innerHTML = `<div class="notes-empty">
      <p>${ui('还没有保存的思考笔记。', 'No reflection notes saved yet.')}</p>
      <p class="muted small">${ui('在任意一课的「想一想」下方写下你的体会，会自动保存在本机浏览器中，并随备份文件一起导出。', 'Write your thoughts under "Reflect" in any lesson. They stay in this browser and are included when you export a backup.')}</p>
    </div>`;
    return;
  }
  box.innerHTML = `<ul class="notes-list">${entries
    .map(({ id, text, found }) => {
      const title = found ? bi(found.lesson.title) : esc(id);
      const href = found ? found.lesson.url : '#';
      const trackBadge = found ? `<span class="note-track" style="--accent:${esc(found.track.color)}">${bi(found.track.title)}</span>` : '';
      return `<li class="note-card">
        <div class="note-head">
          <a class="note-lesson-link" href="${href}">${title}</a>
          ${trackBadge}
        </div>
        <p class="note-body">${esc(text)}</p>
      </li>`;
    })
    .join('')}</ul>`;
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
  renderForYou(s, next?.id);
}

function renderForYou(s: State, primaryNextId?: string) {
  const wrap = document.querySelector<HTMLElement>('[data-for-you-wrap]');
  const grid = document.querySelector<HTMLElement>('[data-for-you]');
  if (!wrap || !grid) return;

  const all = data.tracks.flatMap((t) => t.lessons.map((l) => ({ track: t, lesson: l })));
  const byId = new Map(all.map((x) => [x.lesson.id, x]));

  const recentDoneId = Object.entries(s.completed || {})
    .sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0))
    .map(([id]) => id)[0];
  const anchorId = s.last || recentDoneId || primaryNextId;

  const picks: { track: TrackInfo; lesson: LessonInfo; reason: Text }[] = [];
  const seen = new Set<string>();
  if (primaryNextId) seen.add(primaryNextId);

  const pushPick = (id: string, reason: Text) => {
    if (picks.length >= 3 || seen.has(id) || s.completed[id]) return;
    const found = byId.get(id);
    if (!found) return;
    seen.add(id);
    picks.push({ ...found, reason });
  };

  if (anchorId && RELATED_BRIDGES[anchorId]) {
    for (const b of RELATED_BRIDGES[anchorId]) pushPick(b.id, b.reason);
  }
  if (recentDoneId && recentDoneId !== anchorId && RELATED_BRIDGES[recentDoneId]) {
    for (const b of RELATED_BRIDGES[recentDoneId]) pushPick(b.id, b.reason);
  }

  for (const t of data.tracks) {
    if (t.id === s.track) continue;
    const cand = nextIn(t, s);
    if (cand) {
      pushPick(cand.id, {
        zh: `另一条路径 · ${t.title.zh}`,
        en: `Another path · ${t.title.en || t.title.zh}`,
      });
    }
  }

  if (!picks.length) {
    wrap.setAttribute('hidden', '');
    return;
  }
  wrap.removeAttribute('hidden');
  grid.innerHTML = picks
    .map(
      ({ track, lesson, reason }) => `
      <a class="question-card" href="${lesson.url}">
        <span class="question-tag">${bi(reason)}</span>
        <strong class="question-title">${bi(lesson.title)}</strong>
        <p class="muted small">${bi(lesson.summary)}</p>
        <span class="question-cta">${bi(track.title)} · ${ui(`约 ${lesson.minutes} 分钟`, `${lesson.minutes} min`)}</span>
      </a>`,
    )
    .join('');
}

// ---------- lesson page ----------
function setupLesson() {
  const article = document.querySelector<HTMLElement>('[data-lesson-id]');
  if (!article) return;
  const id = article.dataset.lessonId!;
  if (store.get().last !== id) store.update((s) => (s.last = id));
  const btn = document.querySelector<HTMLButtonElement>('[data-complete]');
  const after = document.querySelector<HTMLElement>('[data-after-complete]');
  const noteInput = document.querySelector<HTMLTextAreaElement>('[data-lesson-note]');
  const noteStatus = document.querySelector<HTMLElement>('[data-note-saved]');
  if (noteInput) {
    noteInput.value = store.get().notes?.[id] || '';
    let noteTimer: number | undefined;
    noteInput.addEventListener('input', () => {
      clearTimeout(noteTimer);
      noteTimer = window.setTimeout(() => {
        store.setNote(id, noteInput.value);
        if (noteStatus) {
          noteStatus.removeAttribute('hidden');
          window.setTimeout(() => noteStatus.setAttribute('hidden', ''), 1800);
        }
      }, 250);
    });
  }
  const paint = (s: State) => {
    const done = Boolean(s.completed[id]);
    btn?.classList.toggle('is-done', done);
    btn?.setAttribute('aria-pressed', String(done));
    after?.toggleAttribute('hidden', !done);
    if (noteInput && document.activeElement !== noteInput) {
      noteInput.value = s.notes?.[id] || '';
    }
  };
  btn?.addEventListener('click', () => {
    const done = !store.get().completed[id];
    store.setComplete(id, done);
    if (done) {
      toast('完成了！做得好', 'Lesson complete. Well done.');
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

function setupKeyboard() {
  document.addEventListener('keydown', (e) => {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
    const target = e.target as HTMLElement | null;
    if (target && (target.matches('input, textarea, select') || target.isContentEditable)) {
      if (e.key === 'Escape') target.blur();
      return;
    }
    if (e.key === 'l' || e.key === 'L') {
      const order: LangMode[] = ['zh', 'both', 'en'];
      let nextLang: LangMode = 'zh';
      store.update((s) => {
        nextLang = order[(order.indexOf(s.settings.lang) + 1) % 3];
        s.settings.lang = nextLang;
      });
      const msg: Record<LangMode, [string, string]> = {
        zh: ['显示语言：中文', 'Language: Chinese'],
        both: ['显示语言：中英对照', 'Language: Bilingual'],
        en: ['显示语言：English', 'Language: English'],
      };
      toast(msg[nextLang][0], msg[nextLang][1]);
    } else if (e.key === 'ArrowLeft' || e.key === '[') {
      const prev = document.querySelector<HTMLAnchorElement>('[data-prev-lesson]');
      if (prev) window.location.href = prev.href;
    } else if (e.key === 'ArrowRight' || e.key === ']') {
      const next = document.querySelector<HTMLAnchorElement>('[data-next-lesson]');
      if (next) window.location.href = next.href;
    } else if (e.key === 'n' || e.key === 'N') {
      const note = document.querySelector<HTMLTextAreaElement>('[data-lesson-note]');
      if (note) {
        e.preventDefault();
        note.focus();
        note.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else if (e.key === 'c' || e.key === 'C') {
      const btn = document.querySelector<HTMLButtonElement>('[data-complete]');
      if (btn) btn.click();
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
setupKeyboard();

// Keep tabs in sync if progress changes in another tab/window.
window.addEventListener('storage', (e) => {
  if (e.key === store.KEY) store.refresh();
});
