// Tags rendered Markdown blocks with data-lang="zh" | "en" so the reader can
// switch between 中文 / EN / 中英 without editors writing any markup.
//
// Supported writing styles (the same ones the Project Covenant library uses):
//   1. Separate paragraphs:  an English paragraph, then a Chinese paragraph.
//   2. One paragraph, two lines joined by <br>:  "English...<br>\n中文..."
//   3. Headings "English | 中文".
// Tables, code and anything that already has a lang/data-lang attribute are
// left alone. A block counts as Chinese when it has at least as many Chinese
// characters as Latin words.

const CJK = /[㐀-鿿豈-﫿]/g;
const LATIN_WORD = /[A-Za-z]+(?:['’][A-Za-z]+)*/g;
const BLOCKS = new Set(['p', 'li', 'h2', 'h3', 'h4', 'h5', 'h6', 'dt', 'dd', 'figcaption', 'th', 'td']);
const CONTAINERS = new Set(['blockquote', 'ul', 'ol', 'section', 'div', 'details', 'dl', 'table', 'thead', 'tbody', 'tr', 'root']);
const SKIP = new Set(['pre', 'code', 'script', 'style', 'svg']);

function textOf(node) {
  if (node.type === 'text') return node.value;
  if (!node.children) return '';
  return node.children.map(textOf).join('');
}

export function detectLang(value) {
  const cjk = (value.match(CJK) || []).length;
  const latin = (value.match(LATIN_WORD) || []).length;
  if (!cjk && !latin) return null;
  return (cjk >= latin || (cjk >= 2 && cjk * 2 >= latin)) && cjk > 0 ? 'zh' : 'en';
}

const isBr = (n) => n.type === 'element' && n.tagName === 'br';
const hasLang = (n) => n.properties && (n.properties.lang || n.properties.dataLang);
const span = (lang, children) => ({
  type: 'element',
  tagName: 'span',
  properties: { dataLang: lang, className: ['lang-seg'] },
  children,
});

function splitOnBreaks(el) {
  const segments = [[]];
  for (const child of el.children) {
    if (isBr(child)) segments.push([]);
    else segments[segments.length - 1].push(child);
  }
  const tagged = segments
    .map((nodes) => ({ nodes, lang: detectLang(nodes.map(textOf).join('')) }))
    .filter((s) => s.nodes.some((n) => textOf(n).trim() || n.type === 'element'));
  const langs = new Set(tagged.map((s) => s.lang).filter(Boolean));
  if (langs.size < 2) return false; // all one language: keep the <br>s
  el.children = tagged.map((s) => (s.lang ? span(s.lang, s.nodes) : span('both', s.nodes)));
  el.properties = { ...el.properties, dataLang: 'both' };
  return true;
}

function splitHeadingPipe(el) {
  if (!el.children.every((c) => c.type === 'text')) return false;
  const value = textOf(el);
  const parts = value.split(/\s+\|\s+/);
  if (parts.length !== 2) return false;
  const [a, b] = parts.map(detectLang);
  if (!a || !b || a === b) return false;
  el.children = [
    span(a, [{ type: 'text', value: parts[0] }]),
    span(b, [{ type: 'text', value: parts[1] }]),
  ];
  el.properties = { ...el.properties, dataLang: 'both' };
  return true;
}

function tagBlock(el) {
  if (hasLang(el)) return;
  const hasBlockChildren = el.children.some(
    (c) => c.type === 'element' && (CONTAINERS.has(c.tagName) || c.tagName === 'p'),
  );
  if (hasBlockChildren) return visit(el); // e.g. a loose <li> holding <p>s
  if (el.tagName === 'th' || el.tagName === 'td') {
    if (splitHeadingPipe(el)) return;
    if (el.children.some(isBr) && splitOnBreaks(el)) return;
    return;
  }
  if (/^h[2-6]$/.test(el.tagName) && splitHeadingPipe(el)) return;
  if (el.children.some(isBr) && splitOnBreaks(el)) return;
  const lang = detectLang(textOf(el));
  if (lang) el.properties = { ...el.properties, dataLang: lang };
}

function visit(node) {
  for (const child of node.children || []) {
    if (child.type !== 'element' || SKIP.has(child.tagName) || hasLang(child)) continue;
    if (BLOCKS.has(child.tagName)) tagBlock(child);
    else if (CONTAINERS.has(child.tagName)) visit(child);
  }
}

export default function rehypeBilingual() {
  return (tree) => visit(tree);
}
