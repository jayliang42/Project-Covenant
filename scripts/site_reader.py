"""Reading chrome for already-rendered, approved site pages (one local language-switch script).

This module never loads repository files or fetches remote content. Every link
is selected from the verified page map supplied by the static-site builder.
"""
from __future__ import annotations

import html
import math
import posixpath
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import quote


SITE_JS_PATH = "assets/lang.js"
CSP = (
    "default-src 'none'; style-src 'self'; img-src 'self'; font-src 'none'; "
    "script-src 'self'; connect-src 'none'; object-src 'none'; frame-src 'none'; "
    "form-action 'none'; base-uri 'none'"
)

# A reading route, not a claim that the library is a complete Bible translation.
STORY_ROUTE = (
    "Bible_Timeline/README.md",
    "Bible_Timeline/First_Steps_Bilingual.md",
    "Bible_Timeline/Bible_Timeline_Bilingual.md",
    "Bible_Timeline/Old_Testament_Timeline_Bilingual.md",
    "Bible_Timeline/New_Testament_Timeline_Bilingual.md",
    "Bible_Timeline/Bible_By_Book_Bilingual.md",
    "Bible_Timeline/Bible_Reading_Toolkit_Bilingual.md",
    "Bible_Timeline/How_the_Bible_Came_to_Us_Bilingual.md",
    "Bible_Timeline/Bible_People_Bilingual.md",
    "Bible_Timeline/Bible_Covenants_Bilingual.md",
    "Bible_Timeline/Feasts_of_the_Bible_Bilingual.md",
    "Bible_Timeline/Parables_of_Jesus_Bilingual.md",
    "Bible_Timeline/Miracles_of_Jesus_Bilingual.md",
    "Bible_Timeline/Key_Passages_Bilingual.md",
    "Bible_Timeline/Prayers_in_the_Bible_Bilingual.md",
    "Bible_Timeline/Psalms_for_Different_Times_Bilingual.md",
    "Bible_Timeline/52周圣经故事线_查经与史料阅读计划.md",
    "Bible_Timeline/Bible_Timeline_Cheat_Sheet.md",
)
COLLECTIONS = (
    ("Bible_Timeline", "Storyline | 圣经故事线", "Follow the story, then explore its context. | 先读故事线，再深入背景。"),
    ("Bilingual_Notes", "Notes | 讲道与团契笔记", "Read draft sermon and fellowship notes. | 阅读讲道与团契笔记草稿。"),
    ("Book_Studies", "Book studies | 书籍研读", "Read with guides and source boundaries. | 带着导读和来源边界阅读。"),
    ("Christian_Traditions", "Traditions | 基督教传统", "Explore historical traditions and their differences. | 了解历史传统及其差异。"),
    ("Bible_Translations", "Translations | 圣经译本", "Find access guides and reading notes. | 查找获取指南与阅读说明。"),
    ("Maps", "Maps | 地图", "Read offline maps with bilingual labels. | 阅读带双语地名的离线地图。"),
    ("Glossary", "Glossary | 词汇表", "Look up common words in plain language. | 用白话查找常见词语。"),
)


# Short beginner guides surfaced on the home page, in reading order.
QUICK_GUIDES = (
    ("Bible_Timeline/Bible_Reading_Toolkit_Bilingual.md", "Reading Toolkit | 读经工具箱", "Find a passage and read each kind of writing. | 查经文出处，读懂不同文体。"),
    ("Bible_Timeline/Bible_People_Bilingual.md", "People | 圣经人物", "Who’s who, in story order. | 按故事顺序认识主要人物。"),
    ("Maps/Bible_Places_Bilingual.md", "Places | 圣经地名", "Key places, each linked to a map. | 重要地点，附地图链接。"),
    ("Bible_Timeline/Bible_Covenants_Bilingual.md", "Covenants | 圣经中的约", "The five covenants that carry the story. | 贯穿故事的五个约。"),
    ("Bible_Timeline/Parables_of_Jesus_Bilingual.md", "Parables | 耶稣的比喻", "Nineteen parables and how to read them. | 十九个比喻及读法。"),
    ("Bible_Timeline/Key_Passages_Bilingual.md", "Key Passages | 值得熟悉的经文", "Thirty-six passages worth knowing well. | 三十六段值得熟悉的经文。"),
    ("Bible_Timeline/Prayers_in_the_Bible_Bilingual.md", "Prayers | 圣经中的祷告", "Twenty-one prayers to learn from. | 二十一篇可以学习的祷告。"),
    ("Bible_Timeline/Psalms_for_Different_Times_Bilingual.md", "Psalms for Different Times | 不同处境中的诗篇", "A psalm for what you are going through. | 为当下处境找一篇诗篇。"),
)

# --- Language display -------------------------------------------------------
# Paired English/Chinese text is marked at build time so a reader can choose
# Chinese, English, or both. Marking never removes text: with no script the
# page shows both languages exactly as before.

_CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
_LATIN = re.compile(r"[A-Za-z]")
_TAG = re.compile(r"<[^>]*>")
_SEPARATOR = re.compile(r"\s+[|/]\s+|\s*｜\s*")
_VOID_TAGS = {"br", "img", "hr", "meta", "link"}
LANG_EN = "en"
LANG_ZH = "zh-Hans"


def text_language(fragment: str) -> str | None:
    """Return "en", "zh", or None (neutral or genuinely mixed) for an HTML fragment."""
    text = html.unescape(_TAG.sub(" ", fragment))
    chinese = len(_CJK.findall(text))
    latin = len(_LATIN.findall(text))
    if not chinese and not latin:
        return None
    if not chinese:
        return "en"
    if not latin:
        return "zh"
    ratio = chinese * 3 / latin
    if ratio >= 2.5:
        return "zh"
    if ratio <= 0.4:
        return "en"
    return None


def _top_level_separators(fragment: str) -> list[tuple[int, int]]:
    """Separator spans that sit outside every tag, so splitting keeps markup balanced."""
    depth = 0
    spans: list[tuple[int, int]] = []
    cursor = 0
    while cursor < len(fragment):
        if fragment[cursor] == "<":
            close = fragment.find(">", cursor)
            if close < 0:
                return []
            tag = fragment[cursor + 1:close].strip()
            name = re.match(r"/?([A-Za-z0-9]+)", tag)
            if name and name.group(1).casefold() not in _VOID_TAGS and not tag.endswith("/"):
                depth += -1 if tag.startswith("/") else 1
            cursor = close + 1
            continue
        if depth == 0:
            match = _SEPARATOR.match(fragment, cursor)
            if match and match.end() > match.start():
                spans.append((match.start(), match.end()))
                cursor = match.end()
                continue
        cursor += 1
    return spans if depth == 0 else []


def _wrap(fragment: str, language: str) -> str:
    code = LANG_EN if language == "en" else LANG_ZH
    return f'<span class="l-{language}" lang="{code}">{fragment}</span>'


_LABEL = re.compile(r"^(\s*)<strong>(.*?)</strong>(.*)$", re.S)


def _split_pair(inner: str) -> tuple[str, str] | None:
    """Split a two-language label such as "Read | 阅读：" into (English, Chinese)."""
    separators = _top_level_separators(inner)
    if len(separators) != 1:
        return None
    left, right = inner[:separators[0][0]], inner[separators[0][1]:]
    colon = ""
    for mark in ("：", ":"):
        if right.endswith(mark) or left.endswith(mark):
            colon = mark
    left, right = left.rstrip("：:"), right.rstrip("：:")
    languages = (text_language(left), text_language(right))
    if languages == ("en", "zh"):
        english, chinese = left, right
    elif languages == ("zh", "en"):
        english, chinese = right, left
    else:
        return None
    return english + (":" if colon else ""), chinese + ("：" if colon else "")


def bilingual_html(fragment: str) -> str:
    """Mark one rendered line (or heading/cell) by language, splitting "EN | 中文" pairs."""
    stripped = fragment.strip()
    if not stripped:
        return fragment
    label = _LABEL.match(fragment)
    if label:
        pair = _split_pair(label.group(2))
        if pair:
            english, chinese = pair
            marked_label = (f'<span class="l-bi"><strong>{label.group(2)}</strong></span>'
                            f'<span class="l-en1" lang="{LANG_EN}"><strong>{english}</strong></span>'
                            f'<span class="l-zh1" lang="{LANG_ZH}"><strong>{chinese}</strong></span>')
            rest = label.group(3)
            if not rest.strip():
                return label.group(1) + marked_label + rest
            rest_language = text_language(rest)
            if rest_language and not _top_level_separators(rest):
                return label.group(1) + _wrap(marked_label + rest, rest_language)
            return label.group(1) + marked_label + bilingual_html(rest)
    separators = _top_level_separators(fragment)
    if separators:
        parts: list[str] = []
        glue: list[str] = []
        start = 0
        for left, right in separators:
            parts.append(fragment[start:left])
            glue.append(fragment[left:right])
            start = right
        parts.append(fragment[start:])
        languages = [text_language(part) for part in parts]
        if all(languages) and "en" in languages and "zh" in languages:
            if len(parts) == 2 and languages[0] != languages[1]:
                return (_wrap(parts[0], languages[0]) + f'<span class="l-sep">{glue[0]}</span>'
                        + _wrap(parts[1], languages[1]))
            english = " · ".join(part.strip() for part, lang in zip(parts, languages) if lang == "en")
            chinese = " · ".join(part.strip() for part, lang in zip(parts, languages) if lang == "zh")
            return (f'<span class="l-bi">{fragment}</span>'
                    f'<span class="l-en1" lang="{LANG_EN}">{english}</span>'
                    f'<span class="l-zh1" lang="{LANG_ZH}">{chinese}</span>')
    language = text_language(fragment)
    return _wrap(fragment, language) if language else fragment


def bilingual_label(text: str) -> str:
    """Escape a plain chrome label such as "Home | 首页" and mark its languages."""
    return bilingual_html(html.escape(text))


def strip_single_language_copies(fragment: str) -> str:
    """Remove the extra one-language copies so outlines and timings count text once."""
    return re.sub(r'<span class="l-(?:en1|zh1)" lang="[^"]+">.*?</span>', "", fragment, flags=re.S)


@dataclass(frozen=True)
class Heading:
    identifier: str
    title: str
    level: int


class _OutlineParser(HTMLParser):
    """Read actual renderer IDs; never invent a second Markdown slug algorithm."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[Heading] = []
        self.ids: set[str] = set()
        self.pending_anchor = ""
        self.active: tuple[str, str, int] | None = None
        self.parts: list[str] = []
        self.copy_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "span" and (self.copy_depth or values.get("class") in {"l-en1", "l-zh1"}):
            self.copy_depth += 1
        identifier = values.get("id") or ""
        if identifier:
            self.ids.add(identifier)
        if tag == "a" and identifier and self.active is None:
            self.pending_anchor = identifier
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.active = (tag, identifier or self.pending_anchor, int(tag[1]))
            self.parts = []
            self.pending_anchor = ""
        elif self.active is None:
            self.pending_anchor = ""
        if tag == "br" and self.active:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self.copy_depth:
            self.copy_depth -= 1
            return
        if self.active and tag == self.active[0]:
            _, identifier, level = self.active
            title = " ".join("".join(self.parts).split())
            if identifier and title and level in {2, 3}:
                self.headings.append(Heading(identifier, title, level))
            self.active = None
            self.parts = []

    def handle_data(self, data: str) -> None:
        if self.copy_depth:
            return
        if self.active:
            self.parts.append(data)
        elif data.strip():
            self.pending_anchor = ""


def outline(body: str) -> list[Heading]:
    parser = _OutlineParser()
    parser.feed(body)
    parser.close()
    # Long research pages can have hundreds of subheadings. Prefer their main
    # sections without truncating them; use third-level headings only as fallback.
    major = [heading for heading in parser.headings if heading.level == 2]
    return major or parser.headings


def _href(current: str, target: str) -> str:
    start = PurePosixPath(current).parent.as_posix()
    return quote(posixpath.relpath(target, start=start), safe="/-._~")


def _link(href: str, label: str, *, css: str = "", current: bool = False) -> str:
    attributes = f' class="{html.escape(css, quote=True)}"' if css else ""
    if current:
        attributes += ' aria-current="page"'
    return f'<a href="{html.escape(href, quote=True)}"{attributes}>{bilingual_label(label)}</a>'


def collection_order(source: str, page_map: dict[str, str]) -> list[str]:
    parent = PurePosixPath(source).parent
    if parent.as_posix() == ".":
        return []
    members = [path for path in page_map if PurePosixPath(path).parent == parent]
    priorities = {path: index for index, path in enumerate(STORY_ROUTE)}
    return sorted(members, key=lambda path: (
        PurePosixPath(path).name != "README.md",
        priorities.get(path, len(priorities)),
        path,
    ))


def _title(source: str, titles: dict[str, str]) -> str:
    return titles.get(source, PurePosixPath(source).stem.replace("_", " "))


def _toc(body: str) -> str:
    headings = outline(body)
    if not headings:
        return ""
    links = "\n".join(
        "<li>" + _link("#" + quote(item.identifier, safe="-._~:"), item.title) + "</li>"
        for item in headings
    )
    return '<nav class="reader-toc" aria-label="On this page | 本页目录"><ul>' + links + "</ul></nav>"


def _library_nav(source: str, output: str, page_map: dict[str, str]) -> str:
    links = ["<li>" + _link(_href(output, page_map["README.md"]), "Home | 首页", current=source == "README.md") + "</li>"]
    for directory, label, _ in COLLECTIONS:
        hub = directory + "/README.md"
        if hub in page_map:
            links.append("<li>" + _link(_href(output, page_map[hub]), label, current=source == hub) + "</li>")
    return '<nav class="library-nav" aria-label="Library | 资料导航"><ul>' + "\n".join(links) + "</ul></nav>"


def _chapter_nav(source: str, output: str, page_map: dict[str, str], titles: dict[str, str]) -> str:
    ordered = collection_order(source, page_map)
    if not ordered:
        return ""
    links = "\n".join(
        "<li>" + _link(_href(output, page_map[path]), _title(path, titles), current=source == path) + "</li>"
        for path in ordered
    )
    return '<div class="sidebar-label">' + bilingual_label("In this collection | 本栏篇目") + '</div><nav class="chapter-nav" aria-label="Collection contents | 栏目目录"><ol>' + links + "</ol></nav>"


def _pager(source: str, output: str, page_map: dict[str, str], titles: dict[str, str]) -> str:
    ordered = collection_order(source, page_map)
    if source not in ordered or len(ordered) < 2:
        return ""
    index = ordered.index(source)
    links: list[str] = []
    for offset, label, css in ((-1, "Previous | 上一篇", "previous"), (1, "Next | 下一篇", "next")):
        position = index + offset
        if 0 <= position < len(ordered):
            target = ordered[position]
            href = html.escape(_href(output, page_map[target]), quote=True)
            links.append(f'<a class="{css}" href="{href}"><span class="pager-label">{bilingual_label(label)}</span><strong>{bilingual_label(_title(target, titles))}</strong></a>')
    return '<nav class="reading-pager" aria-label="Continue reading | 继续阅读">' + "\n".join(links) + "</nav>"


def _home_intro(output: str, page_map: dict[str, str], home_art: str | None = None) -> str:
    first = next((path for path in STORY_ROUTE[1:] if path in page_map), None)
    start = _link(_href(output, page_map[first]), "Start reading | 开始阅读 →", css="start-reading") if first else ""
    cards = []
    for index, (directory, label, description) in enumerate(COLLECTIONS, start=1):
        hub = directory + "/README.md"
        if hub not in page_map:
            continue
        href = html.escape(_href(output, page_map[hub]), quote=True)
        cards.append(f'<a class="collection-card" href="{href}"><span class="collection-number">{index:02d}</span><strong>{bilingual_label(label)}</strong><span class="collection-description">{bilingual_label(description)}</span></a>')
    guides = []
    for path, label, description in QUICK_GUIDES:
        if path not in page_map:
            continue
        href = html.escape(_href(output, page_map[path]), quote=True)
        guides.append(f'<a class="guide-card" href="{href}"><strong>{bilingual_label(label)}</strong><span class="collection-description">{bilingual_label(description)}</span></a>')
    quick = ""
    if guides:
        quick = ('<div class="eyebrow guide-heading"><span class="l-en" lang="en">QUICK GUIDES</span><span class="l-sep"> · </span><span class="l-zh" lang="zh-Hans">快速导览</span></div>'
                 '<nav class="guide-grid" aria-label="Quick guides | 快速导览">' + "\n".join(guides) + '</nav>')
    art = ""
    if home_art:
        art = ('<img class="home-art" src="' + html.escape(_href(output, home_art), quote=True)
               + '" alt="The Bible as a library of 66 books on two shelves | 两层书架上的 66 卷圣经">')
    return ('<div class="book-intro"><div class="eyebrow">'
            '<span class="l-en" lang="en">A READING LIBRARY</span><span class="l-sep"> · </span><span class="l-zh" lang="zh-Hans">阅读资料库</span></div>'
            '<div class="book-tagline"><span class="l-en" lang="en">One story. Many ways to explore.<br></span>'
            '<span class="l-zh" lang="zh-Hans">一条故事线，多种研读路径。</span></div>'
            '<p class="l-en" lang="en">Begin with a short guide, follow a reading plan, or return to a topic. Use the switch at the top right to read in Chinese, in English, or in both, and keep each guide’s Draft status and source notes in view.</p>'
            '<p class="l-zh" lang="zh-Hans">从短篇导读开始，跟随阅读计划，或回到感兴趣的专题。可以用右上角的按钮切换中文、英文或中英对照；请同时留意各页的 Draft 状态与来源说明。</p>'
            + start + art + '</div><nav class="collection-grid" aria-label="Choose a collection | 选择栏目">' + "\n".join(cards) + '</nav>' + quick)


def is_core_study(source: str) -> bool:
    """Identify study pages, keeping navigation and maintenance pages separate."""
    path = PurePosixPath(source)
    return path.parent.as_posix() in {
        "Bible_Timeline", "Bible_Translations", "Bilingual_Notes",
        "Book_Studies", "Christian_Traditions",
    } and path.name not in {
        "README.md", "INDEX_Chronological.md", "研究维护日志.md",
        "00_研究总索引与路线图.md",
    }


def reading_time(body: str, *, include_short: bool = False) -> str:
    """A declared reading aid, estimating one language rather than adding both."""
    text = html.unescape(re.sub(r"<[^>]*>", " ", strip_single_language_copies(body)))
    english_words = len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*", text))
    chinese_characters = len(re.findall(r"[\u3400-\u9fff]", text))
    minutes = max(english_words / 200, chinese_characters / 350)
    if minutes < 3 and not include_short:
        return ""
    low = max(1, math.ceil(minutes))
    high = max(low + 1, math.ceil(minutes * 1.35))
    return (f"Reading: about {low}–{high} min in one language; excludes assigned Bible reading and reflection. "
            f"| 阅读约 {low}–{high} 分钟（按一种语言，指定经文阅读与思考另计）。")


def render_page(source: str, output: str, title: str, body: str,
                page_map: dict[str, str], titles: dict[str, str], css_path: str,
                home_art: str | None = None) -> bytes:
    """Compose reading navigation around untouched, trusted renderer output."""
    if "README.md" not in page_map or page_map.get(source) != output:
        raise ValueError("READER_PAGE_MAP_INVALID")
    library = _library_nav(source, output, page_map)
    chapter_nav = _chapter_nav(source, output, page_map, titles)
    toc = _toc(body)
    home = _href(output, page_map["README.md"])
    ordered = collection_order(source, page_map)
    position = f'{ordered.index(source) + 1:02d} / {len(ordered):02d}' if source in ordered else ""
    collection_label = next((label for folder, label, _ in COLLECTIONS if PurePosixPath(source).parent.as_posix() == folder), "Reading library | 阅读资料库")
    metadata = f'<div class="reading-meta"><span class="reading-collection">{bilingual_label(collection_label)}</span><span class="reading-position">{position}</span></div>'
    estimate = reading_time(body, include_short=is_core_study(source))
    if estimate:
        metadata += '<p class="reading-time">' + bilingual_label(estimate) + '</p>'
    intro = _home_intro(output, page_map, home_art) if source == "README.md" else ""
    mobile_toc = '<details class="mobile-toc"><summary>' + bilingual_label("On this page | 本页目录") + '</summary>' + toc + '</details>' if toc else ""
    right_toc = '<aside class="outline-sidebar"><div class="sidebar-label">' + bilingual_label("On this page | 本页目录") + '</div>' + toc + '</aside>' if toc else '<div class="outline-sidebar"></div>'
    policy_links = []
    for path, label in (("PUBLICATION_POLICY.md", "Privacy | 隐私与发布"), ("LICENSE.md", "Licensing | 授权说明")):
        if path in page_map:
            policy_links.append(_link(_href(output, page_map[path]), label))
    article_class = "reading-body hub-page" if source.rsplit("/", 1)[-1] == "README.md" else "reading-body"
    document = f'''<!doctype html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{html.escape(title)} · Project Covenant</title>
<link rel="stylesheet" href="{html.escape(_href(output, css_path), quote=True)}">
<script src="{html.escape(_href(output, SITE_JS_PATH), quote=True)}"></script>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to content | 跳到正文</a>
<header class="site-header"><div class="header-inner">
<a class="site-title" href="{html.escape(home, quote=True)}"><span class="site-mark" aria-hidden="true">C</span>Project Covenant <span class="site-subtitle">圣约计划</span></a>
<span class="header-note">{bilingual_label("Read at your own pace | 按自己的节奏阅读")}</span>
<div class="lang-switch" role="group" aria-label="Language | 语言"><button type="button" data-lang-choice="zh" aria-pressed="false">中文</button><button type="button" data-lang-choice="en" aria-pressed="false">EN</button><button type="button" data-lang-choice="both" aria-pressed="false">中英</button></div>
</div></header>
<div class="mobile-navigation"><details><summary>{bilingual_label("Library & chapters | 资料与篇目")}</summary>{library}{chapter_nav}</details></div>
<div class="reading-layout">
<aside class="library-sidebar"><div class="sidebar-label">{bilingual_label("Explore | 浏览资料")}</div>{library}{chapter_nav}<div class="sidebar-note"><span class="l-en" lang="en">No account. No tracking.<br></span><span class="l-zh" lang="zh-Hans">无需账号，不记录阅读行为。</span></div></aside>
<main id="main-content" class="content" tabindex="-1">
{metadata}
{intro}
{mobile_toc}
<article class="{article_class}">
{body}
</article>
{_pager(source, output, page_map, titles)}
<div class="reading-end"><a href="#main-content">{bilingual_label("Back to top | 返回页首 ↑")}</a></div>
</main>
{right_toc}
</div>
<footer class="site-footer"><div class="footer-inner"><p>{bilingual_label("Read carefully. Keep the sources close. | 细读正文，保留来源。")}</p><p>{bilingual_label("No analytics, forms, comments, or remote assets. | 不使用分析追踪、表单、评论或远程资源。")}</p><nav aria-label="Publication information | 发布说明">{' · '.join(policy_links)}</nav></div></footer>
</body>
</html>
'''
    return document.encode("utf-8")


SITE_CSS = """\
:root {
  color-scheme: light dark;
  --background: #f7f6f2; --surface: #fffefa; --text: #292e29;
  --muted: #656d62; --line: #dfE2d8; --accent: #456346;
  --accent-soft: #eaf0e5; --code: #eeeee7; --max: 88rem;
  --serif: Georgia, "Noto Serif CJK SC", "Songti SC", SimSun, serif;
}
@media (prefers-color-scheme: dark) {
  :root { --background: #191c19; --surface: #20251f; --text: #e5e9df;
    --muted: #aab6a4; --line: #374134; --accent: #b7d1a5;
    --accent-soft: #2c3b28; --code: #2b3229; }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 5.5rem; }
body { margin: 0; background: var(--background); color: var(--text);
  font-family: system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 1rem; line-height: 1.8; }
a { color: var(--accent); text-underline-offset: .2em; overflow-wrap: anywhere; }
a:hover { text-decoration-thickness: .13em; }
a:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; border-radius: 3px; }
.skip-link { position: absolute; left: -9999px; top: .5rem; z-index: 30; background: var(--surface); padding: .6rem 1rem; }
.skip-link:focus { left: 1rem; }
.site-header { position: sticky; top: 0; z-index: 10; background: var(--surface); border-bottom: 1px solid var(--line); }
.header-inner { max-width: var(--max); margin: auto; padding: .9rem 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.site-title { display: flex; align-items: center; gap: .7rem; font-weight: 650; color: var(--text); text-decoration: none; letter-spacing: -.02em; }
.site-mark { display: inline-grid; place-items: center; width: 2.1rem; height: 2.4rem; border: 1px solid var(--accent); border-radius: 2px 6px 6px 2px; color: var(--accent); font: 1.5rem var(--serif); }
.site-subtitle { padding-left: .7rem; border-left: 1px solid var(--line); color: var(--muted); font-weight: 400; font-size: .9rem; }
.header-note { color: var(--muted); font-size: .75rem; }
.reading-layout { display: grid; grid-template-columns: 14rem minmax(0, 44rem) minmax(10rem, 14rem); gap: 2.25rem; max-width: var(--max); margin: 0 auto; padding: 2.25rem 1.5rem 4rem; align-items: start; }
.library-sidebar, .outline-sidebar { position: sticky; top: 6.25rem; max-height: calc(100dvh - 8rem); overflow-y: auto; scrollbar-width: thin; padding: 0 .65rem .8rem 0; }
.sidebar-label { color: var(--muted); font-size: .7rem; letter-spacing: .06em; margin: .3rem 0 .85rem; font-weight: 650; }
.library-nav ul, .chapter-nav ol, .reader-toc ul { padding: 0; list-style: none; margin: 0; }
.library-nav a { display: block; padding: .5rem .65rem; text-decoration: none; color: var(--text); font-size: .83rem; border-radius: .3rem; }
.library-nav li + li { margin-top: .15rem; }
.library-nav a:hover, .chapter-nav a:hover { background: var(--accent-soft); }
.library-nav a[aria-current="page"], .chapter-nav a[aria-current="page"] { background: var(--accent-soft); color: var(--accent); font-weight: 650; border-left: 2px solid var(--accent); }
.chapter-nav { margin-top: .5rem; }
.library-nav + .sidebar-label { border-top: 1px solid var(--line); padding-top: 1.5rem; margin-top: 1.5rem; }
.chapter-nav a { display: block; font-size: .75rem; padding: .5rem .65rem; text-decoration: none; color: var(--muted); border-left: 2px solid transparent; line-height: 1.65; }
.chapter-nav li + li { margin-top: .15rem; }
.sidebar-note { margin-top: 1.8rem; color: var(--muted); font-size: .7rem; border-top: 1px solid var(--line); padding-top: 1rem; }
.reader-toc a { display: block; padding: .45rem .65rem; color: var(--muted); font-size: .74rem; line-height: 1.6; text-decoration: none; border-left: 1px solid var(--line); }
.reader-toc a:hover { color: var(--accent); border-left-color: var(--accent); }
.content { min-width: 0; padding: 0 0 2rem; outline: none; overflow-wrap: anywhere; }
.reading-meta { display: flex; gap: 1rem; justify-content: space-between; align-items: center; color: var(--muted); font-size: .72rem; padding: .3rem 0 1.3rem; border-bottom: 1px solid var(--line); margin-bottom: 2rem; }
.reading-position { font-variant-numeric: tabular-nums; white-space: nowrap; letter-spacing: .1em; }
.reading-time { color: var(--muted); font-size: .82rem; line-height: 1.7; margin: -.7rem 0 1.5rem; }
.reading-body { font-size: 1.0625rem; line-height: 1.95; }
.reading-body h1 { font-family: var(--serif); font-size: clamp(1.8rem, 3.2vw, 2.65rem); line-height: 1.35; font-weight: 600; margin: 0 0 1.7rem; letter-spacing: -.035em; }
h2, h3, h4, h5, h6 { line-height: 1.45; scroll-margin-top: 5.5rem; }
.reading-body h2 { font-size: 1.45rem; margin-top: 3rem; padding-bottom: .65rem; border-bottom: 1px solid var(--line); letter-spacing: -.015em; }
.reading-body h3 { font-size: 1.15rem; margin-top: 2.1rem; }
.reading-body p { margin: 1rem 0; }
.reading-body li + li { margin-top: .4rem; }
.reading-body ul, .reading-body ol { padding-left: 1.6rem; }
.reading-body strong { font-weight: 650; }
blockquote { margin: 1.5rem 0; padding: .3rem 1.15rem; border-left: 3px solid var(--accent); background: var(--accent-soft); color: var(--muted); font-size: .96em; }
code { background: var(--code); padding: .12em .32em; border-radius: .2rem; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: .85em; }
pre { padding: 1.15rem; overflow-x: auto; background: var(--code); border: 1px solid var(--line); border-radius: .35rem; line-height: 1.65; }
pre code { padding: 0; background: transparent; }
.table-scroll { max-width: 100%; overflow-x: auto; margin: 1.5rem 0; border: 1px solid var(--line); border-radius: .3rem; }
table { border-collapse: collapse; width: 100%; min-width: 34rem; font-size: .9375rem; line-height: 1.8; }
th, td { border-bottom: 1px solid var(--line); padding: .75rem .8rem; vertical-align: top; }
th { text-align: left; font-weight: 650; background: var(--accent-soft); }
tr:last-child td { border-bottom: 0; }
.align-right { text-align: right; }
.task-marker { display: inline-block; min-width: 1.35em; }
hr { border: 0; border-top: 1px solid var(--line); margin: 2.5rem 0; }
.anchor { display: block; position: relative; top: -5.5rem; visibility: hidden; }
.book-intro { padding: .7rem 0 2.1rem; }
.eyebrow { color: var(--accent); font-size: .7rem; letter-spacing: .15em; font-weight: 650; }
.book-tagline { line-height: 1.45; font-family: var(--serif); font-size: clamp(1.8rem, 3.2vw, 2.6rem); margin: 1rem 0; font-weight: 500; letter-spacing: -.025em; }
.book-intro p { color: var(--muted); font-size: .92rem; line-height: 1.8; max-width: 38rem; }
.start-reading { display: inline-block; margin-top: 1rem; padding: .65rem 1.15rem; background: var(--accent); color: var(--surface); border-radius: .25rem; text-decoration: none; font-size: .9rem; font-weight: 600; }
.collection-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; margin-bottom: 3rem; }
.collection-card { display: grid; gap: .4rem; align-content: start; padding: 1.05rem; background: var(--surface); border: 1px solid var(--line); border-radius: .3rem; text-decoration: none; color: var(--text); }
.collection-card:hover { border-color: var(--accent); }
.collection-number { color: var(--muted); font-size: .7rem; letter-spacing: .1em; }
.collection-card strong { font-size: .9rem; font-weight: 600; }
.collection-description { color: var(--muted); font-size: .77rem; line-height: 1.7; }
.reading-pager { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; border-top: 1px solid var(--line); padding-top: 1.5rem; margin-top: 3rem; }
.reading-pager a { display: flex; flex-direction: column; gap: .45rem; padding: 1rem; border: 1px solid var(--line); border-radius: .3rem; background: var(--surface); text-decoration: none; font-size: .9rem; }
.reading-pager a:hover { border-color: var(--accent); }
.reading-pager .next { grid-column: 2; text-align: right; }
.pager-label { color: var(--muted); font-size: .72rem; }
.reading-pager strong { font-weight: 550; }
.reading-end { text-align: center; margin-top: 1.7rem; font-size: .75rem; }
.site-footer { border-top: 1px solid var(--line); }
.footer-inner { max-width: 48rem; padding: 1.5rem; margin: auto; text-align: center; color: var(--muted); font-size: .73rem; }
.footer-inner p { margin: .25rem 0; }
.footer-inner nav { margin-top: .75rem; }
.mobile-navigation, .mobile-toc { display: none; }
summary { cursor: pointer; padding: .75rem .9rem; font-size: .8rem; color: var(--accent); font-weight: 550; }
@media (max-width: 76rem) {
  .reading-layout { grid-template-columns: 13rem minmax(0, 44rem); gap: 2rem; max-width: 67rem; }
  .outline-sidebar { display: none; }
  .mobile-toc { display: block; margin-bottom: 1.6rem; border: 1px solid var(--line); border-radius: .3rem; background: var(--surface); }
  .mobile-toc .reader-toc { padding: 0 .9rem .9rem; max-height: 20rem; overflow-y: auto; }
}
@media (max-width: 50rem) {
  .header-inner { padding: .7rem 1rem; }
  .header-note { display: none; }
  .site-title { gap: .5rem; font-size: .94rem; }
  .site-subtitle { font-size: .78rem; }
  .site-mark { width: 1.8rem; height: 2rem; font-size: 1.25rem; }
  .reading-layout { display: block; padding: 1.25rem 1.15rem 2.5rem; }
  .library-sidebar { display: none; }
  .mobile-navigation { display: block; background: var(--surface); border-bottom: 1px solid var(--line); }
  .mobile-navigation details { padding: 0 .3rem; }
  .mobile-navigation .library-nav, .mobile-navigation .chapter-nav { padding: .5rem .75rem; }
  .mobile-navigation .chapter-nav { max-height: 45vh; overflow-y: auto; }
  .mobile-navigation .sidebar-label { padding-left: 1rem; }
  .reading-meta { margin-bottom: 1.4rem; padding-bottom: .85rem; }
  .reading-body { font-size: 1.0625rem; line-height: 1.95; }
  .reading-body h1 { font-size: 1.85rem; }
  .reading-body h2 { font-size: 1.3rem; }
  .reading-pager { gap: .6rem; }
  .reading-pager a { padding: .75rem; font-size: .8rem; }
}
@media (max-width: 26rem) {
  .collection-grid { grid-template-columns: 1fr; }
  .reading-collection { max-width: 75%; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
@media print {
  :root { color-scheme: light; --background: white; --surface: white; --text: black; --muted: #333; --line: #aaa; --accent: #222; --accent-soft: #eee; --code: #eee; }
  .site-header, .library-sidebar, .outline-sidebar, .mobile-navigation, .mobile-toc, .reading-pager, .reading-end, .site-footer, .skip-link { display: none; }
  .reading-layout { display: block; padding: 0; }
  .content { max-width: none; }
  .reading-body { font-size: 10.5pt; }
  .table-scroll, pre { overflow: visible; }
  blockquote, .study-illustration { break-inside: avoid; }
  .reading-meta, .book-intro, .collection-grid { display: none; }
  table { min-width: 0; font-size: 8.5pt; }
  a { color: black; }
}
""".encode("utf-8")


# The only script: a local language switch. It makes no network request and
# stores nothing but the reader's chosen display mode in this browser.
LANG_JS = """\
(function () {
  "use strict";
  var KEY = "project-covenant-language";
  var MODES = ["zh", "en", "both"];
  var root = document.documentElement;
  function saved() { try { return window.localStorage.getItem(KEY); } catch (error) { return null; } }
  function remember(mode) { try { window.localStorage.setItem(KEY, mode); } catch (error) { return; } }
  function apply(mode) {
    if (MODES.indexOf(mode) < 0) { mode = "both"; }
    root.setAttribute("data-lang", mode);
    root.setAttribute("lang", mode === "en" ? "en" : "zh-Hans");
    var buttons = document.querySelectorAll("[data-lang-choice]");
    for (var index = 0; index < buttons.length; index += 1) {
      buttons[index].setAttribute("aria-pressed", String(buttons[index].getAttribute("data-lang-choice") === mode));
    }
  }
  root.classList.add("lang-ready");
  apply(saved());
  document.addEventListener("DOMContentLoaded", function () {
    apply(root.getAttribute("data-lang"));
    document.addEventListener("click", function (event) {
      var button = event.target && event.target.closest ? event.target.closest("[data-lang-choice]") : null;
      if (!button) { return; }
      var mode = button.getAttribute("data-lang-choice");
      apply(mode);
      remember(mode);
    });
  });
}());
""".encode("utf-8")


SITE_CSS += b"""
.study-illustration { display: block; max-width: 100%; width: auto; max-height: 36rem; height: auto; margin: 1.25rem auto; }
.map-viewport { display: block; width: 100%; max-width: 100%; overflow-x: auto; border: 1px solid var(--line); background: #fff; margin: 1.25rem 0; }
.map-viewport:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.study-map { display: block; min-width: 1100px; width: 100%; height: auto; max-width: none; }
@media print { .study-map { min-width: 0; width: 100%; max-height: 240mm; object-fit: contain; } .map-viewport { overflow: visible; border: 0; break-inside: avoid; } .study-illustration { max-height: 100mm; } }
"""

# Readability batch 3: keep table words whole, show when a wide table can
# scroll sideways, and balance short headings. CSS only; no script or remote asset.
SITE_CSS += b"""
:root { --scroll-shadow: rgba(41, 46, 41, .18); }
@media (prefers-color-scheme: dark) { :root { --scroll-shadow: rgba(0, 0, 0, .55); } }
th, td, th a, td a { overflow-wrap: break-word; word-break: normal; }
td.align-right, th.align-right { font-variant-numeric: tabular-nums; white-space: nowrap; }
.table-scroll {
  background:
    linear-gradient(to right, var(--background) 30%, transparent) left center / 2.5rem 100% no-repeat local,
    linear-gradient(to left, var(--background) 30%, transparent) right center / 2.5rem 100% no-repeat local,
    radial-gradient(farthest-side at 0 50%, var(--scroll-shadow), transparent) left center / .85rem 100% no-repeat scroll,
    radial-gradient(farthest-side at 100% 50%, var(--scroll-shadow), transparent) right center / .85rem 100% no-repeat scroll;
}
tbody tr:hover td { background: color-mix(in srgb, var(--accent-soft) 55%, transparent); }
.reading-body h1, .reading-body h2, .reading-body h3 { text-wrap: balance; }
.reading-body p, .reading-body li, blockquote { text-wrap: pretty; }
@media (max-width: 50rem) {
  table { font-size: .875rem; line-height: 1.7; }
  th, td { padding: .6rem .65rem; }
  blockquote { padding: .2rem .9rem; }
}
@media print { .table-scroll { background: none; } tbody tr:hover td { background: none; } }
"""

# Visual polish batch 4: figures and captions, calmer status notes, warmer
# headings and callouts. CSS only; no script, remote font, or remote image.
SITE_CSS += b"""
::selection { background: color-mix(in srgb, var(--accent) 22%, transparent); }
.reading-body a { text-decoration-color: color-mix(in srgb, var(--accent) 45%, transparent); text-decoration-thickness: .08em; }
.reading-body a:hover { text-decoration-color: var(--accent); }
.reading-body h2 { font-family: var(--serif); font-weight: 600; letter-spacing: -.01em; }
.reading-body h2::before { content: ""; display: block; width: 2.25rem; height: 3px; border-radius: 2px; background: var(--accent); margin-bottom: .85rem; opacity: .75; }
.reading-body h3 { color: color-mix(in srgb, var(--text) 82%, var(--accent)); }
.reading-body li::marker { color: var(--accent); }
blockquote { border-radius: 0 .55rem .55rem 0; padding: .55rem 1.2rem; }
blockquote strong:first-child { color: var(--accent); }
.reading-body > blockquote:first-of-type { background: transparent; border-left-width: 2px; padding: .15rem .9rem; font-size: .82rem; line-height: 1.7; }
.study-illustration { border-radius: .55rem; box-shadow: 0 1px 2px rgba(0, 0, 0, .08), 0 8px 24px rgba(41, 46, 41, .10); }
.study-art { display: block; width: 100%; max-width: 100%; height: auto; margin: 1.6rem auto .4rem; border-radius: 14px; box-shadow: 0 1px 2px rgba(0, 0, 0, .06), 0 10px 28px rgba(41, 46, 41, .10); }
p:has(> img.study-art, > img.study-illustration) + p { margin-top: .2rem; font-size: .8rem; line-height: 1.65; color: var(--muted); text-align: center; }
.collection-card { transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease; }
.collection-card:hover { box-shadow: 0 6px 18px rgba(41, 46, 41, .10); transform: translateY(-1px); }
.start-reading:hover { filter: brightness(1.08); }
hr { border: 0; height: 1px; background: linear-gradient(to right, transparent, var(--line), transparent); }
@media (prefers-color-scheme: dark) {
  .study-art, .study-illustration { box-shadow: 0 1px 2px rgba(0, 0, 0, .4); }
  .study-art { opacity: .94; }
}
@media (prefers-reduced-motion: reduce) { .collection-card { transition: none; } .collection-card:hover { transform: none; } }
p:has(> a[href="#week-index"]:first-child) { font-size: .8rem; line-height: 1.8; color: var(--muted); padding-top: .9rem; border-top: 1px dashed var(--line); }
p:has(> a[href="#week-index"]:first-child) a { text-decoration: none; padding: .15rem .1rem; }
p:has(> a[href="#week-index"]:first-child) a:hover { text-decoration: underline; }
@media print { .study-art { box-shadow: none; max-height: 90mm; width: auto; } .reading-body h2::before { display: none; } p:has(> a[href="#week-index"]:first-child) { display: none; } }
"""

# Language display: both languages by default; the local switch narrows it.
SITE_CSS += b"""
.l-en1, .l-zh1 { display: none; }
html[data-lang="en"] .l-zh, html[data-lang="en"] .l-sep, html[data-lang="en"] .l-bi, html[data-lang="en"] .l-zh1 { display: none; }
html[data-lang="zh"] .l-en, html[data-lang="zh"] .l-sep, html[data-lang="zh"] .l-bi, html[data-lang="zh"] .l-en1 { display: none; }
html[data-lang="en"] .l-en1, html[data-lang="zh"] .l-zh1 { display: inline; }
.lang-switch { display: none; }
html.lang-ready .lang-switch { display: inline-flex; flex: none; border: 1px solid var(--line); border-radius: 999px; padding: 2px; background: var(--background); }
.lang-switch button { font: inherit; font-size: .75rem; line-height: 1; padding: .45rem .7rem; border: 0; border-radius: 999px; background: transparent; color: var(--muted); cursor: pointer; }
.lang-switch button:hover { color: var(--accent); }
.lang-switch button[aria-pressed="true"] { background: var(--accent); color: var(--surface); }
.lang-switch button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.header-inner { gap: .75rem; }
.header-note { margin-left: auto; }
@media (max-width: 50rem) { .lang-switch button { padding: .4rem .55rem; } }
@media print { .lang-switch { display: none !important; } }
.home-art { display: block; width: 100%; max-width: 100%; height: auto; margin: 2rem 0 .5rem; border-radius: 14px; box-shadow: 0 1px 2px rgba(0, 0, 0, .06), 0 10px 28px rgba(41, 46, 41, .10); }
@media (max-width: 50rem) {
  .site-subtitle { display: none; }
  .site-title { min-width: 0; line-height: 1.2; }
  .header-inner { gap: .5rem; }
}
@media (max-width: 24rem) {
  .header-inner { padding: .6rem .75rem; gap: .4rem; }
  .site-title { gap: .4rem; font-size: .88rem; }
  .site-mark { width: 1.55rem; height: 1.75rem; font-size: 1.1rem; }
  .lang-switch button { padding: .38rem .42rem; font-size: .7rem; }
}
@media print { .home-art { display: none; } }
.guide-heading { margin: -1.4rem 0 .8rem; }
.guide-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(11.5rem, 1fr)); gap: .65rem; margin-bottom: 3rem; }
.guide-card { display: grid; gap: .3rem; align-content: start; padding: .85rem .95rem; background: var(--accent-soft); border: 1px solid var(--line); border-radius: 10px; text-decoration: none; color: var(--text); transition: border-color .15s ease, transform .15s ease; }
.guide-card:hover { border-color: var(--accent); transform: translateY(-1px); }
.guide-card strong { font-size: .88rem; font-weight: 600; }
@media (prefers-reduced-motion: reduce) { .guide-card { transition: none; } .guide-card:hover { transform: none; } }
@media print { .guide-heading, .guide-grid { display: none; } }
@media (prefers-color-scheme: dark) {
  .study-art, .study-illustration, .home-art { filter: brightness(.82) saturate(.92); }
}
@media print { .study-art, .study-illustration, .home-art { filter: none; } }
.reading-body > p:last-child:has(> a:first-child[href$="index.html"]) { margin-top: 2.6rem; font-size: .84rem; line-height: 1.9; color: var(--muted); }
.reading-body > p:last-child:has(> a:first-child[href$="index.html"]) a { color: var(--muted); text-decoration-color: var(--line); }
.reading-body > p:last-child:has(> a:first-child[href$="index.html"]) a:hover { color: var(--accent); text-decoration-color: currentColor; }
.hub-page ul:has(> li > a:only-child) { list-style: none; padding-left: 0; }
.hub-page li:has(> a:only-child) > a { display: block; padding: .65rem 1rem .65rem 1.1rem; border: 1px solid var(--line); border-left: 3px solid var(--accent); border-radius: 10px; background: var(--surface); color: var(--text); text-decoration: none; line-height: 1.6; transition: border-color .15s ease, background-color .15s ease; }
.hub-page li:has(> a:only-child) > a:hover { background: var(--accent-soft); border-color: var(--accent); }
.hub-page li:has(> a:only-child) + li { margin-top: .55rem; }
@media (prefers-reduced-motion: reduce) { .hub-page li > a { transition: none; } }
@media print { .hub-page li:has(> a:only-child) > a { border: 0; padding: 0; background: none; } }
"""
