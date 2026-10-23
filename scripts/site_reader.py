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
    "Bible_Timeline/Ten_Commandments_Bilingual.md",
    "Bible_Timeline/Names_of_God_Bilingual.md",
    "Bible_Timeline/Apostles_Creed_Bilingual.md",
    "Bible_Timeline/Feasts_of_the_Bible_Bilingual.md",
    "Bible_Timeline/Parables_of_Jesus_Bilingual.md",
    "Bible_Timeline/Miracles_of_Jesus_Bilingual.md",
    "Bible_Timeline/Sermon_on_the_Mount_Bilingual.md",
    "Bible_Timeline/Key_Passages_Bilingual.md",
    "Bible_Timeline/Prayers_in_the_Bible_Bilingual.md",
    "Bible_Timeline/Lords_Prayer_Bilingual.md",
    "Bible_Timeline/Psalms_for_Different_Times_Bilingual.md",
    "Bible_Timeline/52周圣经故事线_查经与史料阅读计划.md",
    "Bible_Timeline/Bible_Timeline_Cheat_Sheet.md",
)
COLLECTIONS = (
    ("Bible_Timeline", "Storyline | 圣经故事线", "Follow the story, then explore its context. | 先读故事线，再深入背景。", "Storyline | 故事线"),
    ("Bilingual_Notes", "Notes | 讲道与团契笔记", "Read draft sermon and fellowship notes. | 阅读讲道与团契笔记草稿。", "Notes | 笔记"),
    ("Book_Studies", "Book studies | 书籍研读", "Read with guides and source boundaries. | 带着导读和来源边界阅读。", "Books | 书籍"),
    ("Christian_Traditions", "Traditions | 基督教传统", "Explore historical traditions and their differences. | 了解历史传统及其差异。", "Traditions | 传统"),
    ("Bible_Translations", "Translations | 圣经译本", "Find access guides and reading notes. | 查找获取指南与阅读说明。", "Translations | 译本"),
    ("Maps", "Maps | 地图", "Read offline maps with bilingual labels. | 阅读带双语地名的离线地图。", "Maps | 地图"),
    ("Glossary", "Glossary | 词汇表", "Look up common words in plain language. | 用白话查找常见词语。", "Glossary | 词汇"),
)
ABOUT_PAGE = "ABOUT.md"
# The home page shows its topic-guide cards just before this README anchor.
HOME_GUIDES_BEFORE = "explore"


# Short beginner guides surfaced on the home page, in reading order.
QUICK_GUIDES = (
    ("Bible_Timeline/Bible_Reading_Toolkit_Bilingual.md", "Reading Toolkit | 读经工具箱", "Find a passage and read each kind of writing. | 查经文出处，读懂不同文体。", "assets/art/open-bible.svg", "An open Bible | 打开的圣经"),
    ("Bible_Timeline/Bible_People_Bilingual.md", "People | 圣经人物", "Who’s who, in story order. | 按故事顺序认识主要人物。", "assets/art/story-procession.svg", "People of the story | 故事中的人物"),
    ("Maps/Bible_Places_Bilingual.md", "Places | 圣经地名", "Key places, each linked to a map. | 重要地点，附地图链接。", "assets/art/parchment-map.svg", "An old map | 一幅旧地图"),
    ("Bible_Timeline/Bible_Covenants_Bilingual.md", "Covenants | 圣经中的约", "The five covenants that carry the story. | 贯穿故事的五个约。", "assets/art/ark-rainbow.svg", "A rainbow after the flood | 洪水之后的彩虹"),
    ("Bible_Timeline/Parables_of_Jesus_Bilingual.md", "Parables | 耶稣的比喻", "Nineteen parables and how to read them. | 十九个比喻及读法。", "assets/art/lost-sheep.svg", "The sheep that was found | 找回的羊"),
    ("Bible_Timeline/Key_Passages_Bilingual.md", "Key Passages | 值得熟悉的经文", "Thirty-six passages worth knowing well. | 三十六段值得熟悉的经文。", "assets/art/lamp-path.svg", "A lamp for the path | 脚前的灯"),
    ("Bible_Timeline/Prayers_in_the_Bible_Bilingual.md", "Prayers | 圣经中的祷告", "Twenty-one prayers to learn from. | 二十一篇可以学习的祷告。", "assets/art/incense-rising.svg", "Prayer like incense | 祷告如香"),
    ("Bible_Timeline/Psalms_for_Different_Times_Bilingual.md", "Psalms for Different Times | 不同处境中的诗篇", "A psalm for what you are going through. | 为当下处境找一篇诗篇。", "assets/art/lyre-dawn.svg", "A song at dawn | 黎明的诗歌"),
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


def _stacked_label(text: str) -> str:
    """A compact two-line label (Chinese over English) for the header navigation."""
    pair = _split_pair(html.escape(text))
    if not pair:
        return bilingual_label(text)
    english, chinese = pair
    return (f'<span class="l-zh" lang="{LANG_ZH}">{chinese}</span><span class="l-sep"> · </span>'
            f'<span class="l-en" lang="{LANG_EN}">{english}</span>')


def _nav_link(href: str, label: str, *, current: bool = False) -> str:
    attributes = ' aria-current="page"' if current else ""
    return f'<a href="{html.escape(href, quote=True)}"{attributes}>{_stacked_label(label)}</a>'


def _site_nav(source: str, output: str, page_map: dict[str, str]) -> str:
    links: list[str] = []
    current_folder = PurePosixPath(source).parent.as_posix()
    for directory, _, _, short in COLLECTIONS:
        hub = directory + "/README.md"
        if hub in page_map:
            links.append("<li>" + _nav_link(_href(output, page_map[hub]), short, current=current_folder == directory) + "</li>")
    if ABOUT_PAGE in page_map:
        links.append("<li>" + _nav_link(_href(output, page_map[ABOUT_PAGE]), "About | 关于", current=source == ABOUT_PAGE) + "</li>")
    if not links:
        return ""
    return '<nav class="site-nav" aria-label="Library | 资料导航"><ul>' + "".join(links) + "</ul></nav>"


def _library_nav(source: str, output: str, page_map: dict[str, str]) -> str:
    links = ["<li>" + _link(_href(output, page_map["README.md"]), "Home | 首页", current=source == "README.md") + "</li>"]
    for directory, label, _, _ in COLLECTIONS:
        hub = directory + "/README.md"
        if hub in page_map:
            links.append("<li>" + _link(_href(output, page_map[hub]), label, current=source == hub) + "</li>")
    if ABOUT_PAGE in page_map:
        links.append("<li>" + _link(_href(output, page_map[ABOUT_PAGE]), "About this library | 关于本资料库", current=source == ABOUT_PAGE) + "</li>")
    return '<nav class="library-nav" aria-label="Library | 资料导航"><ul>' + "\n".join(links) + "</ul></nav>"


def _chapter_list(source: str, output: str, page_map: dict[str, str], titles: dict[str, str]) -> str:
    ordered = collection_order(source, page_map)
    if not ordered:
        return ""
    links = "\n".join(
        "<li>" + _link(_href(output, page_map[path]), _title(path, titles), current=source == path) + "</li>"
        for path in ordered
    )
    return '<nav class="chapter-nav" aria-label="Collection contents | 栏目目录"><ol>' + links + "</ol></nav>"


def _collection_label(source: str) -> str | None:
    folder = PurePosixPath(source).parent.as_posix()
    return next((label for directory, label, _, _ in COLLECTIONS if directory == folder), None)


def _series(source: str, output: str, page_map: dict[str, str], titles: dict[str, str]) -> str:
    chapters = _chapter_list(source, output, page_map, titles)
    label = _collection_label(source)
    if not chapters or not label:
        return ""
    english, chinese = label.split(" | ", 1)
    count = len(collection_order(source, page_map))
    summary = bilingual_label(f"All {count} pages in {english} | {chinese}全部 {count} 篇")
    return f'<details class="series"><summary>{summary}</summary>{chapters}</details>'


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


def _guide_grid(output: str, page_map: dict[str, str], guide_art: frozenset[str]) -> str:
    guides = []
    for path, label, description, art_path, art_alt in QUICK_GUIDES:
        if path not in page_map:
            continue
        href = html.escape(_href(output, page_map[path]), quote=True)
        thumb = ""
        if art_path in guide_art:
            thumb = '<img class="guide-thumb" src="' + html.escape(_href(output, art_path), quote=True) + '" alt="' + html.escape(art_alt, quote=True) + '">'
        guides.append(f'<a class="guide-card" href="{href}">{thumb}<strong>{bilingual_label(label)}</strong><span class="guide-description">{bilingual_label(description)}</span></a>')
    if not guides:
        return ""
    return ('<div class="home-section" aria-label="Topic guides | 专题导读"><div class="section-kicker">'
            + bilingual_label("Topic guides | 专题导读") + '</div><p class="section-intro">'
            + bilingual_label("Short guides you can read in one sitting. | 一次就能读完的短篇导读。")
            + '</p><nav class="guide-grid" aria-label="Topic guides | 专题导读">' + "\n".join(guides) + "</nav></div>")


def _home_actions(output: str, page_map: dict[str, str]) -> str:
    first = next((path for path in STORY_ROUTE[1:] if path in page_map), None)
    if not first:
        return ""
    start = _link(_href(output, page_map[first]), "Start reading | 开始阅读 →", css="start-reading")
    return ('<div class="home-actions">' + start + '<p class="home-hint"><span class="l-en" lang="en">Use the switch at the top to read in Chinese, in English, or in both.</span>'
            '<span class="l-sep"> </span><span class="l-zh" lang="zh-Hans">可以用页面顶部的按钮切换中文、英文或中英对照。</span></p></div>')


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
    chinese_characters = len(re.findall(r"[㐀-鿿]", text))
    minutes = max(english_words / 200, chinese_characters / 350)
    if minutes < 3 and not include_short:
        return ""
    return f"{max(1, math.ceil(minutes))} min read | 约 {max(1, math.ceil(minutes))} 分钟"


# --- Article shaping ----------------------------------------------------------
# Repository Markdown keeps its GitHub-friendly status lines, route tables,
# captions, and back links. The website moves or drops only these exact,
# repeated reading aids; every id they carried is kept as an empty anchor.

_ANCHOR = r'<a id="[^"]*" class="anchor" aria-hidden="true"></a>\n'
_STATUS = re.compile(
    r'<blockquote>\n<p><span class="l-en" lang="en">Status: (?P<state>[A-Za-z]+) \((?P<en>[^()<]*)\)</span>'
    r'<span class="l-sep"> \| </span><span class="l-zh" lang="zh-Hans">状态：(?P=state)（(?P<zh>[^（）<]*)）</span></p>\n</blockquote>\n'
)
_H1 = re.compile(r"<h1(?: [^>]*)?>.*?</h1>\n", re.S)
_BLOCKQUOTE = re.compile(r"<blockquote>\n(?P<inner>(?:<p>.*?</p>\n)+)</blockquote>\n", re.S)
_LANGUAGE_STATUS = ("Language status", "语言状态")
_FULLY_BILINGUAL = "Fully bilingual, paragraph by paragraph."
_ILLUSTRATION_NOTE = re.compile(
    r'<p><em>Original illustration for this library; not historical evidence\. / 本资料库原创插画，不作为历史证据。</em> '
    r'<a href="[^"]*CREDITS\.html#original-illustrations">About the illustrations \| 插画说明</a></p>\n'
)
_ROUTE_GUIDE = re.compile(
    r'(?P<anchors>(?:' + _ANCHOR + r')*)<h2 id="(?P<id>route-guide[^"]*)">.*?</h2>\n'
    r'<div class="table-scroll">\n(?P<table><table>.*?</table>)\n</div>\n', re.S
)
_BACK_LINKS = re.compile(r'<p>(?P<links>(?:<a href="[^"]*">[^<]*</a>(?: · )?)+)</p>\n?$')
_LABEL_PARAGRAPH = re.compile(r'<p>(<span class="l-bi"><strong>[^<]*</strong></span>.*?)</p>', re.S)


def _anchor(identifier: str) -> str:
    return f'<a id="{identifier}" class="anchor" aria-hidden="true"></a>\n'


@dataclass
class ShapedArticle:
    anchors: str = ""
    title: str = ""
    lede: str = ""
    status: tuple[str, str, str] | None = None
    notes: str = ""
    body: str = ""


def _drop_route_guides(body: str) -> str:
    def replace(match: re.Match[str]) -> str:
        hrefs = re.findall(r'href="([^"]*)"', match.group("table"))
        if not hrefs or not all(href.startswith("#") for href in hrefs):
            return match.group(0)
        return match.group("anchors") + _anchor(match.group("id"))
    return _ROUTE_GUIDE.sub(replace, body)


def _is_language_status(inner: str) -> bool:
    paragraphs = re.findall(r"<p>(.*?)</p>", inner, re.S)
    return bool(paragraphs) and all(
        any(marker in paragraph[:400] for marker in _LANGUAGE_STATUS) for paragraph in paragraphs
    )


def shape_article(body: str) -> ShapedArticle:
    """Split trusted renderer output into a reading header and the article body."""
    shaped = ShapedArticle()
    rest = _ILLUSTRATION_NOTE.sub("", body)
    rest = _drop_route_guides(rest)
    back = _BACK_LINKS.search(rest)
    if back and re.search(r'">(?:Back to|Return to) ', back.group("links")):
        rest = rest[:back.start()].rstrip("\n") + "\n" if rest[:back.start()].strip() else rest[:back.start()]

    title = _H1.search(rest)
    if not title:
        shaped.body = rest
        return shaped
    before = rest[:title.start()]
    status = _STATUS.search(before)
    if status:
        shaped.status = (status.group("state"), status.group("en"), status.group("zh"))
        before = before[:status.start()] + before[status.end():]
    if re.fullmatch(r"(?:" + _ANCHOR + r")*", before) is None:
        # Unexpected content before the title: keep the page exactly as written.
        shaped.status = None
        shaped.body = rest
        return shaped
    shaped.anchors = before
    shaped.title = title.group(0)
    after = rest[title.end():]

    if shaped.status is None:
        status = _STATUS.match(after)
        if status:
            shaped.status = (status.group("state"), status.group("en"), status.group("zh"))
            after = after[status.end():]

    lede_anchors = re.match(r"(?:" + _ANCHOR + r")*", after)
    lede_quote = _BLOCKQUOTE.match(after, lede_anchors.end())
    if lede_quote and not _is_language_status(lede_quote.group("inner")):
        shaped.anchors += lede_anchors.group(0)
        inner = _LABEL_PARAGRAPH.sub(r'<p class="lede-label">\1</p>', lede_quote.group("inner"), count=1)
        shaped.lede = '<div class="lede">\n' + inner + "</div>\n"
        after = after[lede_quote.end():]

    first_section = re.search(r"<h2[ >]", after)
    limit = first_section.start() if first_section else len(after)
    head, tail = after[:limit], after[limit:]
    for match in list(_BLOCKQUOTE.finditer(head))[::-1]:
        if not _is_language_status(match.group("inner")):
            continue
        if _FULLY_BILINGUAL not in match.group("inner"):
            shaped.notes = '<div class="page-note">\n' + match.group("inner") + "</div>\n" + shaped.notes
        head = head[:match.start()] + head[match.end():]
    shaped.body = head + tail
    return shaped


def _status_badge(status: tuple[str, str, str] | None) -> str:
    if not status:
        return ""
    state, english, chinese = status
    return (f'<span class="status-badge">{html.escape(state)}</span>'
            f'<span class="status-note">{bilingual_label(english + " | " + chinese)}</span>')


def render_page(source: str, output: str, title: str, body: str,
                page_map: dict[str, str], titles: dict[str, str], css_path: str,
                home_art: str | None = None, guide_art: frozenset[str] = frozenset()) -> bytes:
    """Compose reading navigation around trusted renderer output."""
    if "README.md" not in page_map or page_map.get(source) != output:
        raise ValueError("READER_PAGE_MAP_INVALID")
    is_home = source == "README.md"
    is_hub = source.rsplit("/", 1)[-1] == "README.md"
    shaped = shape_article(body)
    toc = _toc(shaped.body)
    home = _href(output, page_map["README.md"])
    ordered = collection_order(source, page_map)

    kicker = ""
    collection = _collection_label(source)
    if is_home:
        kicker = '<span class="kicker-label">' + bilingual_label("A bilingual Bible study library | 中英双语查经资料库") + "</span>"
    elif collection:
        hub = PurePosixPath(source).parent.as_posix() + "/README.md"
        kicker = '<span class="kicker-label">' + (_link(_href(output, page_map[hub]), collection) if hub in page_map and hub != source else bilingual_label(collection)) + "</span>"
        if source in ordered and len(ordered) > 1:
            kicker += f'<span class="kicker-position">{ordered.index(source) + 1:02d} / {len(ordered):02d}</span>'
    meta_parts = []
    badge = _status_badge(shaped.status)
    if badge:
        meta_parts.append('<span class="meta-item">' + badge + "</span>")
    estimate = reading_time(shaped.body, include_short=is_core_study(source))
    if estimate:
        meta_parts.append('<span class="reading-time">' + bilingual_label(estimate) + "</span>")
    meta = '<div class="article-meta">' + "".join(meta_parts) + "</div>\n" if meta_parts else ""
    header = ""
    if shaped.title or kicker or meta:
        header = ('<header class="article-header">\n'
                  + (f'<div class="article-kicker">{kicker}</div>\n' if kicker else "")
                  + shaped.anchors + shaped.title + shaped.lede + meta + shaped.notes
                  + (_home_actions(output, page_map) if is_home else "")
                  + "</header>\n")
    article_body = shaped.body
    if is_home:
        art = ""
        if home_art:
            art = ('<p class="home-figure"><img class="home-art" src="' + html.escape(_href(output, home_art), quote=True)
                   + '" alt="The Bible as a library of 66 books on two shelves | 两层书架上的 66 卷圣经"></p>\n')
        guides = _guide_grid(output, page_map, guide_art)
        marker = article_body.find(_anchor(HOME_GUIDES_BEFORE))
        if guides and marker >= 0:
            article_body = article_body[:marker] + guides + "\n" + article_body[marker:]
        elif guides:
            article_body += guides
        article_body = art + article_body

    mobile_toc = '<details class="mobile-toc"><summary>' + bilingual_label("On this page | 本页目录") + '</summary>' + toc + '</details>\n' if toc else ""
    right_toc = '<aside class="outline-sidebar"><div class="sidebar-label">' + bilingual_label("On this page | 本页目录") + '</div>' + toc + '</aside>' if toc else ""
    footer_links = []
    for path, label in ((ABOUT_PAGE, "About | 关于"), ("CREDITS.md", "Credits | 署名与来源"),
                        ("PUBLICATION_POLICY.md", "Privacy | 隐私与发布"), ("LICENSE.md", "Licensing | 授权说明")):
        if path in page_map:
            footer_links.append(_link(_href(output, page_map[path]), label))
    illustration_note = ""
    if "CREDITS.md" in page_map:
        illustration_note = ('<p>' + bilingual_label("Illustrations are original to this library and are not historical evidence. | 插画为本资料库原创，不作为历史证据。") + "</p>")
    article_class = "reading-body hub-page" if is_hub else "reading-body"
    if is_home:
        article_class = "reading-body hub-page home-page"
    menu_chapters = _chapter_list(source, output, page_map, titles)
    menu_chapters = ('<div class="sidebar-label">' + bilingual_label("In this collection | 本栏篇目") + "</div>" + menu_chapters) if menu_chapters else ""
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
<a class="site-title" href="{html.escape(home, quote=True)}"><span class="site-mark" aria-hidden="true">C</span><span class="site-name">Project Covenant</span><span class="site-subtitle">圣约计划</span></a>
{_site_nav(source, output, page_map)}
<div class="lang-switch" role="group" aria-label="Language | 语言"><button type="button" data-lang-choice="zh" aria-pressed="false">中文</button><button type="button" data-lang-choice="en" aria-pressed="false">EN</button><button type="button" data-lang-choice="both" aria-pressed="false">中英</button></div>
</div></header>
<div class="mobile-navigation"><details><summary>{bilingual_label("Menu | 菜单")}</summary>{_library_nav(source, output, page_map)}{menu_chapters}</details></div>
<div class="reading-layout{' has-outline' if toc else ''}">
<main id="main-content" class="content" tabindex="-1">
<article class="{article_class}">
{header}{mobile_toc}{article_body}
</article>
{_pager(source, output, page_map, titles)}
{_series(source, output, page_map, titles)}
<div class="reading-end"><a href="#main-content">{bilingual_label("Back to top | 返回页首 ↑")}</a></div>
</main>
{right_toc}
</div>
<footer class="site-footer"><div class="footer-inner"><p class="footer-title"><span class="site-mark" aria-hidden="true">C</span>Project Covenant · 圣约计划</p>{illustration_note}<p>{bilingual_label("No account, no tracking, no remote assets. | 无需账号，不追踪阅读，不加载远程资源。")}</p><nav aria-label="About this site | 关于本站">{' · '.join(footer_links)}</nav></div></footer>
</body>
</html>
'''
    return document.encode("utf-8")


SITE_CSS = """\
:root {
  color-scheme: light dark;
  --background: #faf8f3; --surface: #ffffff; --raised: #f3f0e8; --text: #22261f;
  --muted: #696f63; --faint: #8c9186; --line: #e5e1d6; --accent: #3e6a48;
  --accent-soft: #e8efe4; --code: #f0ede4; --max: 80rem; --measure: 42rem;
  --shadow: 0 1px 2px rgba(34, 38, 31, .06), 0 10px 30px rgba(34, 38, 31, .08);
  --scroll-shadow: rgba(34, 38, 31, .16);
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", system-ui, sans-serif;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Noto Serif", "DejaVu Serif", "Songti SC", "Noto Serif CJK SC", "Source Han Serif SC", STSong, SimSun, serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root { --background: #151916; --surface: #1c211d; --raised: #222823; --text: #e3e7de;
    --muted: #a4ae9f; --faint: #7f8a7b; --line: #303932; --accent: #a8cf9a;
    --accent-soft: #243326; --code: #252c26;
    --shadow: 0 1px 2px rgba(0, 0, 0, .4); --scroll-shadow: rgba(0, 0, 0, .55); }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 5.5rem; -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--background); color: var(--text); font-family: var(--sans);
  font-size: 1rem; line-height: 1.75; -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
::selection { background: color-mix(in srgb, var(--accent) 24%, transparent); }
a { color: var(--accent); text-underline-offset: .22em; overflow-wrap: anywhere; }
a:focus-visible, summary:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 4px; }
.skip-link { position: absolute; left: -9999px; top: .5rem; z-index: 30; background: var(--surface); padding: .6rem 1rem; }
.skip-link:focus { left: 1rem; }

/* Header */
.site-header { position: sticky; top: 0; z-index: 10; background: color-mix(in srgb, var(--background) 92%, transparent); backdrop-filter: saturate(1.4) blur(10px); -webkit-backdrop-filter: saturate(1.4) blur(10px); border-bottom: 1px solid var(--line); }
.header-inner { max-width: var(--max); margin: auto; padding: .6rem 1.5rem; display: flex; align-items: center; gap: 1.25rem; min-height: 3.75rem; }
.site-title { display: flex; align-items: center; gap: .6rem; color: var(--text); text-decoration: none; flex: none; line-height: 1.2; }
.site-mark { display: inline-grid; place-items: center; width: 1.85rem; height: 2.1rem; border: 1.5px solid var(--accent); border-radius: 2px 7px 7px 2px; color: var(--accent); font: 1.3rem/1 var(--serif); flex: none; }
.site-name { font-weight: 650; letter-spacing: -.015em; }
.site-subtitle { color: var(--muted); font-size: .85rem; padding-left: .6rem; border-left: 1px solid var(--line); }
.site-nav { flex: 1; min-width: 0; overflow-x: auto; scrollbar-width: none; }
.site-nav ul { display: flex; justify-content: center; gap: .15rem; list-style: none; margin: 0; padding: 0; }
.site-nav a { display: flex; flex-direction: column; align-items: center; padding: .3rem .65rem; border-radius: .5rem; color: var(--muted); text-decoration: none; font-size: .86rem; line-height: 1.3; white-space: nowrap; }
.site-nav a .l-sep { display: none; }
.site-nav a .l-en { font-size: .68rem; letter-spacing: .02em; color: var(--faint); }
html[data-lang="en"] .site-nav a .l-en { font-size: .84rem; color: inherit; }
.site-nav a:hover { color: var(--text); background: var(--raised); }
.site-nav a[aria-current="page"] { color: var(--accent); font-weight: 600; }
.site-nav a[aria-current="page"] .l-en { color: var(--accent); }
.lang-switch { display: none; }
html.lang-ready .lang-switch { display: inline-flex; flex: none; margin-left: auto; border: 1px solid var(--line); border-radius: 999px; padding: 2px; background: var(--surface); }
.lang-switch button { font: inherit; font-size: .75rem; line-height: 1; padding: .45rem .7rem; border: 0; border-radius: 999px; background: transparent; color: var(--muted); cursor: pointer; }
.lang-switch button:hover { color: var(--accent); }
.lang-switch button[aria-pressed="true"] { background: var(--accent); color: var(--surface); }

/* Menu for narrow screens */
.mobile-navigation { display: none; background: var(--surface); border-bottom: 1px solid var(--line); }
.mobile-navigation details { max-width: var(--max); margin: auto; padding: 0 .4rem; }
.mobile-navigation .library-nav, .mobile-navigation .chapter-nav { padding: .25rem .8rem .8rem; }
.mobile-navigation .chapter-nav { max-height: 45vh; overflow-y: auto; }
.mobile-navigation .sidebar-label { padding: .6rem 1.2rem 0; border-top: 1px solid var(--line); }
summary { cursor: pointer; padding: .75rem .9rem; font-size: .85rem; color: var(--accent); font-weight: 600; }
.library-nav ul, .chapter-nav ol, .reader-toc ul { padding: 0; list-style: none; margin: 0; }
.library-nav a, .chapter-nav a { display: block; padding: .45rem .7rem; border-radius: .45rem; color: var(--text); text-decoration: none; font-size: .9rem; line-height: 1.55; }
.chapter-nav a { color: var(--muted); font-size: .84rem; }
.library-nav a:hover, .chapter-nav a:hover { background: var(--raised); }
.library-nav a[aria-current="page"], .chapter-nav a[aria-current="page"] { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
.sidebar-label { color: var(--faint); font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 650; margin: 0 0 .7rem; }

/* Layout */
.reading-layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, var(--measure)) minmax(0, 1fr); column-gap: 3.5rem; max-width: var(--max); margin: 0 auto; padding: 3rem 1.5rem 4rem; align-items: start; }
.content { grid-column: 2; min-width: 0; outline: none; overflow-wrap: anywhere; }
.outline-sidebar { grid-column: 3; position: sticky; top: 6rem; max-width: 15rem; max-height: calc(100dvh - 8rem); overflow-y: auto; scrollbar-width: thin; padding: .2rem 0 1rem; }
.reader-toc a { display: block; padding: .32rem 0 .32rem .85rem; color: var(--muted); font-size: .8rem; line-height: 1.55; text-decoration: none; border-left: 1px solid var(--line); }
.reader-toc a:hover { color: var(--accent); border-left-color: var(--accent); }
.mobile-toc { display: none; }

/* Article header */
.article-header { margin: 0 0 2.5rem; }
.article-kicker { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; font-size: .8rem; color: var(--muted); letter-spacing: .02em; margin-bottom: 1.1rem; }
.article-kicker a { color: var(--accent); text-decoration: none; font-weight: 600; }
.article-kicker a:hover { text-decoration: underline; }
.kicker-position { font-variant-numeric: tabular-nums; letter-spacing: .1em; color: var(--faint); white-space: nowrap; }
.reading-body h1 { font-family: var(--serif); font-size: clamp(2rem, 4.2vw, 2.85rem); line-height: 1.22; font-weight: 600; letter-spacing: -.02em; margin: 0 0 1.25rem; text-wrap: balance; }
.lede { font-size: 1.12rem; line-height: 1.8; color: var(--muted); margin: 0 0 1.4rem; }
.lede p { margin: 0 0 .7rem; }
.lede p.lede-label { font-size: .74rem; letter-spacing: .1em; text-transform: uppercase; color: var(--accent); margin-bottom: .45rem; }
.lede p.lede-label strong { font-weight: 650; }
.article-meta { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem 1.1rem; padding: .9rem 0 0; border-top: 1px solid var(--line); color: var(--muted); font-size: .8rem; line-height: 1.6; }
.meta-item, .reading-time { display: inline-flex; align-items: baseline; gap: .5rem; flex-wrap: wrap; }
.status-badge { display: inline-block; padding: .05rem .5rem; border-radius: 999px; border: 1px solid color-mix(in srgb, #b07a1d 55%, transparent); color: #8a5d0f; background: color-mix(in srgb, #e9b44c 16%, transparent); font-size: .7rem; font-weight: 650; letter-spacing: .04em; }
.page-note { margin-top: .8rem; color: var(--muted); font-size: .8rem; line-height: 1.65; }
.page-note p { margin: .2rem 0; }
.page-note strong { font-weight: 600; }

/* Body text */
.reading-body { font-size: 1.0625rem; line-height: 1.9; }
.reading-body p { margin: 0 0 1.25rem; }
.reading-body h2, .reading-body h3, .reading-body h4 { scroll-margin-top: 5.5rem; text-wrap: balance; }
.reading-body h2 { font-family: var(--serif); font-size: 1.6rem; line-height: 1.35; font-weight: 600; letter-spacing: -.01em; margin: 3.4rem 0 1.1rem; }
.reading-body h3 { font-size: 1.18rem; line-height: 1.5; font-weight: 650; margin: 2.4rem 0 .8rem; }
.reading-body h4, .reading-body h5, .reading-body h6 { font-size: 1rem; font-weight: 650; margin: 1.8rem 0 .6rem; }
.reading-body p, .reading-body li { text-wrap: pretty; }
.reading-body ul, .reading-body ol { padding-left: 1.4rem; margin: 0 0 1.4rem; }
.reading-body li { padding-left: .2rem; }
.reading-body li + li { margin-top: .65rem; }
.reading-body li::marker { color: var(--accent); }
.reading-body ol > li::marker { font-weight: 600; font-variant-numeric: tabular-nums; }
.reading-body strong { font-weight: 650; }
.reading-body a { text-decoration-color: color-mix(in srgb, var(--accent) 40%, transparent); text-decoration-thickness: .07em; }
.reading-body a:hover { text-decoration-color: var(--accent); }
blockquote { margin: 1.8rem 0; padding: 1rem 1.25rem; border-left: 3px solid var(--accent); border-radius: 0 .6rem .6rem 0; background: var(--raised); font-size: .97em; }
blockquote p:last-child { margin-bottom: 0; }
blockquote strong:first-child { color: var(--accent); }
code { background: var(--code); padding: .1em .35em; border-radius: .3rem; font-family: var(--mono); font-size: .86em; }
pre { padding: 1.1rem 1.2rem; overflow-x: auto; background: var(--code); border-radius: .6rem; line-height: 1.6; font-size: .9rem; }
pre code { padding: 0; background: transparent; }
hr { border: 0; height: 1px; background: var(--line); margin: 3rem auto; width: 40%; }
.anchor { display: block; position: relative; top: -5.5rem; visibility: hidden; }
.task-marker { display: inline-block; min-width: 1.35em; }

/* Tables */
.table-scroll { max-width: 100%; overflow-x: auto; margin: 1.8rem 0;
  background:
    linear-gradient(to right, var(--background) 30%, transparent) left center / 2.5rem 100% no-repeat local,
    linear-gradient(to left, var(--background) 30%, transparent) right center / 2.5rem 100% no-repeat local,
    radial-gradient(farthest-side at 0 50%, var(--scroll-shadow), transparent) left center / .85rem 100% no-repeat scroll,
    radial-gradient(farthest-side at 100% 50%, var(--scroll-shadow), transparent) right center / .85rem 100% no-repeat scroll; }
table { border-collapse: collapse; width: 100%; min-width: 32rem; font-size: .92rem; line-height: 1.7; }
th, td { padding: .7rem .75rem; vertical-align: top; text-align: left; border-bottom: 1px solid var(--line); overflow-wrap: break-word; word-break: normal; }
th { font-size: .8rem; font-weight: 650; color: var(--muted); letter-spacing: .02em; border-bottom: 1.5px solid color-mix(in srgb, var(--text) 30%, transparent); }
th:first-child, td:first-child { padding-left: 0; }
th:last-child, td:last-child { padding-right: 0; }
.align-right, td.align-right, th.align-right { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tbody tr:hover td { background: color-mix(in srgb, var(--accent-soft) 45%, transparent); }

/* Figures */
.study-art, .home-art { display: block; width: 100%; max-width: 100%; height: auto; margin: 2rem auto; border-radius: 14px; box-shadow: var(--shadow); }
.study-illustration { display: block; max-width: 100%; width: auto; max-height: 36rem; height: auto; margin: 1.8rem auto; border-radius: 10px; box-shadow: var(--shadow); }
p:has(> img.study-art, > img.study-illustration) + p:has(> em:first-child) { margin-top: -1.2rem; font-size: .8rem; line-height: 1.65; color: var(--muted); text-align: center; }
.map-viewport { display: block; width: 100%; max-width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: #fff; margin: 1.8rem 0; }
.map-viewport:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.study-map { display: block; min-width: 1100px; width: 100%; height: auto; max-width: none; }

/* Hub pages: link lists read as a table of contents */
.hub-page ul:has(> li > a:only-child) { list-style: none; padding-left: 0; }
.hub-page li:has(> a:only-child) { list-style: none; padding-left: 0; }
.hub-page li + li:has(> a:only-child) { margin-top: 0; }
.hub-page li > a:only-child { display: block; padding: .8rem .2rem; border-bottom: 1px solid var(--line); color: var(--text); text-decoration: none; line-height: 1.55; }
.hub-page li:first-child > a:only-child { border-top: 1px solid var(--line); }
.hub-page li > a:only-child:hover { color: var(--accent); background: color-mix(in srgb, var(--accent-soft) 45%, transparent); }
.hub-page li > a:only-child::after { content: " →"; color: var(--faint); }

/* Home */
.home-page .article-header { margin-bottom: 1rem; }
.home-page h1 { font-size: clamp(2.3rem, 5.5vw, 3.4rem); }
.home-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .8rem 1.2rem; margin-top: 1.6rem; }
.home-hint { margin: 0; color: var(--muted); font-size: .82rem; line-height: 1.6; max-width: 26rem; }
.start-reading { display: inline-block; padding: .7rem 1.25rem; background: var(--accent); color: var(--surface); border-radius: 999px; text-decoration: none; font-size: .92rem; font-weight: 600; }
.start-reading:hover { filter: brightness(1.08); }
.reading-body a.start-reading { color: var(--surface); text-decoration: none; }
.home-figure { margin: 0 0 2rem; }
.home-section { margin: 3.2rem 0; }
.section-kicker { font-family: var(--serif); font-size: 1.6rem; font-weight: 600; line-height: 1.35; }
.section-intro { color: var(--muted); font-size: .95rem; }
.guide-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
.guide-card { display: grid; gap: .3rem; align-content: start; padding: .8rem .8rem 1rem; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; text-decoration: none; color: var(--text); transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease; }
.reading-body a.guide-card { color: var(--text); text-decoration: none; }
.guide-card:hover { border-color: color-mix(in srgb, var(--accent) 50%, var(--line)); box-shadow: var(--shadow); transform: translateY(-2px); }
.guide-card strong { font-size: .98rem; font-weight: 650; line-height: 1.45; margin-top: .35rem; }
.guide-description { color: var(--muted); font-size: .84rem; line-height: 1.6; }
.guide-thumb { display: block; width: 100%; height: auto; aspect-ratio: 2 / 1; object-fit: cover; border-radius: 9px; }

/* End of article */
.reading-pager { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--line); }
.reading-pager a { display: flex; flex-direction: column; gap: .35rem; padding: 1rem 1.1rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); text-decoration: none; color: var(--text); font-size: .92rem; line-height: 1.5; transition: border-color .15s ease; }
.reading-pager a:hover { border-color: var(--accent); }
.reading-pager .next { grid-column: 2; text-align: right; }
.pager-label { color: var(--faint); font-size: .74rem; letter-spacing: .04em; }
.reading-pager strong { font-weight: 600; }
.series { margin-top: 1rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
.series .chapter-nav { padding: 0 .6rem .8rem; max-height: 26rem; overflow-y: auto; }
.reading-end { text-align: center; margin-top: 2rem; font-size: .8rem; }
.reading-end a { color: var(--muted); text-decoration: none; }
.site-footer { border-top: 1px solid var(--line); background: var(--raised); }
.footer-inner { max-width: var(--measure); padding: 2.2rem 1.5rem 2.6rem; margin: auto; text-align: center; color: var(--muted); font-size: .8rem; line-height: 1.7; }
.footer-inner p { margin: .3rem 0; }
.footer-title { display: flex; justify-content: center; align-items: center; gap: .55rem; color: var(--text); font-weight: 600; font-size: .9rem; margin-bottom: .8rem !important; }
.footer-title .site-mark { width: 1.4rem; height: 1.6rem; font-size: 1rem; }
.footer-inner nav { margin-top: .9rem; }
.footer-inner nav a { color: var(--muted); }

/* Responsive */
@media (max-width: 82rem) {
  .reading-layout { grid-template-columns: minmax(0, 1fr) minmax(0, var(--measure)) minmax(0, 1fr); column-gap: 2rem; }
  .reading-layout.has-outline { grid-template-columns: minmax(0, 1fr) minmax(0, var(--measure)) minmax(11rem, 13rem); }
  .reading-layout.has-outline .content { grid-column: 2; }
}
@media (max-width: 68rem) {
  .reading-layout, .reading-layout.has-outline { display: block; max-width: calc(var(--measure) + 3rem); }
  .outline-sidebar { display: none; }
  .mobile-toc { display: block; margin: 0 0 2.2rem; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
  .mobile-toc .reader-toc { padding: 0 1rem 1rem; max-height: 22rem; overflow-y: auto; }
  .site-nav { display: none; }
  .mobile-navigation { display: block; }
}
@media (max-width: 40rem) {
  .header-inner { padding: .5rem 1rem; gap: .6rem; min-height: 3.4rem; }
  .site-subtitle { display: none; }
  .site-name { font-size: .95rem; }
  .site-mark { width: 1.65rem; height: 1.9rem; font-size: 1.15rem; }
  .lang-switch button { padding: .42rem .55rem; }
  .reading-layout, .reading-layout.has-outline { padding: 1.6rem 1.15rem 3rem; }
  .reading-body { font-size: 1.0625rem; line-height: 1.85; }
  .reading-body h1 { font-size: 1.8rem; }
  .home-page h1 { font-size: 2.2rem; }
  .reading-body h2 { font-size: 1.38rem; margin-top: 2.8rem; }
  .lede { font-size: 1.04rem; }
  blockquote { padding: .85rem 1rem; margin-left: 0; margin-right: 0; }
  table { font-size: .87rem; line-height: 1.65; }
  th, td { padding: .6rem .6rem; }
  .guide-grid { grid-template-columns: 1fr; gap: .7rem; }
  .guide-card { grid-template-columns: 5.25rem 1fr; column-gap: .9rem; padding: .7rem; }
  .guide-thumb { grid-row: span 2; aspect-ratio: 1; }
  .guide-card strong { margin-top: 0; }
  .reading-pager { gap: .6rem; }
  .reading-pager a { padding: .8rem; font-size: .84rem; }
  .article-kicker { font-size: .76rem; }
}
@media (max-width: 24rem) {
  .header-inner { padding: .5rem .7rem; gap: .4rem; }
  .site-name { font-size: .86rem; }
  .lang-switch button { padding: .38rem .42rem; font-size: .7rem; }
}
@media (prefers-color-scheme: dark) {
  .status-badge { color: #e8c37a; border-color: color-mix(in srgb, #e8c37a 45%, transparent); background: color-mix(in srgb, #e8c37a 10%, transparent); }
  .study-art, .study-illustration, .home-art, .guide-thumb { filter: brightness(.84) saturate(.92); }
  .site-header { background: color-mix(in srgb, var(--background) 88%, transparent); }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .guide-card, .reading-pager a { transition: none; }
  .guide-card:hover { transform: none; }
}
@media print {
  :root { color-scheme: light; --background: white; --surface: white; --raised: white; --text: black; --muted: #333; --faint: #555; --line: #aaa; --accent: #222; --accent-soft: #eee; --code: #eee; }
  .site-header, .outline-sidebar, .mobile-navigation, .mobile-toc, .reading-pager, .series, .reading-end, .site-footer, .skip-link, .lang-switch, .home-actions, .home-section { display: none !important; }
  .reading-layout { display: block; padding: 0; }
  .reading-body { font-size: 10.5pt; }
  .table-scroll { overflow: visible; background: none; }
  pre { overflow: visible; }
  blockquote, .study-illustration, .study-art { break-inside: avoid; }
  table { min-width: 0; font-size: 8.5pt; }
  tbody tr:hover td { background: none; }
  .study-art { box-shadow: none; max-height: 90mm; width: auto; filter: none; }
  .study-illustration { max-height: 100mm; filter: none; }
  .home-art { display: none; }
  .study-map { min-width: 0; width: 100%; max-height: 240mm; object-fit: contain; }
  .map-viewport { overflow: visible; border: 0; break-inside: avoid; }
  a { color: black; }
}

/* Language display: both languages by default; the local switch narrows it. */
.l-en1, .l-zh1 { display: none; }
html[data-lang="en"] .l-zh, html[data-lang="en"] .l-sep, html[data-lang="en"] .l-bi, html[data-lang="en"] .l-zh1 { display: none; }
html[data-lang="zh"] .l-en, html[data-lang="zh"] .l-sep, html[data-lang="zh"] .l-bi, html[data-lang="zh"] .l-en1 { display: none; }
html[data-lang="en"] .l-en1, html[data-lang="zh"] .l-zh1 { display: inline; }
html[data-lang="en"] .site-nav a .l-en, html[data-lang="zh"] .site-nav a .l-zh { display: inline; }

/* Side-by-side reading: each language starts on its own line. */
html:not([data-lang]) .reading-body h1 > .l-sep, html[data-lang="both"] .reading-body h1 > .l-sep { display: none; }
html:not([data-lang]) .reading-body h1 > .l-zh, html[data-lang="both"] .reading-body h1 > .l-zh { display: block; margin-top: .4rem; font-size: .68em; font-weight: 500; letter-spacing: 0; color: color-mix(in srgb, var(--text) 78%, var(--background)); }
html:not([data-lang]) .reading-body p > .l-en + .l-zh, html[data-lang="both"] .reading-body p > .l-en + .l-zh,
html:not([data-lang]) .reading-body p > .l-zh + .l-en, html[data-lang="both"] .reading-body p > .l-zh + .l-en { display: block; margin-top: .45rem; }
.article-meta .l-sep { color: var(--faint); }

/* Week-index return links in the year plan stay quiet. */
p:has(> a[href="#week-index"]:first-child) { font-size: .8rem; line-height: 1.8; color: var(--muted); padding-top: .9rem; border-top: 1px dashed var(--line); }
p:has(> a[href="#week-index"]:first-child) a { text-decoration: none; padding: .15rem .1rem; }
p:has(> a[href="#week-index"]:first-child) a:hover { text-decoration: underline; }
@media print { p:has(> a[href="#week-index"]:first-child) { display: none; } }
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


