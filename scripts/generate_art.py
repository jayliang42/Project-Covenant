#!/usr/bin/env python3
"""Generate the project's original vector illustrations.

The drawings are original works made for Project Covenant from simple shapes.
No network, image, or font dependency is needed. Use --check to reject drift
between this script and the committed SVG files in assets/art/.
"""

from __future__ import annotations

import argparse
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable

if __package__:
    from .publication_assets import validate_svg
else:
    from publication_assets import validate_svg

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/art"
ET.register_namespace("", "http://www.w3.org/2000/svg")
NS = "{http://www.w3.org/2000/svg}"
FONT = '"PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif'
SERIF = 'Georgia, "Songti SC", "Noto Serif CJK SC", serif'

PAPER = "#f4efe3"
INK = "#2f3a2f"
GREEN = "#456346"


def el(parent: ET.Element, tag: str, text: str | None = None, **attributes: object) -> ET.Element:
    node = ET.SubElement(parent, NS + tag, {key.replace("_", "-"): str(value) for key, value in attributes.items()})
    if text is not None:
        node.text = text
    return node


def canvas(name: str, width: int, height: int, title: str, desc: str) -> ET.Element:
    root = ET.Element(NS + "svg", {
        "viewBox": f"0 0 {width} {height}", "width": str(width), "height": str(height),
        "role": "img", "aria-labelledby": f"{name}-title {name}-desc",
    })
    el(root, "title", title, id=f"{name}-title")
    el(root, "desc", desc, id=f"{name}-desc")
    el(root, "rect", x=0, y=0, width=width, height=height, rx=18, fill=PAPER)
    return root


def path(points: list[tuple[float, float]], close: bool = True) -> str:
    text = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)
    return text + (" Z" if close else "")


def wave(x0: float, x1: float, y: float, amplitude: float, length: float, phase: float = 0.0) -> list[tuple[float, float]]:
    steps = max(8, int((x1 - x0) / 6))
    return [(x0 + (x1 - x0) * i / steps,
             y + amplitude * math.sin(phase + 2 * math.pi * (x0 + (x1 - x0) * i / steps) / length))
            for i in range(steps + 1)]


# --- 66-book library -------------------------------------------------------

SECTIONS = [
    ("Law", "律法", "#7c5a3a", ["创", "出", "利", "民", "申"], [50, 40, 27, 36, 34]),
    ("History", "历史书", "#a8743f", ["书", "士", "得", "撒上", "撒下", "王上", "王下", "代上", "代下", "拉", "尼", "斯"],
     [24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10]),
    ("Wisdom & poetry", "智慧与诗歌", "#c69a3e", ["伯", "诗", "箴", "传", "歌"], [42, 150, 31, 12, 8]),
    ("Major prophets", "大先知书", "#6d7f4a", ["赛", "耶", "哀", "结", "但"], [66, 52, 5, 48, 12]),
    ("Minor prophets", "小先知书", "#8f9d5c", ["何", "珥", "摩", "俄", "拿", "弥", "鸿", "哈", "番", "该", "亚", "玛"],
     [14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4]),
    ("Gospels & Acts", "福音书与使徒行传", "#456346", ["太", "可", "路", "约", "徒"], [28, 16, 24, 21, 28]),
    ("Paul's letters", "保罗书信", "#3f6c7a", ["罗", "林前", "林后", "加", "弗", "腓", "西", "帖前", "帖后", "提前", "提后", "多", "门"],
     [16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1]),
    ("General letters", "普通书信", "#5f7f97", ["来", "雅", "彼前", "彼后", "约一", "约二", "约三", "犹"], [13, 5, 5, 3, 5, 1, 1, 1]),
    ("Prophecy", "预言", "#7b4f6b", ["启"], [22]),
]


def library() -> ET.Element:
    width, height = 960, 510
    root = canvas(
        "bible-library", width, height,
        "The Bible as a library of 66 books | 圣经是一座 66 卷书的图书馆",
        "Two shelves hold 39 Old Testament books and 27 New Testament books. Each spine shows the "
        "book's Chinese abbreviation; its width grows with the number of chapters, and its color shows "
        "the book's section. | 两层书架摆放旧约 39 卷与新约 27 卷。书脊上写着中文缩写，宽度随章数增加，颜色表示所属分类。",
    )
    el(root, "text", "Old Testament · 旧约 39", x=40, y=46, font_family=SERIF, font_size=20, fill=INK)
    el(root, "text", "New Testament · 新约 27", x=40, y=290, font_family=SERIF, font_size=20, fill=INK)
    shelves = [(SECTIONS[:5], 190), (SECTIONS[5:], 432)]
    for groups, base in shelves:
        books = [(color, abbr, chapters) for _, _, color, abbrs, counts in groups for abbr, chapters in zip(abbrs, counts)]
        raw = [10 + 2.6 * math.sqrt(chapters) for _, _, chapters in books]
        gap = 2.0
        scale = (width - 80 - gap * (len(books) - 1)) / sum(raw)
        x = 40.0
        index = 0
        for name_en, name_zh, color, abbrs, counts in groups:
            start = x
            for abbr, chapters in zip(abbrs, counts):
                spine = raw[index] * scale
                tall = 112 + (index * 37 % 5) * 6
                el(root, "rect", x=f"{x:.1f}", y=f"{base - tall:.1f}", width=f"{spine:.1f}", height=tall, rx=2.5, fill=color)
                el(root, "rect", x=f"{x:.1f}", y=f"{base - tall + 12:.1f}", width=f"{spine:.1f}", height=3, fill="#ffffff", fill_opacity=0.35)
                el(root, "rect", x=f"{x:.1f}", y=f"{base - 18:.1f}", width=f"{spine:.1f}", height=3, fill="#ffffff", fill_opacity=0.35)
                label = el(root, "text", x=f"{x + spine / 2:.1f}", y=f"{base - tall + 34:.1f}", font_family=FONT,
                           font_size=12 if spine >= 15 else 10, text_anchor="middle", fill="#fffdf6")
                for position, character in enumerate(abbr):
                    el(label, "tspan", character, x=f"{x + spine / 2:.1f}", dy=0 if position == 0 else 14)
                x += spine + gap
                index += 1
            end = x - gap
            el(root, "line", x1=f"{start:.1f}", x2=f"{end:.1f}", y1=base + 14, y2=base + 14, stroke=color, stroke_width=3, stroke_linecap="round")
            el(root, "text", name_zh, x=f"{(start + end) / 2:.1f}", y=base + 34, font_family=FONT, font_size=13, text_anchor="middle", fill=INK)
            el(root, "text", name_en, x=f"{(start + end) / 2:.1f}", y=base + 50, font_family=FONT, font_size=11, text_anchor="middle", fill="#5f665b")
        el(root, "rect", x=30, y=base, width=width - 60, height=8, rx=3, fill="#6b4e33")
    return root


# --- Scenes ----------------------------------------------------------------

def jonah() -> ET.Element:
    width, height = 800, 450
    root = canvas("jonah", width, height, "Jonah and the storm | 约拿与风暴",
                  "A small sailing boat tosses on a stormy sea under dark clouds and rain, while a great fish "
                  "swims beneath the waves. | 乌云与大雨下，一艘小帆船在风浪中颠簸，一条大鱼在浪底游动。")
    el(root, "rect", x=0, y=0, width=width, height=290, rx=18, fill="#c9d3d6")
    el(root, "rect", x=0, y=120, width=width, height=170, fill="#b7c3c7")
    for cx, cy, r in [(120, 70, 60), (200, 50, 70), (300, 80, 55), (430, 55, 75), (540, 75, 60), (650, 50, 70), (740, 80, 55)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#6f7c83", fill_opacity=0.85)
    for i in range(34):
        x = 20 + i * 24
        el(root, "line", x1=x, y1=110 + (i % 3) * 12, x2=x - 18, y2=190 + (i % 4) * 10, stroke="#8b9aa1", stroke_width=2, stroke_linecap="round", stroke_opacity=0.7)
    sea = wave(0, width, 250, 14, 160)
    el(root, "path", d=path([(0, height)] + sea + [(width, height)]), fill="#2f5d6e")
    deep = wave(0, width, 330, 8, 220, 1.3)
    el(root, "path", d=path([(0, height)] + deep + [(width, height)]), fill="#24495a")
    # great fish beneath the surface
    fish = [(260, 380), (300, 352), (380, 338), (470, 344), (540, 362), (580, 382), (540, 400), (470, 414), (380, 416), (300, 404)]
    el(root, "path", d=path(fish), fill="#173744")
    el(root, "path", d=path([(575, 382), (640, 350), (628, 384), (642, 418)]), fill="#173744")
    el(root, "circle", cx=312, cy=372, r=5, fill="#c9d3d6")
    el(root, "path", d=path([(262, 382), (300, 390)], close=False), stroke="#c9d3d6", stroke_width=2, fill="none", stroke_linecap="round")
    # boat, tilted on a crest
    boat = ET.SubElement(root, NS + "g", {"transform": "rotate(-12 400 236)"})
    el(boat, "path", d="M320 230 L480 230 L455 262 L345 262 Z", fill="#7a4a2b")
    el(boat, "rect", x=320, y=226, width=160, height=6, fill="#5c371f")
    el(boat, "line", x1=400, y1=226, x2=400, y2=110, stroke="#4a3020", stroke_width=5, stroke_linecap="round")
    el(boat, "path", d="M404 118 L470 200 L404 206 Z", fill="#ece0c6")
    el(boat, "path", d="M396 124 L346 198 L396 204 Z", fill="#ddcfb1")
    for start in range(0, width, 160):
        if 300 <= start <= 480:
            continue  # the boat sits on this crest
        foam = wave(start + 50, start + 110, 250, 14, 160)
        el(root, "path", d=path([(x, y - 3) for x, y in foam], close=False),
           fill="none", stroke="#e8f0f2", stroke_width=3, stroke_linecap="round", stroke_opacity=0.85)
    return root


def shepherd() -> ET.Element:
    width, height = 800, 450
    root = canvas("shepherd", width, height, "The LORD is my shepherd | 耶和华是我的牧者",
                  "A shepherd with a staff stands on green hills beside a quiet stream, watching over a small "
                  "flock under a warm sun. | 温暖的阳光下，一位手持杖的牧人站在青草地上、安静的溪水旁，看顾一小群羊。")
    el(root, "rect", x=0, y=0, width=width, height=height, rx=18, fill="#f3e7cc")
    el(root, "circle", cx=620, cy=110, r=58, fill="#eab54d")
    el(root, "circle", cx=620, cy=110, r=84, fill="#eab54d", fill_opacity=0.18)
    el(root, "path", d=path([(0, 260)] + wave(0, 800, 230, 28, 520, 0.4) + [(800, 450), (0, 450)]), fill="#a9bf8a")
    el(root, "path", d=path([(0, 300)] + wave(0, 800, 290, 22, 420, 2.0) + [(800, 450), (0, 450)]), fill="#86a46b")
    el(root, "path", d=path([(0, 360)] + wave(0, 800, 350, 16, 360, 4.0) + [(800, 450), (0, 450)]), fill="#5f824c")
    stream = "M0 420 C 150 380, 260 440, 400 400 S 640 360, 800 395 L800 450 L0 450 Z"
    el(root, "path", d=stream, fill="#9cc6cf")
    el(root, "path", d="M40 425 C 150 395, 250 440, 380 410", fill="none", stroke="#e7f3f4", stroke_width=3, stroke_linecap="round")
    # shepherd
    el(root, "path", d="M205 330 C 200 260, 215 225, 232 220 C 250 225, 262 262, 258 330 Z", fill="#6b4f3a")
    el(root, "path", d="M214 236 C 222 228, 244 228, 252 238 L250 262 L216 262 Z", fill="#c8a978")
    el(root, "circle", cx=233, cy=206, r=15, fill="#8a5f43")
    el(root, "path", d="M216 200 C 220 182, 248 182, 251 200 L251 214 L246 214 L244 200 L222 200 L220 216 L215 216 Z", fill="#d9c7a1")
    el(root, "path", d="M282 332 L286 190 C 286 172, 306 170, 306 186", fill="none", stroke="#4a3424", stroke_width=6, stroke_linecap="round")
    el(root, "line", x1=256, y1=250, x2=284, y2=246, stroke="#6b4f3a", stroke_width=8, stroke_linecap="round")
    # sheep
    for sx, sy, scale in [(360, 330, 1.0), (430, 318, 0.9), (500, 340, 1.05), (575, 322, 0.85), (450, 365, 1.1), (640, 350, 0.95)]:
        group = ET.SubElement(root, NS + "g", {"transform": f"translate({sx} {sy}) scale({scale})"})
        for dx, dy, r in [(-16, 0, 14), (0, -6, 16), (16, 0, 14), (0, 8, 14), (-8, 6, 12), (10, 8, 12)]:
            el(group, "circle", cx=dx, cy=dy, r=r, fill="#f8f5ec")
        el(group, "circle", cx=28, cy=-6, r=9, fill="#3e3a33")
        el(group, "line", x1=-10, y1=18, x2=-10, y2=32, stroke="#3e3a33", stroke_width=4, stroke_linecap="round")
        el(group, "line", x1=12, y1=18, x2=12, y2=32, stroke="#3e3a33", stroke_width=4, stroke_linecap="round")
    return root


def letter() -> ET.Element:
    width, height = 800, 450
    root = canvas("letter", width, height, "A letter by lamplight | 灯下书信",
                  "On a wooden table lie a parchment letter with a wax seal, a reed pen, and a small clay oil "
                  "lamp with a glowing flame. | 木桌上放着一封盖有蜡印的羊皮纸书信、一支芦苇笔，以及一盏点着火苗的小陶油灯。")
    el(root, "rect", x=0, y=0, width=width, height=height, rx=18, fill="#3d342b")
    el(root, "circle", cx=600, cy=210, r=190, fill="#f2c56b", fill_opacity=0.10)
    el(root, "circle", cx=600, cy=210, r=110, fill="#f2c56b", fill_opacity=0.14)
    el(root, "path", d="M0 300 L800 300 L800 450 L0 450 Z", fill="#7a5537")
    el(root, "path", d="M0 300 L800 300 L800 312 L0 312 Z", fill="#8e6644")
    for y in (340, 372, 404, 436):
        el(root, "line", x1=0, y1=y, x2=800, y2=y + 4, stroke="#6a4930", stroke_width=2, stroke_opacity=0.6)
    # parchment
    el(root, "path", d="M120 120 L440 104 L462 330 L138 346 Z", fill="#efe2c2")
    el(root, "path", d="M120 120 L138 346 L126 348 L108 124 Z", fill="#dccaa1")
    for i in range(9):
        y = 150 + i * 19
        length = 270 if i % 4 != 3 else 170
        el(root, "line", x1=150, y1=y + 4 - i * 0.8, x2=150 + length, y2=y - 10 - i * 0.8, stroke="#8f7a55", stroke_width=2.4, stroke_linecap="round", stroke_opacity=0.75)
    el(root, "circle", cx=400, cy=300, r=20, fill="#9b3b2e")
    el(root, "circle", cx=400, cy=300, r=12, fill="#b5503f")
    el(root, "line", x1=330, y1=372, x2=520, y2=330, stroke="#c9b27a", stroke_width=6, stroke_linecap="round")
    el(root, "path", d="M520 330 L536 325 L522 336 Z", fill="#3a2a1d")
    # oil lamp
    el(root, "path", d="M540 286 C 540 250, 660 246, 690 268 L720 262 L712 280 C 700 296, 600 304, 540 286 Z", fill="#b5793f")
    el(root, "path", d="M560 270 C 580 258, 640 256, 664 266", fill="none", stroke="#d29659", stroke_width=4, stroke_linecap="round")
    el(root, "path", d="M712 262 C 700 236, 708 214, 722 196 C 734 218, 740 240, 726 262 Z", fill="#f0a93a")
    el(root, "path", d="M716 258 C 712 242, 716 230, 722 220 C 730 234, 730 248, 724 258 Z", fill="#fbe08a")
    el(root, "path", d="M600 300 L650 300 L640 312 L610 312 Z", fill="#8f5c2f")
    return root


def rebuilding() -> ET.Element:
    width, height = 800, 450
    root = canvas("rebuilding", width, height, "Rebuilding the walls | 重建城墙",
                  "Workers rebuild a city wall and gate stone by stone, using a wooden scaffold and baskets, "
                  "under a clear sky. | 晴空下，工人借着木架和筐子，一块一块地重建城墙与城门。")
    el(root, "rect", x=0, y=0, width=width, height=height, rx=18, fill="#dfe8ea")
    el(root, "path", d=path([(0, 330)] + wave(0, 800, 310, 18, 500, 1.0) + [(800, 450), (0, 450)]), fill="#c9b48a")
    el(root, "path", d="M0 380 L800 380 L800 450 L0 450 Z", fill="#b39a6c")
    stones = ["#cdb48a", "#bfa274", "#d7c098", "#c4aa7e"]
    for row in range(7):
        y = 340 - row * 30
        offset = 0 if row % 2 == 0 else 30
        right = 760 - max(0, row - 3) * 80
        x = 60 - offset
        column = 0
        while x < right:
            w = 58
            if not (330 <= x + w / 2 <= 470 and row < 5):
                el(root, "rect", x=max(x, 60), y=y, width=min(w, right - max(x, 60)), height=27, rx=3, fill=stones[(row + column) % 4])
            x += w + 2
            column += 1
    el(root, "path", d="M330 370 L330 250 C 330 190, 470 190, 470 250 L470 370 Z", fill="#5a4630")
    el(root, "path", d="M346 370 L346 256 C 346 210, 454 210, 454 256 L454 370 Z", fill="#2f2a22")
    for x in (560, 640, 720):
        el(root, "line", x1=x, y1=370, x2=x, y2=150, stroke="#7a5537", stroke_width=6)
    for y in (180, 240, 300):
        el(root, "line", x1=550, y1=y, x2=730, y2=y, stroke="#7a5537", stroke_width=5)
    # workers
    for x, y, carry in [(600, 240, True), (150, 380, True), (240, 380, False)]:
        el(root, "circle", cx=x, cy=y - 58, r=10, fill="#8a5f43")
        el(root, "path", d=f"M{x - 12} {y} L{x - 9} {y - 44} L{x + 9} {y - 44} L{x + 12} {y} Z", fill="#4f6b52" if carry else "#7b5d84")
        if carry:
            el(root, "rect", x=x - 16, y=y - 86, width=32, height=18, rx=4, fill="#cdb48a")
            el(root, "line", x1=x - 10, y1=y - 40, x2=x - 14, y2=y - 72, stroke="#8a5f43", stroke_width=4, stroke_linecap="round")
            el(root, "line", x1=x + 10, y1=y - 40, x2=x + 14, y2=y - 72, stroke="#8a5f43", stroke_width=4, stroke_linecap="round")
        else:
            el(root, "path", d=f"M{x + 30} {y} L{x + 26} {y - 26} L{x + 54} {y - 26} L{x + 50} {y} Z", fill="#a77d4b")
            el(root, "line", x1=x + 8, y1=y - 38, x2=x + 30, y2=y - 26, stroke="#8a5f43", stroke_width=4, stroke_linecap="round")
    return root


def open_book() -> ET.Element:
    width, height = 800, 400
    root = canvas("open-bible", width, height, "Finding a verse: John 3:16 | 查找经文：约翰福音 3:16",
                  "An open book shows a chapter number at the top and small verse numbers in the margin; "
                  "the line marked 16 is highlighted, with labels for book, chapter, and verse. | "
                  "翻开的书页上方标着章数，页边有小小的节数；第 16 节被标亮，旁边注明书卷、章和节。")
    el(root, "path", d="M80 90 C 220 60, 330 70, 400 104 L400 356 C 330 322, 220 316, 80 344 Z", fill="#fffaf0", stroke="#d9cdb2", stroke_width=2)
    el(root, "path", d="M720 90 C 580 60, 470 70, 400 104 L400 356 C 470 322, 580 316, 720 344 Z", fill="#fffaf0", stroke="#d9cdb2", stroke_width=2)
    el(root, "path", d="M400 104 L400 356", stroke="#cbbd9c", stroke_width=3)
    el(root, "path", d="M548 70 L548 132 L562 120 L576 132 L576 74 Z", fill="#9b3b2e")
    el(root, "text", "John 3 · 约翰福音 3章", x=240, y=118, font_family=FONT, font_size=18, text_anchor="middle", fill=GREEN, font_weight=600)
    for i, verse in enumerate(range(13, 20)):
        y = 152 + i * 26
        if verse == 16:
            el(root, "rect", x=118, y=y - 16, width=256, height=22, rx=4, fill="#f2d98c", fill_opacity=0.8)
        el(root, "text", str(verse), x=108, y=y, font_family=FONT, font_size=12, text_anchor="end", fill="#9b3b2e")
        el(root, "line", x1=124, y1=y - 5, x2=124 + (230 if verse % 3 else 170), y2=y - 5, stroke="#7d7462", stroke_width=3, stroke_linecap="round", stroke_opacity=0.6)
    for i in range(8):
        y = 140 + i * 26
        el(root, "line", x1=430, y1=y, x2=430 + (240 if i % 3 else 170), y2=y, stroke="#7d7462", stroke_width=3, stroke_linecap="round", stroke_opacity=0.35)
    # labels
    el(root, "rect", x=470, y=292, width=250, height=74, rx=10, fill="#456346")
    el(root, "text", "John 3:16 = 约 3:16", x=595, y=322, font_family=FONT, font_size=18, text_anchor="middle", fill="#fffdf6", font_weight=600)
    el(root, "text", "book · chapter : verse", x=595, y=344, font_family=FONT, font_size=12, text_anchor="middle", fill="#e6efe0")
    el(root, "text", "书卷 · 章 : 节", x=595, y=360, font_family=FONT, font_size=12, text_anchor="middle", fill="#e6efe0")
    el(root, "path", d="M470 320 C 430 300, 400 250, 378 244", fill="none", stroke="#456346", stroke_width=2.5, stroke_dasharray="6 5")
    return root


ARTWORKS: dict[str, Callable[[], ET.Element]] = {
    "bible-library.svg": library,
    "jonah.svg": jonah,
    "shepherd.svg": shepherd,
    "letter.svg": letter,
    "rebuilding.svg": rebuilding,
    "open-bible.svg": open_book,
}


def render(builder: Callable[[], ET.Element]) -> bytes:
    data = (ET.tostring(builder(), encoding="unicode") + "\n").encode("utf-8")
    validate_svg(data)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed SVG files differ from generated output")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    status = 0
    for name, builder in ARTWORKS.items():
        data = render(builder)
        target = OUTPUT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != data:
                print(f"art_drift={name}", file=sys.stderr)
                status = 1
            else:
                print(f"art_ok={name}")
        else:
            target.write_bytes(data)
            print(f"art_written={name}; bytes={len(data)}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
