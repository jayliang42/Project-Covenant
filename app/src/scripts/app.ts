// Progressive enhancement for every page. Pages are fully readable without it;
// this adds language switching, local progress, quizzes and settings.
import * as store from './store';
import type { LangMode, State } from './store';

type Text = { zh: string; en?: string };
interface LessonInfo { id: string; title: Text; summary: Text; unit: string; minutes: number; url: string }
interface TrackInfo { id: string; color: string; title: Text; url: string; lessons: LessonInfo[]; units: { id: string; title: Text; lessons: string[] }[] }

const RELATED_BRIDGES: Record<string, { id: string; reason: Text }[]> = {
  'curious/01-a-library-of-books': [
    { id: 'seeking/05-manuscripts', reason: { zh: '跨路径求证 · 抄本怎么留存', en: 'Cross-path · How manuscripts survived' } },
    { id: 'new/01-reading-every-day', reason: { zh: '实践延伸 · 每天 15 分钟读经法', en: 'Practical step · 15-min daily reading' } },
  ],
  'curious/02-many-kinds-of-writing': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '进阶视角 · 在不同文体中读出基督', en: 'Deeper lens · Reading genres through Christ' } },
    { id: 'new/01-reading-every-day', reason: { zh: '实践延伸 · 按文体开始日常读经', en: 'Practical step · Daily reading by genre' } },
  ],
  'curious/03-how-the-bible-came-to-us': [
    { id: 'seeking/05-manuscripts', reason: { zh: '跨路径深挖 · 死海古卷与抄本互校', en: 'Deep dive · Dead Sea Scrolls & textual criticism' } },
    { id: 'seeking/04-what-history-can-show', reason: { zh: '历史互证 · 考古与史料的边界', en: 'Historical lens · Archaeology & evidence limits' } },
  ],
  'curious/04-one-story': [
    { id: 'deeper/01-covenant-thread', reason: { zh: '跨路径深挖 · 串起全书的圣约主线', en: 'Deep dive · The covenant backbone of Scripture' } },
    { id: 'curious/05-creation-and-fall', reason: { zh: '顺着读 · 故事的起点与破裂', en: 'Next up · Creation and the fracture' } },
  ],
  'curious/05-creation-and-fall': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '大问题延伸 · 为什么世界会有苦难', en: 'Big question · Why is there suffering?' } },
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '基要延伸 · 创造天地的主是谁', en: 'Foundation · Who is the Maker of heaven and earth?' } },
  ],
  'curious/06-who-is-jesus': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '历史求证 · 史学界如何看耶稣与空坟墓', en: 'Historical lens · Historians on Jesus & the empty tomb' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '基要延伸 · 基督的身份与救赎工作', en: 'Foundation · Christ’s person and redemptive work' } },
  ],
  'curious/07-what-jesus-taught': [
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '跨路径延伸 · 恩典与道德努力有什么不同', en: 'Cross-path · Grace vs. moral scorekeeping' } },
    { id: 'new/02-learning-to-pray', reason: { zh: '实践延伸 · 照着耶稣教的主祷文开口', en: 'Practical step · Praying with the Lord’s Prayer' } },
  ],
  'seeking/01-questions-are-welcome': [
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '最常问 · 良善的神与真实苦难', en: 'Most asked · A good God and real suffering' } },
    { id: 'curious/01-a-library-of-books', reason: { zh: '全景入门 · 先看清圣经这本「图书馆」', en: 'First look · See how the 66-book library works' } },
  ],
  'seeking/02-why-is-there-suffering': [
    { id: 'curious/05-creation-and-fall', reason: { zh: '背景脉络 · 世界为何既美善又伤痕累累', en: 'Context · Why the world is both noble and broken' } },
    { id: 'new/02-learning-to-pray', reason: { zh: '诚实回应 · 如何在困惑与眼泪中祷告', en: 'Honest response · Praying through lament and tears' } },
  ],
  'seeking/03-does-god-exist': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '下一步求证 · 从哲学线索走向历史现场', en: 'Next inquiry · From cosmic clues to historical evidence' } },
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '延伸阅读 · 圣经所说的神是怎样的一位', en: 'Further look · Who is the God Scripture speaks of?' } },
  ],
  'seeking/04-what-history-can-show': [
    { id: 'deeper/03-second-temple-world', reason: { zh: '历史现场 · 走进第二圣殿与罗马帝国', en: 'Historical world · Second Temple & Roman context' } },
    { id: 'seeking/05-manuscripts', reason: { zh: '文本求证 · 古卷抄本有没有被篡改', en: 'Textual inquiry · Were the manuscripts altered?' } },
  ],
  'seeking/05-manuscripts': [
    { id: 'curious/03-how-the-bible-came-to-us', reason: { zh: '脉络总览 · 正典形成与现代圣经译本', en: 'Overview · Canon formation & modern translations' } },
    { id: 'seeking/06-what-it-means-to-believe', reason: { zh: '核心落点 · 证据看清之后，相信意味着什么', en: 'Key question · Beyond evidence, what is faith?' } },
  ],
  'seeking/06-what-it-means-to-believe': [
    { id: 'new/01-reading-every-day', reason: { zh: '起步实践 · 怎样开始每天自己读圣经', en: 'First habit · How to start reading daily' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '基要扎根 · 更深认识耶稣基督的救恩', en: 'Foundation · Deeper into the gospel of Christ' } },
  ],
  'new/01-reading-every-day': [
    { id: 'curious/02-many-kinds-of-writing', reason: { zh: '读经工具 · 辨认叙事、诗篇与书信文体', en: 'Reading tool · Recognizing biblical genres' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '进阶方法 · 观察、解释、应用的归纳法', en: 'Next level · Observation, interpretation, application' } },
  ],
  'new/02-learning-to-pray': [
    { id: 'new/03-i-believe-in-god-the-father', reason: { zh: '信仰根基 · 认识我们在祷告中呼求的天父', en: 'Foundation · Knowing the Father we pray to' } },
    { id: 'seeking/02-why-is-there-suffering', reason: { zh: '深度共鸣 · 诗篇如何把眼泪带进祷告', en: 'Deep resonance · How the Psalms bring tears to prayer' } },
  ],
  'new/03-i-believe-in-god-the-father': [
    { id: 'curious/05-creation-and-fall', reason: { zh: '故事起点 · 创造的美善与人的护理', en: 'Story origin · Creation’s goodness and care' } },
    { id: 'deeper/01-covenant-thread', reason: { zh: '整全视野 · 天父在历史中立约的信实', en: 'Whole-Bible view · The Father’s covenant faithfulness' } },
  ],
  'new/04-jesus-christ-his-only-son': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '跨路径深挖 · 从整本旧约读出基督的预表', en: 'Deep dive · Reading the Old Testament through Christ' } },
    { id: 'curious/06-who-is-jesus', reason: { zh: '福音书肖像 · 回到四福音看耶稣的生平', en: 'Gospel portrait · Jesus’ life in the four Gospels' } },
  ],
  'new/05-baptism-and-communion': [
    { id: 'deeper/01-covenant-thread', reason: { zh: '神学脉络 · 「用我血所立的新约」从何而来', en: 'Theological thread · Where “the new covenant in my blood” comes from' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '团契实践 · 在群体中一起研读与彼此建造', en: 'Community practice · Studying Scripture together' } },
  ],
  'deeper/01-covenant-thread': [
    { id: 'deeper/02-reading-the-ot-through-christ', reason: { zh: '顺着深读 · 圣约如何汇聚在基督身上', en: 'Next deep dive · How the covenants converge in Christ' } },
    { id: 'new/05-baptism-and-communion', reason: { zh: '礼仪呼应 · 圣约记号在洗礼与圣餐中的延续', en: 'Sacramental echo · Covenant signs in baptism & communion' } },
  ],
  'deeper/02-reading-the-ot-through-christ': [
    { id: 'deeper/03-second-temple-world', reason: { zh: '历史纵深 · 新约引用旧约时的第二圣殿语境', en: 'Historical depth · Second Temple context of NT citations' } },
    { id: 'new/04-jesus-christ-his-only-son', reason: { zh: '信经核心 · 先知、祭司、君王三重职分', en: 'Creedal core · Prophet, Priest, and King' } },
  ],
  'deeper/03-second-temple-world': [
    { id: 'seeking/04-what-history-can-show', reason: { zh: '历史互证 · 约瑟夫斯、塔西佗与考古铭文', en: 'Historical cross-check · Josephus, Tacitus & inscriptions' } },
    { id: 'deeper/04-leading-a-study', reason: { zh: '查经实践 · 把历史背景转化为好问题', en: 'Study practice · Turning historical context into good questions' } },
  ],
  'deeper/04-leading-a-study': [
    { id: 'new/01-reading-every-day', reason: { zh: '个人根基 · 先建立自己的日常读经节奏', en: 'Personal rhythm · Grounding group study in daily reading' } },
    { id: 'curious/02-many-kinds-of-writing', reason: { zh: '文体敏感度 · 帮小组成员分清叙事与书信', en: 'Genre sensitivity · Helping a group read genres well' } },
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
        zh: `跨路径拓展 · ${t.title.zh}`,
        en: `Cross-path pick · ${t.title.en || t.title.zh}`,
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
