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


# --- Second set: scenes for the 52-week plan ---------------------------------

SKIN = ["#8a5f43", "#b07a55", "#6e4a33", "#c08a63", "#7d5338"]
ROBES = ["#4f6b52", "#7b5d84", "#a0703e", "#3f6c7a", "#8b4b45", "#6d7f4a"]


def person(parent: ET.Element, x: float, y: float, robe: str, skin: str, scale: float = 1.0) -> None:
    """A simple standing figure whose feet rest at (x, y)."""
    group = ET.SubElement(parent, NS + "g", {"transform": f"translate({x:.1f} {y:.1f}) scale({scale})"})
    el(group, "path", d="M-13 0 L-9 -44 C -8 -50, 8 -50, 9 -44 L13 0 Z", fill=robe)
    el(group, "circle", cx=0, cy=-56, r=9, fill=skin)


def sky(root: ET.Element, width: int, height: int, color: str) -> None:
    el(root, "rect", x=0, y=0, width=width, height=height, rx=18, fill=color)


def joseph_granary() -> ET.Element:
    w, h = 800, 450
    root = canvas("joseph-granary", w, h, "Grain stored in Egypt | 埃及的粮仓",
                  "Domed granaries and sacks of grain stand beside the Nile, with pyramids on the desert horizon. | "
                  "尼罗河边有圆顶粮仓和一袋袋粮食，沙漠地平线上可见金字塔。")
    sky(root, w, h, "#f3e2bd")
    el(root, "circle", cx=640, cy=96, r=46, fill="#eaa94a")
    el(root, "path", d=path([(0, 270)] + wave(0, 800, 262, 10, 600, 0.5) + [(800, 450), (0, 450)]), fill="#e3c58e")
    for x, base, size in [(470, 262, 90), (580, 262, 120), (700, 262, 70)]:
        el(root, "path", d=path([(x - size, base), (x, base - size * 0.9), (x + size, base)]), fill="#d8b47a")
        el(root, "path", d=path([(x, base - size * 0.9), (x + size, base), (x + 18, base)]), fill="#c39a5e")
    el(root, "path", d="M0 360 C 200 340, 420 380, 800 350 L800 395 C 420 420, 200 380, 0 400 Z", fill="#7fb0b5")
    for i in range(18):
        x = 30 + i * 44
        el(root, "line", x1=x, y1=392 - (i % 3) * 4, x2=x + 6, y2=362 - (i % 3) * 6, stroke="#6d8f4e", stroke_width=3, stroke_linecap="round")
    for x in (90, 190, 290):
        el(root, "rect", x=x - 42, y=190, width=84, height=96, fill="#c99a5b")
        el(root, "path", d=f"M{x - 42} 192 C {x - 42} 130, {x + 42} 130, {x + 42} 192 Z", fill="#d8ad6c")
        el(root, "rect", x=x - 12, y=246, width=24, height=40, rx=3, fill="#7a5537")
    for x, y in [(360, 300), (392, 300), (376, 278), (408, 296)]:
        el(root, "path", d=f"M{x - 14} {y} C {x - 16} {y - 22}, {x + 16} {y - 22}, {x + 14} {y} Z", fill="#e9d6a6", stroke="#b89a62", stroke_width=1.5)
    return root


def sea_crossing() -> ET.Element:
    w, h = 800, 450
    root = canvas("sea-crossing", w, h, "Crossing the sea | 过红海",
                  "At night, a line of travelers walks on a dry path between two towering walls of water, led by "
                  "a glowing pillar. | 夜里，一行人走在两道高耸水墙之间的干地上，前面有发光的柱子引路。")
    sky(root, w, h, "#1f2f4a")
    for x, y in [(80, 60), (160, 110), (260, 50), (520, 70), (610, 120), (700, 60), (740, 140), (360, 100)]:
        el(root, "circle", cx=x, cy=y, r=2, fill="#f4efe3", fill_opacity=0.8)
    el(root, "path", d="M360 430 L440 430 L520 260 L280 260 Z", fill="#d9c08e")
    el(root, "path", d="M0 450 L0 140 C 80 120, 150 160, 220 150 C 260 170, 290 220, 300 260 L360 450 Z", fill="#2f6f8a")
    el(root, "path", d="M800 450 L800 140 C 720 120, 650 160, 580 150 C 540 170, 510 220, 500 260 L440 450 Z", fill="#2f6f8a")
    el(root, "path", d="M0 450 L0 220 C 90 200, 170 240, 250 230 L330 450 Z", fill="#245a72")
    el(root, "path", d="M800 450 L800 220 C 710 200, 630 240, 550 230 L470 450 Z", fill="#245a72")
    for side in (-1, 1):
        for i in range(5):
            x = 400 + side * (130 + i * 50)
            el(root, "path", d=f"M{x - 20} {150 + i * 14} C {x - 6} {138 + i * 14}, {x + 6} {138 + i * 14}, {x + 20} {150 + i * 14}",
               fill="none", stroke="#cfe6ee", stroke_width=3, stroke_linecap="round", stroke_opacity=0.7)
    el(root, "rect", x=388, y=120, width=24, height=150, rx=12, fill="#f0a93a", fill_opacity=0.85)
    el(root, "circle", cx=400, cy=150, r=46, fill="#f0a93a", fill_opacity=0.18)
    for i, (x, y, s) in enumerate([(400, 300, 0.55), (392, 330, 0.65), (408, 360, 0.75), (396, 395, 0.85), (412, 428, 0.95)]):
        person(root, x, y, ROBES[i % len(ROBES)], SKIN[i % len(SKIN)], s)
    return root


def wilderness_camp() -> ET.Element:
    w, h = 800, 450
    root = canvas("wilderness-camp", w, h, "Camp in the wilderness | 旷野中的营地",
                  "Rows of tents surround a central tent of meeting in a desert valley, under a tall pillar of cloud. | "
                  "沙漠山谷中，一排排帐棚围绕着中间的会幕，上方有高高的云柱。")
    sky(root, w, h, "#f2e4c8")
    el(root, "path", d="M0 250 L120 150 L220 230 L330 120 L470 240 L600 140 L800 250 L800 450 L0 450 Z", fill="#c7a77a")
    el(root, "path", d="M0 290 C 200 270, 600 270, 800 290 L800 450 L0 450 Z", fill="#e1c793")
    for cx, cy, r in [(400, 70, 30), (388, 104, 28), (412, 136, 30), (396, 168, 26), (404, 196, 22)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#ffffff", fill_opacity=0.9)
    el(root, "rect", x=340, y=230, width=120, height=56, fill="#f4efe3", stroke="#b8a37a", stroke_width=2)
    el(root, "rect", x=380, y=214, width=44, height=40, fill="#7b4f6b")
    el(root, "path", d="M376 216 L402 196 L428 216 Z", fill="#5e3c52")
    colors = ["#a0703e", "#8b6a4a", "#b8865a", "#7a5f45"]
    for row, y in enumerate((312, 352, 396)):
        count = 8 + row
        for i in range(count):
            x = 40 + i * (720 / (count - 1))
            if row == 0 and 300 < x < 500:
                continue
            size = 22 + row * 5
            el(root, "path", d=path([(x - size, y), (x, y - size * 1.1), (x + size, y)]), fill=colors[(i + row) % 4])
            el(root, "path", d=path([(x - 4, y), (x, y - size * 0.6), (x + 4, y)]), fill="#3d342b")
    return root


def barley_harvest() -> ET.Element:
    w, h = 800, 450
    root = canvas("barley-harvest", w, h, "Barley harvest near Bethlehem | 伯利恒附近的麦收",
                  "A woman gathers leftover stalks in a golden barley field, with bound sheaves and a hilltop town "
                  "in the distance. | 一位妇人在金黄的大麦田里拾取遗落的麦穗，田里有捆好的禾捆，远处山上有一座小城。")
    sky(root, w, h, "#f5e6c6")
    el(root, "circle", cx=150, cy=120, r=44, fill="#ef9f45")
    el(root, "path", d=path([(0, 230)] + wave(0, 800, 210, 20, 700, 2.2) + [(800, 450), (0, 450)]), fill="#c9b07a")
    for x, y in [(560, 168), (590, 160), (620, 166), (650, 156), (680, 166), (610, 146)]:
        el(root, "rect", x=x, y=y, width=26, height=22, fill="#e9dcc0", stroke="#b8a37a", stroke_width=1)
    el(root, "path", d="M0 260 C 200 240, 600 250, 800 240 L800 450 L0 450 Z", fill="#e3b955")
    for row in range(6):
        y = 280 + row * 30
        el(root, "path", d=path(wave(0, 800, y, 4, 120, row), close=False), fill="none", stroke="#c99a35", stroke_width=3, stroke_opacity=0.7)
    for x, y in [(520, 330), (620, 360), (700, 320)]:
        for dx in range(-14, 15, 4):
            el(root, "line", x1=x + dx * 0.4, y1=y, x2=x + dx, y2=y - 52, stroke="#b8862f", stroke_width=3, stroke_linecap="round")
        el(root, "rect", x=x - 10, y=y - 26, width=20, height=6, rx=2, fill="#7a5537")
    group = ET.SubElement(root, NS + "g", {"transform": "translate(300 380)"})
    el(group, "path", d="M-16 0 L-10 -40 C -4 -58, 30 -60, 40 -46 L28 -36 C 20 -44, 6 -42, 4 -34 L14 0 Z", fill="#8b4b45")
    el(group, "circle", cx=40, cy=-50, r=10, fill="#b07a55")
    el(group, "path", d="M30 -60 C 38 -70, 54 -64, 52 -50 L46 -50 C 46 -58, 38 -60, 34 -56 Z", fill="#e9dcc0")
    el(group, "line", x1=34, y1=-36, x2=52, y2=-6, stroke="#b07a55", stroke_width=4, stroke_linecap="round")
    for dx in (-4, 0, 4):
        el(group, "line", x1=54 + dx, y1=-4, x2=58 + dx * 2, y2=-26, stroke="#b8862f", stroke_width=2.5, stroke_linecap="round")
    return root


def david_harp() -> ET.Element:
    w, h = 800, 450
    root = canvas("david-harp", w, h, "A shepherd's lyre and sling | 牧童的琴与机弦",
                  "A wooden lyre, a leather sling, and five smooth stones lie on a rock above green pasture, with "
                  "a small golden crown nearby. | 青草地上方的岩石上放着木琴、皮制机弦和五块光滑的石子，旁边有一顶小金冠。")
    sky(root, w, h, "#e6eedb")
    el(root, "path", d=path([(0, 300)] + wave(0, 800, 280, 18, 500, 1.2) + [(800, 450), (0, 450)]), fill="#8fb06e")
    el(root, "path", d="M120 330 C 160 290, 640 290, 690 330 L700 400 L110 400 Z", fill="#b9ad98")
    el(root, "path", d="M120 330 C 160 290, 640 290, 690 330 L680 340 C 600 310, 200 312, 128 340 Z", fill="#cfc4b0")
    # lyre
    el(root, "path", d="M210 320 C 190 250, 170 180, 196 120 L214 126 C 196 180, 214 250, 236 318 Z", fill="#7a4a2b")
    el(root, "path", d="M370 320 C 390 250, 410 180, 384 120 L366 126 C 384 180, 366 250, 344 318 Z", fill="#7a4a2b")
    el(root, "rect", x=190, y=116, width=200, height=16, rx=8, fill="#5c371f")
    el(root, "path", d="M208 300 L372 300 L380 330 L200 330 Z", fill="#8e5a34")
    for i in range(7):
        x = 238 + i * 17
        el(root, "line", x1=x, y1=132, x2=x - 2 + i * 0.6, y2=300, stroke="#efe2c2", stroke_width=2)
    # sling and stones
    el(root, "path", d="M440 300 C 470 250, 520 250, 560 280 C 600 310, 640 300, 660 270", fill="none", stroke="#6b4e33", stroke_width=4, stroke_linecap="round")
    el(root, "path", d="M540 268 C 548 252, 580 252, 588 270 C 578 284, 552 284, 540 268 Z", fill="#8a6a48")
    for x, y, r in [(470, 330, 12), (500, 336, 11), (530, 330, 13), (562, 338, 10), (592, 332, 12)]:
        el(root, "circle", cx=x, cy=y, r=r, fill="#9a948a")
        el(root, "circle", cx=x - r * 0.3, cy=y - r * 0.3, r=r * 0.35, fill="#c9c3b8")
    el(root, "path", d="M600 210 L612 180 L628 200 L640 172 L652 200 L668 180 L680 210 Z", fill="#e1b444")
    el(root, "rect", x=600, y=208, width=80, height=12, rx=3, fill="#c99a2e")
    return root


def carmel_altar() -> ET.Element:
    w, h = 800, 450
    root = canvas("carmel-altar", w, h, "Fire on Mount Carmel | 迦密山上的火",
                  "Fire falls from the sky onto an altar of twelve stones surrounded by a water-filled trench on a "
                  "mountaintop, while a small cloud rises over the distant sea. | "
                  "火从天降在山顶十二块石头筑成的祭坛上，四周沟里满了水；远处海面升起一小片云。")
    sky(root, w, h, "#e9d6c0")
    el(root, "path", d="M0 300 C 120 280, 260 250, 400 240 C 540 250, 680 280, 800 300 L800 450 L0 450 Z", fill="#9a8a6a")
    el(root, "path", d="M600 300 L800 300 L800 330 L600 330 Z", fill="#7fa8b5")
    el(root, "circle", cx=720, cy=272, r=12, fill="#8d9aa3")
    el(root, "circle", cx=708, cy=278, r=9, fill="#8d9aa3")
    el(root, "path", d="M300 330 C 300 300, 500 300, 500 330 L500 346 C 500 372, 300 372, 300 346 Z", fill="#7fa8b5")
    for row, y in enumerate((300, 276, 252)):
        count = 4 if row < 2 else 4
        for i in range(count):
            el(root, "rect", x=332 + i * 36 + (row % 2) * 8, y=y, width=34, height=22, rx=3, fill="#b8ad98" if (i + row) % 2 else "#a39883")
    for dx, top in [(-40, 60), (-10, 20), (20, 40), (50, 80)]:
        x = 400 + dx
        el(root, "path", d=f"M{x} {top} L{x + 14} {top + 70} L{x - 4} {top + 90} L{x + 10} 250 L{x - 18} 160 L{x - 2} 140 Z", fill="#f0a93a", fill_opacity=0.9)
    el(root, "path", d="M340 252 C 330 210, 360 190, 372 170 C 380 200, 400 190, 404 160 C 420 190, 444 200, 438 170 C 470 200, 470 230, 460 252 Z", fill="#e8742f")
    el(root, "path", d="M362 252 C 360 226, 380 214, 388 196 C 396 218, 414 214, 420 200 C 432 222, 440 236, 438 252 Z", fill="#fbd36b")
    return root


def lions_den() -> ET.Element:
    w, h = 800, 450
    root = canvas("lions-den", w, h, "Daniel in the lions' den | 狮子坑中的但以理",
                  "In a dark stone pit, a man kneels in prayer in a beam of light while two lions lie quietly nearby. | "
                  "幽暗的石坑里，一人跪在一道光中祷告，两只狮子安静地伏在一旁。")
    sky(root, w, h, "#3a342d")
    el(root, "path", d="M330 0 L470 0 L560 450 L240 450 Z", fill="#f2d98c", fill_opacity=0.18)
    el(root, "path", d="M0 360 C 200 340, 600 340, 800 360 L800 450 L0 450 Z", fill="#5a4e40")
    for x, y, r in [(60, 120, 50), (90, 240, 60), (720, 110, 55), (740, 250, 60), (40, 330, 40), (770, 340, 40)]:
        el(root, "circle", cx=x, cy=y, r=r, fill="#4a4036")
    # kneeling man
    el(root, "path", d="M380 380 L376 330 C 376 312, 412 310, 416 330 L430 380 Z", fill="#3f6c7a")
    el(root, "path", d="M380 380 L440 380 L440 368 L400 362 Z", fill="#355b67")
    el(root, "circle", cx=398, cy=300, r=12, fill="#b07a55")
    el(root, "line", x1=408, y1=322, x2=420, y2=296, stroke="#b07a55", stroke_width=5, stroke_linecap="round")
    # lions
    for x, flip in [(200, 1), (600, -1)]:
        group = ET.SubElement(root, NS + "g", {"transform": f"translate({x} 372) scale({flip} 1)"})
        el(group, "path", d="M-70 0 C -72 -30, -40 -40, 0 -36 C 30 -34, 50 -24, 52 0 Z", fill="#c99044")
        el(group, "path", d="M-70 -6 C -90 -10, -100 -24, -92 -36", fill="none", stroke="#c99044", stroke_width=5, stroke_linecap="round")
        el(group, "circle", cx=58, cy=-30, r=28, fill="#8a5a2b")
        el(group, "circle", cx=66, cy=-24, r=17, fill="#d9a352")
        el(group, "circle", cx=72, cy=-28, r=2.5, fill="#3a2a1d")
        el(group, "path", d="M74 -16 C 78 -14, 82 -16, 84 -18", fill="none", stroke="#3a2a1d", stroke_width=2, stroke_linecap="round")
        el(group, "path", d="M30 0 C 40 -6, 60 -6, 80 0 Z", fill="#c99044")
    return root


def bread_cup() -> ET.Element:
    w, h = 800, 450
    root = canvas("bread-cup", w, h, "Bread and cup | 饼与杯",
                  "A broken loaf of bread and a simple cup sit on a table in warm evening light. | "
                  "暖暖的黄昏光线下，桌上放着一个掰开的饼和一只朴素的杯。")
    sky(root, w, h, "#4a3a44")
    el(root, "circle", cx=400, cy=210, r=230, fill="#f2c56b", fill_opacity=0.08)
    el(root, "path", d="M0 300 L800 300 L800 450 L0 450 Z", fill="#7a5537")
    el(root, "path", d="M0 300 L800 300 L800 314 L0 314 Z", fill="#8e6644")
    el(root, "path", d="M80 320 L720 320 L760 360 L40 360 Z", fill="#efe6d3", fill_opacity=0.9)
    el(root, "path", d="M210 304 C 200 250, 300 236, 340 262 L330 306 Z", fill="#c98a45")
    el(root, "path", d="M350 306 L360 262 C 400 240, 470 256, 462 306 Z", fill="#c98a45")
    el(root, "path", d="M330 306 L340 262 L350 268 L344 306 Z", fill="#ead2a2")
    el(root, "path", d="M350 306 L360 262 L352 266 L344 306 Z", fill="#ead2a2")
    for x in (240, 280, 400, 430):
        el(root, "path", d=f"M{x} 270 C {x + 8} 262, {x + 16} 262, {x + 22} 270", fill="none", stroke="#a76d33", stroke_width=3, stroke_linecap="round")
    el(root, "path", d="M520 180 L620 180 C 620 240, 600 262, 576 268 L576 300 L606 310 L534 310 L564 300 L564 268 C 540 262, 520 240, 520 180 Z", fill="#b5793f")
    el(root, "path", d="M526 186 L614 186 C 612 206, 600 214, 570 214 C 540 214, 528 206, 526 186 Z", fill="#7a2f3a")
    return root


def empty_tomb() -> ET.Element:
    w, h = 800, 450
    root = canvas("empty-tomb", w, h, "The empty tomb at dawn | 清晨的空坟墓",
                  "At sunrise, a large round stone has been rolled away from the open doorway of a rock-cut tomb in "
                  "a garden. | 日出时分，园中凿在岩石里的坟墓门口，一块大圆石已被滚开，墓门敞开。")
    sky(root, w, h, "#f6dcc0")
    for i in range(9):
        angle = math.radians(200 + i * 17)
        # Fix serialization precision across platform math libraries.
        el(root, "line", x1=600, y1=230,
           x2=f"{600 + 420 * math.cos(angle) * -1:.6f}", y2=f"{230 + 420 * math.sin(angle):.6f}",
           stroke="#f7c98a", stroke_width=10, stroke_opacity=0.35, stroke_linecap="round")
    el(root, "circle", cx=600, cy=230, r=50, fill="#f3a95a")
    el(root, "path", d="M0 450 L0 140 C 120 110, 300 120, 420 200 C 460 240, 470 300, 470 450 Z", fill="#a39883")
    el(root, "path", d="M0 450 L0 170 C 110 150, 270 160, 380 220 C 420 250, 430 300, 430 450 Z", fill="#b8ad98")
    el(root, "path", d="M180 360 L180 290 C 180 250, 280 250, 280 290 L280 360 Z", fill="#2f2a22")
    el(root, "circle", cx=360, cy=318, r=56, fill="#8d8474")
    el(root, "circle", cx=360, cy=318, r=40, fill="#9e9584")
    el(root, "path", d="M0 360 C 200 350, 600 350, 800 360 L800 450 L0 450 Z", fill="#7f9f62")
    for x, color in [(520, "#e8774a"), (560, "#f4efe3"), (610, "#e8b04a"), (660, "#e8774a"), (720, "#f4efe3"), (120, "#f4efe3"), (70, "#e8b04a")]:
        el(root, "line", x1=x, y1=400, x2=x, y2=376, stroke="#5f824c", stroke_width=3)
        el(root, "circle", cx=x, cy=372, r=7, fill=color)
    return root


def pentecost() -> ET.Element:
    w, h = 800, 450
    root = canvas("pentecost", w, h, "Pentecost | 五旬节",
                  "A diverse group of people gathers in a room with arched windows; small flames rest above their "
                  "heads and lines of wind sweep through. | 一群不同肤色的人聚集在有拱窗的屋子里，每人头上有小火焰，风的线条从屋中吹过。")
    sky(root, w, h, "#efe4d0")
    for x in (120, 330, 540):
        el(root, "path", d=f"M{x} 220 L{x} 120 C {x} 80, {x + 140} 80, {x + 140} 120 L{x + 140} 220 Z", fill="#cfe0e6")
    el(root, "path", d="M0 300 L800 300 L800 450 L0 450 Z", fill="#c9b48a")
    for i in range(4):
        y = 70 + i * 26
        el(root, "path", d=f"M{40 + i * 30} {y} C 240 {y - 30}, 420 {y + 30}, {700 - i * 20} {y - 8}", fill="none",
           stroke="#9fb7c0", stroke_width=3, stroke_linecap="round", stroke_opacity=0.7)
    people = [(120, 390, 1.15), (210, 380, 1.1), (300, 392, 1.2), (390, 378, 1.1), (480, 390, 1.18), (570, 382, 1.1), (660, 392, 1.15),
              (165, 330, 0.95), (255, 324, 0.95), (345, 330, 0.95), (435, 324, 0.95), (525, 330, 0.95), (615, 324, 0.95)]
    for i, (x, y, s) in enumerate(sorted(people, key=lambda item: item[1])):
        person(root, x, y, ROBES[i % len(ROBES)], SKIN[(i * 2) % len(SKIN)], s)
        top = y - 66 * s - 14
        el(root, "path", d=f"M{x} {top - 18} C {x + 8} {top - 6}, {x + 7} {top + 4}, {x} {top + 6} C {x - 7} {top + 4}, {x - 8} {top - 6}, {x} {top - 18} Z", fill="#f0a93a")
    return root


def paul_ship() -> ET.Element:
    w, h = 800, 450
    root = canvas("paul-ship", w, h, "A ship bound for Rome | 驶往罗马的船",
                  "An ancient cargo ship with a square sail rides heavy waves toward a rocky island shore under a "
                  "stormy sky. | 风雨交加的天空下，一艘挂着方帆的古代货船在大浪中驶向多岩的海岛岸边。")
    sky(root, w, h, "#b9c4c8")
    for cx, cy, r in [(150, 60, 70), (280, 40, 60), (420, 70, 80), (580, 50, 70), (720, 70, 60)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#8b979d", fill_opacity=0.8)
    el(root, "path", d="M560 300 C 600 230, 680 220, 800 240 L800 320 L560 320 Z", fill="#6f6a5c")
    el(root, "path", d="M600 300 C 640 260, 700 256, 800 262 L800 320 L600 320 Z", fill="#8a8470")
    el(root, "path", d=path([(0, 450)] + wave(0, 800, 300, 12, 140, 0.8) + [(800, 450)]), fill="#3f6f80")
    el(root, "path", d=path([(0, 450)] + wave(0, 800, 360, 10, 180, 2.0) + [(800, 450)]), fill="#305a6a")
    ship = ET.SubElement(root, NS + "g", {"transform": "rotate(6 300 300)"})
    el(ship, "path", d="M150 300 C 180 330, 420 330, 460 290 L470 270 L140 276 Z", fill="#6b4a30")
    el(ship, "path", d="M140 276 L470 270 L466 280 L144 286 Z", fill="#8a6440")
    el(ship, "path", d="M460 290 C 480 270, 490 250, 486 236", fill="none", stroke="#6b4a30", stroke_width=8, stroke_linecap="round")
    el(ship, "line", x1=300, y1=276, x2=300, y2=120, stroke="#4a3020", stroke_width=6)
    el(ship, "path", d="M220 132 L380 132 C 392 180, 392 220, 380 250 L220 250 C 208 220, 208 180, 220 132 Z", fill="#ece0c6")
    el(ship, "path", d="M300 132 L300 250", stroke="#cdbb95", stroke_width=3)
    for i in range(6):
        x = 180 + i * 48
        el(ship, "line", x1=x, y1=296, x2=x - 22, y2=330, stroke="#4a3020", stroke_width=3)
    return root


# --- Third set: one scene for every remaining week -------------------------

def ground(root: ET.Element, y: float, color: str, amplitude: float = 14, length: float = 520, phase: float = 0.0) -> None:
    el(root, "path", d=path([(0, y + 20)] + wave(0, 800, y, amplitude, length, phase) + [(800, 450), (0, 450)]), fill=color)


def scene(name: str, title: str, desc: str, background: str) -> ET.Element:
    root = canvas(name, 800, 450, title, desc)
    sky(root, 800, 450, background)
    return root


def jacob_ladder() -> ET.Element:
    root = scene("jacob-ladder", "Jacob's dream | 雅各的梦",
                 "Under a starry sky, a man sleeps with his head on a stone while a stairway of light rises to heaven. | "
                 "星空下，一个人枕着石头睡觉，一道光的阶梯直通到天上。", "#1f2b46")
    for x, y in [(90, 60), (180, 120), (260, 40), (620, 70), (700, 130), (740, 40), (540, 30), (140, 200)]:
        el(root, "circle", cx=x, cy=y, r=2.2, fill="#f4efe3")
    el(root, "path", d="M360 330 L440 330 L520 0 L280 0 Z", fill="#f2d98c", fill_opacity=0.16)
    for i in range(12):
        y = 320 - i * 27
        half = 40 + i * 6
        el(root, "line", x1=400 - half, y1=y, x2=400 + half, y2=y, stroke="#f2d98c", stroke_width=4, stroke_opacity=0.9 - i * 0.05, stroke_linecap="round")
    el(root, "line", x1=360, y1=330, x2=280, y2=10, stroke="#f2d98c", stroke_width=4, stroke_opacity=0.6)
    el(root, "line", x1=440, y1=330, x2=520, y2=10, stroke="#f2d98c", stroke_width=4, stroke_opacity=0.6)
    ground(root, 340, "#3b3a30", 8, 600)
    el(root, "path", d="M240 384 C 250 366, 300 360, 330 370 C 360 364, 420 366, 440 384 Z", fill="#7b5d84")
    el(root, "circle", cx=232, cy=372, r=11, fill="#8a5f43")
    el(root, "path", d="M200 392 C 200 372, 236 368, 246 384 L246 392 Z", fill="#8d8474")
    return root


def lamb_altar() -> ET.Element:
    root = scene("lamb-altar", "Altar and offering | 祭坛与献祭",
                 "A lamb stands beside a bronze altar from which smoke rises before the curtained tabernacle. | "
                 "一只羊羔站在铜坛旁，坛上烟气升起，后面是挂着幔子的会幕。", "#efe2c8")
    el(root, "rect", x=420, y=120, width=300, height=200, fill="#e9dcc0", stroke="#b8a37a", stroke_width=2)
    for x in range(440, 720, 40):
        el(root, "line", x1=x, y1=120, x2=x, y2=320, stroke="#7b4f6b", stroke_width=10, stroke_opacity=0.35)
    ground(root, 320, "#d6bf8f", 6, 700)
    el(root, "rect", x=210, y=250, width=140, height=90, fill="#b5793f")
    el(root, "rect", x=200, y=240, width=160, height=16, fill="#9b6634")
    for x in (206, 354):
        el(root, "path", d=f"M{x - 6} 240 L{x} 226 L{x + 6} 240 Z", fill="#9b6634")
    for i, cx in enumerate((260, 290, 300)):
        el(root, "path", d=f"M{cx} 236 C {cx - 30} {200 - i * 20}, {cx + 30} {170 - i * 20}, {cx - 10} {110 - i * 20}", fill="none", stroke="#9a948a", stroke_width=10 - i * 2, stroke_linecap="round", stroke_opacity=0.5)
    group = ET.SubElement(root, NS + "g", {"transform": "translate(110 360)"})
    for dx, dy, r in [(-20, -20, 18), (0, -26, 20), (20, -20, 18), (0, -12, 18)]:
        el(group, "circle", cx=dx, cy=dy, r=r, fill="#fbf8f0")
    el(group, "circle", cx=36, cy=-34, r=11, fill="#e8ddd0")
    for x in (-18, 18):
        el(group, "line", x1=x, y1=0, x2=x, y2=22, stroke="#5a4e40", stroke_width=4, stroke_linecap="round")
    return root


def stone_tablets() -> ET.Element:
    root = scene("stone-tablets", "Words to remember | 当记念的话",
                 "Two stone tablets rest at the foot of a mountain, with the promised land spreading out in the distance. | "
                 "两块石版立在山脚，远处是展开的应许之地。", "#eae4d4")
    el(root, "path", d="M0 260 L180 120 L330 240 L520 90 L800 260 L800 450 L0 450 Z", fill="#b3a68a")
    ground(root, 280, "#9fb27f", 12, 600, 1.0)
    ground(root, 330, "#c8b48a", 8, 700, 2.0)
    for x in (300, 410):
        el(root, "path", d=f"M{x} 380 L{x} 250 C {x} 214, {x + 90} 214, {x + 90} 250 L{x + 90} 380 Z", fill="#8d8474")
        el(root, "path", d=f"M{x + 8} 372 L{x + 8} 254 C {x + 8} 226, {x + 82} 226, {x + 82} 254 L{x + 82} 372 Z", fill="#a39883")
        for i in range(5):
            y = 266 + i * 20
            el(root, "line", x1=x + 22, y1=y, x2=x + 68 - (i % 2) * 14, y2=y, stroke="#6b6355", stroke_width=4, stroke_linecap="round")
    return root


def jericho_walls() -> ET.Element:
    root = scene("jericho-walls", "Around the walls of Jericho | 绕行耶利哥城",
                 "A line of people carrying horns walks around a walled city on a hill. | 一行人拿着角号，绕着山上有城墙的城行走。", "#f1e3c6")
    ground(root, 250, "#d3b98a", 16, 500)
    el(root, "rect", x=230, y=140, width=340, height=120, fill="#c4aa7e")
    for x in range(230, 570, 34):
        el(root, "rect", x=x, y=124, width=20, height=20, fill="#c4aa7e")
    for x in (260, 360, 460):
        el(root, "rect", x=x, y=180, width=18, height=24, fill="#7a5537")
    el(root, "rect", x=380, y=210, width=40, height=50, fill="#5a4630")
    ground(root, 300, "#b89c6a", 10, 400, 1.0)
    for i in range(9):
        x = 80 + i * 76
        person(root, x, 380 + (i % 2) * 8, ROBES[i % len(ROBES)], SKIN[i % len(SKIN)], 0.9)
        if i % 2 == 0:
            el(root, "path", d=f"M{x + 6} {330 + (i % 2) * 8} C {x + 26} {316}, {x + 36} {312}, {x + 44} {300}", fill="none", stroke="#e1c27a", stroke_width=5, stroke_linecap="round")
    return root


def anointing() -> ET.Element:
    root = scene("anointing", "Oil for a new king | 膏立新王",
                 "An old prophet pours oil from a horn onto the head of a young shepherd kneeling before him. | "
                 "年老的先知用角里的油，倒在跪在面前的年轻牧人头上。", "#eef0e2")
    ground(root, 330, "#9fb27f", 10, 600)
    person(root, 470, 380, "#7b5d84", "#a07052", 1.7)
    el(root, "path", d="M430 250 C 420 236, 410 232, 396 238 L392 226 C 410 214, 430 222, 440 240 Z", fill="#d9c08e")
    el(root, "path", d="M394 232 C 390 250, 388 262, 390 270", fill="none", stroke="#e1b444", stroke_width=4, stroke_linecap="round")
    group = ET.SubElement(root, NS + "g", {"transform": "translate(380 380)"})
    el(group, "path", d="M-20 0 L-16 -40 C -10 -52, 14 -52, 18 -40 L22 0 Z", fill="#4f6b52")
    el(group, "circle", cx=0, cy=-64, r=12, fill="#b07a55")
    el(group, "path", d="M-40 0 L-20 -10 L-16 0 Z", fill="#4f6b52")
    for x, y in [(160, 360), (210, 372), (250, 356)]:
        for dx, r in [(-10, 12), (6, 14), (20, 11)]:
            el(root, "circle", cx=x + dx, cy=y, r=r, fill="#fbf8f0")
        el(root, "circle", cx=x + 34, cy=y - 6, r=7, fill="#3e3a33")
    return root


def golden_calf() -> ET.Element:
    root = scene("golden-calf", "A divided kingdom | 分裂的王国",
                 "A golden calf stands on a stone pedestal where a road splits in two directions, toward two distant cities. | "
                 "一尊金牛犊立在石座上，脚下的道路分成两条，通往远处两座城。", "#efe5d0")
    ground(root, 260, "#c8b48a", 10, 600)
    for x in (140, 640):
        el(root, "rect", x=x - 50, y=200, width=100, height=60, fill="#bfa274")
        el(root, "rect", x=x - 20, y=176, width=40, height=30, fill="#bfa274")
    el(root, "path", d="M400 450 L380 330 C 360 300, 220 280, 150 262 L170 258 C 240 272, 380 290, 400 320 C 420 290, 560 272, 630 258 L650 262 C 580 280, 440 300, 420 330 L420 450 Z", fill="#e3d0a6")
    el(root, "rect", x=340, y=290, width=120, height=50, fill="#8d8474")
    group = ET.SubElement(root, NS + "g", {"transform": "translate(400 290)"})
    el(group, "path", d="M-46 0 L-44 -34 C -40 -50, 30 -50, 40 -36 L44 0 L32 0 L30 -20 L-30 -20 L-32 0 Z", fill="#e1b444")
    el(group, "circle", cx=44, cy=-46, r=14, fill="#e1b444")
    el(group, "path", d="M36 -58 L30 -72 L42 -60 Z M52 -58 L58 -72 L48 -60 Z", fill="#c99a2e")
    return root


def burning_coal() -> ET.Element:
    root = scene("burning-coal", "A coal from the altar | 坛上的红炭",
                 "Smoke fills a temple hall as a glowing coal is lifted from the altar with tongs. | "
                 "圣殿中烟云缭绕，有人用火剪从坛上夹起一块烧红的炭。", "#e7e0d4")
    for x in (150, 650):
        el(root, "rect", x=x - 30, y=60, width=60, height=330, fill="#c9bea8")
    for cx, cy, r in [(300, 120, 80), (420, 90, 100), (540, 130, 80), (380, 180, 70)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#ffffff", fill_opacity=0.55)
    el(root, "path", d="M0 390 L800 390 L800 450 L0 450 Z", fill="#b39a6c")
    el(root, "rect", x=320, y=300, width=160, height=90, fill="#b5793f")
    el(root, "rect", x=310, y=292, width=180, height=14, fill="#9b6634")
    for x in (350, 380, 420, 450):
        el(root, "circle", cx=x, cy=290, r=12, fill="#e8742f")
    el(root, "line", x1=520, y1=170, x2=432, y2=258, stroke="#6b4e33", stroke_width=6, stroke_linecap="round")
    el(root, "line", x1=532, y1=180, x2=444, y2=268, stroke="#6b4e33", stroke_width=6, stroke_linecap="round")
    el(root, "circle", cx=436, cy=266, r=13, fill="#f0a93a")
    el(root, "circle", cx=436, cy=266, r=26, fill="#f0a93a", fill_opacity=0.25)
    return root


def exile_road() -> ET.Element:
    root = scene("exile-road", "The road into exile | 被掳之路",
                 "A long line of people carrying bundles walks along a dusty road away from their homeland under a pale sky. | "
                 "灰白的天空下，一长列背着包袱的人沿着尘土飞扬的路离开故土。", "#e9e3d6")
    ground(root, 230, "#c7b089", 14, 600)
    el(root, "path", d="M0 330 C 200 300, 500 280, 800 240 L800 280 C 500 320, 200 350, 0 380 Z", fill="#e1cfa6")
    for i in range(10):
        x = 60 + i * 72
        y = 368 - i * 11
        s = 1.0 - i * 0.05
        person(root, x, y, ROBES[i % len(ROBES)], SKIN[i % len(SKIN)], s)
        el(root, "circle", cx=x + 10 * s, cy=y - 44 * s, r=10 * s, fill="#d9c7a1")
    return root


def water_tunnel() -> ET.Element:
    root = scene("water-tunnel", "A tunnel for water | 引水的隧道",
                 "Inside a narrow rock-cut tunnel, a small lamp lights water flowing toward the city. | "
                 "一条凿在岩石里的狭窄隧道中，一盏小灯照着流向城里的水。", "#3d342b")
    el(root, "path", d="M120 450 L200 120 C 260 60, 540 60, 600 120 L680 450 Z", fill="#7a6a55")
    el(root, "path", d="M220 450 L270 160 C 310 110, 490 110, 530 160 L580 450 Z", fill="#2a241e")
    el(root, "path", d="M260 450 C 300 400, 500 400, 540 450 Z", fill="#4f8a9a")
    for i in range(4):
        y = 420 + i * 8
        el(root, "path", d=f"M{290 + i * 10} {y} C 360 {y - 10}, 440 {y - 10}, {510 - i * 10} {y}", fill="none", stroke="#a9d3dc", stroke_width=2, stroke_opacity=0.7)
    for x, y in [(160, 200), (180, 300), (620, 210), (640, 320), (300, 90), (500, 90)]:
        el(root, "line", x1=x, y1=y, x2=x + 20, y2=y + 10, stroke="#5a4e40", stroke_width=3, stroke_linecap="round")
    el(root, "circle", cx=400, cy=300, r=70, fill="#f2c56b", fill_opacity=0.15)
    el(root, "path", d="M370 330 C 370 312, 430 312, 434 326 L446 322 L440 334 C 420 344, 380 344, 370 330 Z", fill="#b5793f")
    el(root, "path", d="M442 322 C 438 308, 442 298, 448 290 C 454 300, 456 312, 450 322 Z", fill="#f0a93a")
    return root


def found_scroll() -> ET.Element:
    root = scene("found-scroll", "A scroll found in the temple | 在圣殿中找到的书卷",
                 "An old scroll lies partly unrolled among stones and dust, lit by a beam of light. | "
                 "一卷古老的书卷半展开地躺在石块与尘土之间，被一束光照亮。", "#4a4038")
    el(root, "path", d="M300 0 L500 0 L620 450 L180 450 Z", fill="#f2d98c", fill_opacity=0.14)
    el(root, "path", d="M0 340 L800 340 L800 450 L0 450 Z", fill="#6b5d4c")
    for x, y, w2 in [(60, 300, 120), (620, 290, 140), (180, 320, 90), (560, 320, 80)]:
        el(root, "rect", x=x, y=y, width=w2, height=46, rx=4, fill="#8d7f6a")
    el(root, "path", d="M280 330 L520 330 L520 380 L280 380 Z", fill="#efe2c2")
    el(root, "circle", cx=280, cy=355, r=26, fill="#d9c69c")
    el(root, "circle", cx=520, cy=355, r=26, fill="#d9c69c")
    el(root, "circle", cx=280, cy=355, r=8, fill="#8a6a48")
    el(root, "circle", cx=520, cy=355, r=8, fill="#8a6a48")
    for i in range(3):
        y = 344 + i * 12
        el(root, "line", x1=320, y1=y, x2=480, y2=y, stroke="#8f7a55", stroke_width=3, stroke_linecap="round", stroke_opacity=0.7)
    return root


def ruined_city() -> ET.Element:
    root = scene("ruined-city", "Jerusalem in ruins | 荒凉的耶路撒冷",
                 "Broken walls and fallen stones lie under drifting smoke, with a single tree still standing. | "
                 "飘散的烟雾下，城墙坍塌、石块散落，只剩一棵树仍然站着。", "#d8d2c8")
    for cx, cy, r in [(200, 80, 70), (320, 60, 60), (460, 90, 80)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#9a948a", fill_opacity=0.45)
    ground(root, 300, "#a8987a", 8, 600)
    el(root, "path", d="M80 300 L80 200 L130 200 L130 170 L160 170 L170 230 L220 220 L240 300 Z", fill="#8d8474")
    el(root, "path", d="M420 300 L430 180 L470 186 L480 150 L520 160 L540 240 L600 230 L620 300 Z", fill="#8d8474")
    for x, y in [(270, 320), (300, 330), (340, 318), (380, 334), (650, 320), (690, 330), (240, 340)]:
        el(root, "rect", x=x, y=y, width=34, height=20, rx=3, fill="#a39883", transform=f"rotate({(x % 7) * 5 - 15} {x + 17} {y + 10})")
    el(root, "line", x1=720, y1=310, x2=720, y2=220, stroke="#5a4630", stroke_width=8)
    for cx, cy, r in [(720, 200, 30), (700, 220, 22), (742, 222, 22)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#6f8f55")
    return root


def potter_wheel() -> ET.Element:
    root = scene("potter-wheel", "At the potter's house | 在窑匠家里",
                 "A potter shapes a clay vessel on a turning wheel, with finished jars on a shelf behind him. | "
                 "窑匠在转动的轮子上塑造陶器，身后的架子上放着做好的罐子。", "#efe1cb")
    el(root, "rect", x=80, y=120, width=640, height=12, fill="#8e6644")
    for x, hgt in [(120, 70), (200, 90), (280, 60), (560, 80), (640, 70)]:
        el(root, "path", d=f"M{x - 22} 120 C {x - 34} {120 - hgt * 0.6}, {x - 10} {120 - hgt}, {x} {120 - hgt} C {x + 10} {120 - hgt}, {x + 34} {120 - hgt * 0.6}, {x + 22} 120 Z", fill="#b5793f")
    el(root, "path", d="M0 360 L800 360 L800 450 L0 450 Z", fill="#9b7a55")
    el(root, "rect", x=330, y=300, width=140, height=16, rx=8, fill="#6b4e33")
    el(root, "rect", x=392, y=316, width=16, height=60, fill="#5a4630")
    el(root, "path", d="M360 300 C 352 270, 372 240, 388 232 L412 232 C 428 240, 448 270, 440 300 Z", fill="#c48a52")
    el(root, "path", d="M384 232 C 384 222, 416 222, 416 232 Z", fill="#a86f3c")
    group = ET.SubElement(root, NS + "g", {"transform": "translate(540 380)"})
    el(group, "path", d="M-30 0 L-24 -70 C -18 -86, 18 -86, 24 -70 L30 0 Z", fill="#4f6b52")
    el(group, "circle", cx=0, cy=-98, r=14, fill="#8a5f43")
    el(root, "line", x1=520, y1=316, x2=446, y2=280, stroke="#8a5f43", stroke_width=7, stroke_linecap="round")
    return root


def dry_bones() -> ET.Element:
    root = scene("dry-bones", "The valley of dry bones | 枯骨的平原",
                 "A wide valley scattered with dry bones, while a fresh wind blows in from the hills and green shoots appear. | "
                 "宽阔的山谷里散满枯骨，一阵新风从山间吹来，地上冒出青绿的嫩芽。", "#ece3cf")
    el(root, "path", d="M0 220 L140 150 L300 210 L460 140 L620 200 L800 150 L800 450 L0 450 Z", fill="#c2ad87")
    ground(root, 280, "#d9c69c", 10, 700)
    for x, y, a in [(120, 330, 10), (220, 360, -20), (320, 320, 30), (420, 370, -5), (540, 340, 15), (640, 380, -30), (180, 400, 40), (480, 410, -15)]:
        el(root, "path", d=f"M{x - 26} {y} L{x + 26} {y}", stroke="#f6f0e1", stroke_width=7, stroke_linecap="round", transform=f"rotate({a} {x} {y})")
        el(root, "circle", cx=x - 26, cy=y, r=5, fill="#f6f0e1", transform=f"rotate({a} {x} {y})")
        el(root, "circle", cx=x + 26, cy=y, r=5, fill="#f6f0e1", transform=f"rotate({a} {x} {y})")
    for i in range(4):
        y = 120 + i * 28
        el(root, "path", d=f"M{40 + i * 40} {y} C 220 {y - 30}, 420 {y + 30}, {760 - i * 30} {y - 10}", fill="none", stroke="#8fb3bb", stroke_width=4, stroke_linecap="round", stroke_opacity=0.7)
    for x in (260, 380, 600, 700):
        el(root, "path", d=f"M{x} 440 C {x - 2} 428, {x - 10} 420, {x - 16} 416 M{x} 440 C {x + 2} 428, {x + 10} 420, {x + 16} 416", fill="none", stroke="#6f9f4c", stroke_width=3, stroke_linecap="round")
    return root


def royal_scepter() -> ET.Element:
    root = scene("royal-scepter", "The golden scepter | 金杖",
                 "In a Persian throne room, a king on a raised throne extends a golden scepter toward a queen who approaches. | "
                 "在波斯宫殿里，坐在高位上的王向走近的王后伸出金杖。", "#e9dfcf")
    for x in (80, 240, 560, 720):
        el(root, "rect", x=x - 18, y=60, width=36, height=330, fill="#cfc2a6")
        el(root, "rect", x=x - 30, y=50, width=60, height=16, fill="#b8a37a")
    el(root, "path", d="M0 390 L800 390 L800 450 L0 450 Z", fill="#9b7a55")
    for i in range(3):
        el(root, "rect", x=420 + i * 20, y=330 + i * 20, width=260 - i * 40, height=20, fill="#b39a6c")
    el(root, "rect", x=520, y=200, width=110, height=130, rx=8, fill="#7b4f6b")
    person(root, 575, 330, "#3f6c7a", "#a07052", 1.3)
    el(root, "path", d="M558 240 L568 226 L576 240 L584 226 L594 240 Z", fill="#e1b444")
    el(root, "line", x1=548, y1=280, x2=430, y2=250, stroke="#e1b444", stroke_width=5, stroke_linecap="round")
    el(root, "circle", cx=428, cy=250, r=8, fill="#e1b444")
    person(root, 360, 390, "#8b4b45", "#c08a63", 1.35)
    el(root, "path", d="M342 300 L350 288 L360 300 L370 288 L378 300 Z", fill="#e1b444")
    return root


def sunrise_field() -> ET.Element:
    root = scene("sunrise-field", "The sun of righteousness | 公义的日头",
                 "A large sun rises over green fields, its rays spreading like wings, while young calves leap in the pasture. | "
                 "一轮大日头从青绿的田野上升起，光芒像翅膀一样展开，小牛犊在草场上跳跃。", "#f7e4c3")
    for i in range(11):
        angle = math.radians(190 + i * 16)
        el(root, "line", x1=400, y1=300, x2=400 + 420 * math.cos(angle), y2=300 + 420 * math.sin(angle), stroke="#f3c47a", stroke_width=12, stroke_opacity=0.35, stroke_linecap="round")
    el(root, "circle", cx=400, cy=300, r=80, fill="#f0a93a")
    ground(root, 300, "#9fbf7a", 14, 600)
    ground(root, 350, "#7ea660", 10, 400, 2.0)
    for x, y, jump in [(220, 380, 0), (300, 360, 1), (560, 380, 0)]:
        group = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y - jump * 20}) rotate({-12 * jump})"})
        el(group, "path", d="M-30 0 C -32 -24, 22 -26, 26 -6 L24 0 Z", fill="#a0703e")
        el(group, "circle", cx=30, cy=-16, r=10, fill="#a0703e")
        for lx in (-22, -10, 8, 18):
            el(group, "line", x1=lx, y1=0, x2=lx + (4 if jump else 0), y2=18, stroke="#6b4e33", stroke_width=4, stroke_linecap="round")
    return root


def whirlwind() -> ET.Element:
    root = scene("whirlwind", "Out of the whirlwind | 从旋风中",
                 "A man sits on an ash heap beneath a vast swirling storm that fills the sky. | "
                 "一个人坐在炉灰中，上方是充满天空的巨大旋风。", "#cfcfc7")
    for i in range(7):
        r = 40 + i * 30
        el(root, "path", d=f"M{400 - r} {150} C {400 - r} {150 - r * 0.7}, {400 + r} {150 - r * 0.7}, {400 + r} {150 + 10}",
           fill="none", stroke="#6f7c83", stroke_width=10 - i, stroke_linecap="round", stroke_opacity=0.75 - i * 0.07)
    el(root, "path", d="M380 170 C 360 230, 420 260, 400 330", fill="none", stroke="#6f7c83", stroke_width=12, stroke_linecap="round", stroke_opacity=0.5)
    ground(root, 350, "#8d8474", 6, 700)
    el(root, "path", d="M280 380 C 300 350, 380 350, 400 380 Z", fill="#6b6355")
    group = ET.SubElement(root, NS + "g", {"transform": "translate(340 370)"})
    el(group, "path", d="M-24 0 C -26 -30, -14 -46, 0 -48 C 14 -46, 24 -30, 22 0 Z", fill="#8d7f6a")
    el(group, "circle", cx=0, cy=-60, r=12, fill="#a07052")
    return root


def seasons_tree() -> ET.Element:
    root = scene("seasons-tree", "A time for everything | 凡事都有定时",
                 "A single tree is shown through four seasons side by side: blossom, full leaf, falling leaves, and bare branches in snow. | "
                 "同一棵树并排呈现四季：开花、繁茂、落叶，以及雪中光秃的枝条。", "#f2ebdc")
    seasons = [("#f6dfe2", "#e9a7b5"), ("#dfeccf", "#6f9f4c"), ("#f4e2c4", "#d9822b"), ("#e6ecef", None)]
    for i, (back, leaf) in enumerate(seasons):
        x0 = 20 + i * 192
        el(root, "rect", x=x0, y=40, width=180, height=370, rx=12, fill=back)
        cx = x0 + 90
        el(root, "rect", x=cx - 7, y=250, width=14, height=120, fill="#6b4e33")
        el(root, "path", d=f"M{cx} 280 L{cx - 40} 220 M{cx} 260 L{cx + 44} 200 M{cx} 300 L{cx + 30} 250", stroke="#6b4e33", stroke_width=6, stroke_linecap="round", fill="none")
        if leaf:
            for dx, dy, r in [(-40, 210, 30), (0, 180, 40), (44, 200, 32), (20, 240, 26), (-20, 250, 24)]:
                el(root, "circle", cx=cx + dx, cy=dy, r=r * (0.7 if i == 2 else 1), fill=leaf, fill_opacity=0.9)
        else:
            for dx in (-40, -10, 30, 50):
                el(root, "circle", cx=cx + dx, cy=120 + (dx % 3) * 30, r=3, fill="#ffffff")
            el(root, "rect", x=x0, y=362, width=180, height=48, rx=10, fill="#ffffff")
        if i == 2:
            for dx, dy in [(-50, 330), (30, 350), (60, 310)]:
                el(root, "circle", cx=cx + dx, cy=dy, r=5, fill=leaf)
        el(root, "rect", x=x0, y=370, width=180, height=8, fill="#8e6644", fill_opacity=0.5)
    return root


def jordan_dove() -> ET.Element:
    root = scene("jordan-dove", "At the Jordan River | 在约旦河边",
                 "A dove descends through an opening in the clouds above a figure standing in a river. | "
                 "云层裂开，一只鸽子降下，下方有一人站在河水中。", "#e6eef0")
    el(root, "path", d="M330 0 L470 0 L440 300 L360 300 Z", fill="#f2d98c", fill_opacity=0.3)
    for cx, cy, r in [(220, 60, 70), (580, 60, 70), (300, 30, 50), (500, 30, 50)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#ffffff", fill_opacity=0.8)
    ground(root, 260, "#a9bf8a", 10, 600)
    el(root, "path", d="M0 330 C 200 300, 600 300, 800 330 L800 400 C 600 380, 200 380, 0 410 Z", fill="#8cbac6")
    group = ET.SubElement(root, NS + "g", {"transform": "translate(400 140)"})
    el(group, "path", d="M0 0 C -40 -20, -70 -10, -80 6 C -50 4, -30 10, 0 14 C 30 10, 50 4, 80 6 C 70 -10, 40 -20, 0 0 Z", fill="#ffffff")
    el(group, "path", d="M-6 10 C -4 28, 4 28, 6 10 Z", fill="#ffffff")
    el(group, "circle", cx=0, cy=4, r=7, fill="#ffffff")
    person(root, 400, 360, "#e9dcc0", "#a07052", 1.3)
    el(root, "path", d="M360 350 C 380 342, 420 342, 440 350", fill="none", stroke="#cfe6ee", stroke_width=3)
    return root


def galilee_boat() -> ET.Element:
    root = scene("galilee-boat", "Fishing on the Sea of Galilee | 在加利利海打鱼",
                 "A small fishing boat with a net floats on a calm lake ringed by green hills in morning light. | "
                 "晨光中，一艘带着渔网的小船漂在宁静的湖面上，四周是青翠的山丘。", "#f3e9d6")
    el(root, "circle", cx=640, cy=110, r=40, fill="#f0b25a")
    el(root, "path", d="M0 220 C 150 150, 300 190, 420 170 C 560 150, 680 190, 800 170 L800 260 L0 260 Z", fill="#8fae73")
    el(root, "path", d="M0 250 L800 250 L800 450 L0 450 Z", fill="#7fb0bd")
    for i in range(6):
        y = 280 + i * 26
        el(root, "line", x1=60 + i * 30, y1=y, x2=200 + i * 40, y2=y, stroke="#e3f1f4", stroke_width=2, stroke_opacity=0.6)
    el(root, "path", d="M280 330 C 300 360, 480 360, 520 330 L530 316 L270 318 Z", fill="#7a4a2b")
    el(root, "line", x1=400, y1=318, x2=400, y2=200, stroke="#4a3020", stroke_width=5)
    el(root, "path", d="M404 206 L460 300 L404 304 Z", fill="#ece0c6")
    el(root, "path", d="M520 330 C 560 340, 600 360, 640 400", fill="none", stroke="#5a4630", stroke_width=2)
    for i in range(6):
        el(root, "path", d=f"M{540 + i * 18} {340 + i * 10} L{560 + i * 18} {380 + i * 6}", stroke="#5a4630", stroke_width=1.5)
    person(root, 340, 322, "#4f6b52", "#8a5f43", 0.8)
    person(root, 470, 322, "#a0703e", "#b07a55", 0.8)
    return root


def sower() -> ET.Element:
    root = scene("sower", "The sower | 撒种的比喻",
                 "A sower scatters seed across a field showing a hard path, rocky ground, thorns, and good soil with tall grain. | "
                 "撒种的人把种子撒在田里，可以看见硬路、石头地、荆棘和长出高高麦穗的好土。", "#f3e6c8")
    el(root, "path", d="M0 250 L800 250 L800 450 L0 450 Z", fill="#b39a6c")
    el(root, "path", d="M0 290 L800 270 L800 300 L0 320 Z", fill="#d8c8a2")
    for x in range(60, 260, 40):
        el(root, "circle", cx=x, cy=380 + (x % 3) * 10, r=14, fill="#9a948a")
    for x in range(300, 480, 30):
        el(root, "path", d=f"M{x} 420 L{x + 10} 360 L{x + 20} 420 M{x - 6} 390 L{x + 26} 380", stroke="#5f7a45", stroke_width=3, fill="none")
    for x in range(520, 780, 22):
        el(root, "line", x1=x, y1=430, x2=x, y2=340, stroke="#c99a35", stroke_width=4, stroke_linecap="round")
        el(root, "path", d=f"M{x - 5} 345 C {x - 6} 326, {x + 6} 326, {x + 5} 345 Z", fill="#e1b444")
    group = ET.SubElement(root, NS + "g", {"transform": "translate(160 280)"})
    el(group, "path", d="M-20 0 L-16 -60 C -10 -76, 16 -76, 22 -60 L26 0 Z", fill="#6d7f4a")
    el(group, "circle", cx=2, cy=-88, r=13, fill="#8a5f43")
    el(group, "path", d="M22 -56 C 48 -66, 70 -58, 84 -44", fill="none", stroke="#8a5f43", stroke_width=6, stroke_linecap="round")
    for dx, dy in [(100, -40), (120, -20), (140, -46), (160, -10), (110, 0)]:
        el(root, "circle", cx=160 + dx, cy=280 + dy, r=3, fill="#7a5537")
    return root


def palm_road() -> ET.Element:
    root = scene("palm-road", "The road to Jerusalem | 往耶路撒冷的路",
                 "Palm branches lie along a road that climbs toward a walled city on a hill. | 棕树枝铺在通往山上那座有城墙之城的路上。", "#f4e6cc")
    el(root, "path", d="M420 120 L700 120 L700 200 L420 200 Z", fill="#d9c08e")
    for x in range(420, 700, 30):
        el(root, "rect", x=x, y=106, width=18, height=16, fill="#d9c08e")
    el(root, "path", d="M540 200 L540 160 C 540 140, 580 140, 580 160 L580 200 Z", fill="#7a5537")
    ground(root, 200, "#c7b089", 10, 600)
    el(root, "path", d="M100 450 C 260 380, 420 300, 560 210 L580 214 C 460 310, 340 390, 260 450 Z", fill="#e7d5ad")
    for x, y, a in [(170, 420, -30), (240, 390, -20), (300, 360, -40), (360, 320, -25), (420, 290, -35), (470, 258, -20)]:
        el(root, "path", d=f"M{x - 34} {y} C {x - 10} {y - 6}, {x + 10} {y - 6}, {x + 34} {y}", fill="none", stroke="#4f7a3a", stroke_width=4, transform=f"rotate({a} {x} {y})")
        for k in range(-3, 4):
            el(root, "line", x1=x + k * 9, y1=y - 2, x2=x + k * 9 + 6, y2=y - 14, stroke="#6f9f4c", stroke_width=3, stroke_linecap="round", transform=f"rotate({a} {x} {y})")
    el(root, "line", x1=90, y1=330, x2=90, y2=170, stroke="#7a5537", stroke_width=10)
    for a in range(0, 360, 45):
        el(root, "path", d=f"M90 170 C 120 160, 150 170, 170 190", fill="none", stroke="#4f7a3a", stroke_width=6, stroke_linecap="round", transform=f"rotate({a} 90 170)")
    return root


def chariot_road() -> ET.Element:
    root = scene("chariot-road", "A chariot on the desert road | 旷野路上的车",
                 "A traveler reads a scroll in a chariot on a desert road while another man runs alongside. | "
                 "旷野的路上，一位旅人坐在车上读书卷，另一人在车旁奔跑。", "#f3e2c0")
    ground(root, 260, "#e0c592", 12, 700)
    el(root, "path", d="M0 360 C 300 330, 500 330, 800 300 L800 340 C 500 370, 300 370, 0 400 Z", fill="#ecdab2")
    el(root, "path", d="M360 330 L520 330 L540 270 L380 270 Z", fill="#a0703e")
    el(root, "circle", cx=420, cy=340, r=30, fill="none", stroke="#5a4630", stroke_width=6)
    el(root, "line", x1=390, y1=340, x2=450, y2=340, stroke="#5a4630", stroke_width=3)
    el(root, "line", x1=420, y1=310, x2=420, y2=370, stroke="#5a4630", stroke_width=3)
    el(root, "line", x1=540, y1=300, x2=620, y2=310, stroke="#5a4630", stroke_width=4)
    group = ET.SubElement(root, NS + "g", {"transform": "translate(650 340)"})
    el(group, "path", d="M-40 0 L-36 -30 C -30 -40, 30 -40, 36 -30 L40 0 Z", fill="#8a6a48")
    el(group, "path", d="M30 -34 L50 -60 L60 -54 L44 -28 Z", fill="#8a6a48")
    for x in (-30, -14, 14, 30):
        el(group, "line", x1=x, y1=0, x2=x + 4, y2=30, stroke="#6b4e33", stroke_width=4, stroke_linecap="round")
    person(root, 460, 280, "#7b4f6b", "#6e4a33", 1.0)
    el(root, "rect", x=470, y=232, width=28, height=10, rx=4, fill="#efe2c2")
    person(root, 300, 390, "#4f6b52", "#b07a55", 1.05)
    return root


def table_fellowship() -> ET.Element:
    root = scene("table-fellowship", "One family at one table | 同坐一桌的一家人",
                 "People of many backgrounds sit together around a long table sharing bread and fruit. | "
                 "不同背景的人围坐在一张长桌旁，一同分享饼和水果。", "#f1e5d1")
    el(root, "rect", x=100, y=260, width=600, height=26, rx=6, fill="#8e6644")
    el(root, "rect", x=130, y=286, width=16, height=90, fill="#6b4e33")
    el(root, "rect", x=654, y=286, width=16, height=90, fill="#6b4e33")
    for i, x in enumerate((160, 260, 360, 460, 560, 640)):
        person(root, x, 262, ROBES[i % len(ROBES)], SKIN[(i * 3) % len(SKIN)], 1.05)
    el(root, "rect", x=100, y=250, width=600, height=14, rx=6, fill="#a87a50")
    for x in (220, 420, 600):
        el(root, "path", d=f"M{x - 30} 250 C {x - 30} 226, {x + 30} 226, {x + 30} 250 Z", fill="#c98a45")
    for x, c in [(320, "#8b4b45"), (336, "#e1b444"), (512, "#6f9f4c"), (528, "#8b4b45")]:
        el(root, "circle", cx=x, cy=242, r=9, fill=c)
    el(root, "path", d="M0 376 L800 376 L800 450 L0 450 Z", fill="#c9b48a")
    return root


def jars_of_clay() -> ET.Element:
    root = scene("jars-of-clay", "Treasure in jars of clay | 瓦器里的宝贝",
                 "Three plain clay jars sit on a dark shelf; one is cracked, and warm light shines out through the crack. | "
                 "幽暗的架子上放着三个朴素的瓦器，其中一个有裂缝，温暖的光从裂缝中透出来。", "#2f2a26")
    el(root, "path", d="M0 330 L800 330 L800 450 L0 450 Z", fill="#5a4630")
    el(root, "rect", x=0, y=322, width=800, height=12, fill="#6b4e33")
    el(root, "circle", cx=400, cy=230, r=170, fill="#f2c56b", fill_opacity=0.12)
    for x, hgt, light in [(220, 150, False), (400, 190, True), (580, 140, False)]:
        el(root, "path", d=f"M{x - 40} 322 C {x - 70} {322 - hgt * 0.5}, {x - 40} {322 - hgt}, {x - 18} {322 - hgt} L{x + 18} {322 - hgt} C {x + 40} {322 - hgt}, {x + 70} {322 - hgt * 0.5}, {x + 40} 322 Z", fill="#a86f3c")
        el(root, "rect", x=x - 22, y=322 - hgt - 12, width=44, height=14, rx=4, fill="#8f5c2f")
        if light:
            el(root, "path", d=f"M{x - 4} {322 - hgt + 30} L{x + 10} {322 - hgt + 70} L{x - 6} {322 - hgt + 100} L{x + 8} {322 - hgt + 140}", fill="none", stroke="#fbe08a", stroke_width=5, stroke_linecap="round")
            for i in range(5):
                angle = math.radians(-30 + i * 15)
                el(root, "line", x1=x + 14, y1=322 - hgt + 80, x2=x + 14 + 120 * math.cos(angle), y2=322 - hgt + 80 + 120 * math.sin(angle), stroke="#fbe08a", stroke_width=3, stroke_opacity=0.35, stroke_linecap="round")
    return root


def anchor_hope() -> ET.Element:
    root = scene("anchor-hope", "An anchor for the soul | 灵魂的锚",
                 "A large anchor holds fast on the sea floor while waves move above it, with a ship riding safely at the surface. | "
                 "一只大锚牢牢抓住海底，上方海浪起伏，水面上的船安稳地停着。", "#c9dde3")
    el(root, "path", d=path([(0, 450)] + wave(0, 800, 120, 10, 160) + [(800, 450)]), fill="#5f97a8")
    el(root, "path", d=path([(0, 450)] + wave(0, 800, 200, 6, 220, 1.0) + [(800, 450)]), fill="#3f7385")
    el(root, "path", d="M0 400 C 200 380, 600 390, 800 400 L800 450 L0 450 Z", fill="#c2ad87")
    el(root, "path", d="M330 108 C 350 124, 450 124, 470 108 L476 96 L324 96 Z", fill="#7a4a2b")
    el(root, "line", x1=400, y1=96, x2=400, y2=40, stroke="#4a3020", stroke_width=4)
    el(root, "path", d="M404 44 L440 90 L404 92 Z", fill="#ece0c6")
    el(root, "path", d="M400 118 C 380 200, 420 260, 400 300", fill="none", stroke="#3a3530", stroke_width=3, stroke_dasharray="6 4")
    el(root, "circle", cx=400, cy=304, r=10, fill="none", stroke="#3a3530", stroke_width=5)
    el(root, "line", x1=400, y1=314, x2=400, y2=400, stroke="#3a3530", stroke_width=10, stroke_linecap="round")
    el(root, "line", x1=370, y1=332, x2=430, y2=332, stroke="#3a3530", stroke_width=8, stroke_linecap="round")
    el(root, "path", d="M340 370 C 350 400, 380 410, 400 410 C 420 410, 450 400, 460 370", fill="none", stroke="#3a3530", stroke_width=10, stroke_linecap="round")
    el(root, "path", d="M332 362 L346 360 L342 376 Z M468 362 L454 360 L458 376 Z", fill="#3a3530")
    return root


def lamp_light() -> ET.Element:
    root = scene("lamp-light", "Light in the house | 屋中的光",
                 "A lamp on a stand fills a simple room with warm light, pushing back the darkness at the edges. | "
                 "灯台上的灯把朴素的屋子照得温暖明亮，把暗处推到墙角。", "#2c2722")
    el(root, "circle", cx=400, cy=190, r=300, fill="#f2c56b", fill_opacity=0.10)
    el(root, "circle", cx=400, cy=190, r=180, fill="#f2c56b", fill_opacity=0.14)
    el(root, "circle", cx=400, cy=190, r=90, fill="#f2c56b", fill_opacity=0.2)
    el(root, "path", d="M0 360 L800 360 L800 450 L0 450 Z", fill="#6b4e33")
    el(root, "rect", x=392, y=210, width=16, height=150, fill="#8f5c2f")
    el(root, "path", d="M360 360 L440 360 L420 340 L380 340 Z", fill="#8f5c2f")
    el(root, "path", d="M360 210 C 360 190, 440 190, 450 200 L462 196 L456 210 C 440 220, 380 222, 360 210 Z", fill="#b5793f")
    el(root, "path", d="M458 196 C 452 178, 458 164, 466 152 C 474 166, 476 182, 468 196 Z", fill="#f0a93a")
    el(root, "path", d="M460 192 C 458 182, 462 174, 466 168 C 470 176, 470 186, 466 192 Z", fill="#fbe08a")
    el(root, "rect", x=120, y=150, width=110, height=90, fill="#3d342b", stroke="#5a4630", stroke_width=6)
    el(root, "rect", x=600, y=260, width=120, height=100, rx=6, fill="#5a4630")
    return root



# --- Fourth set: one scene for each teaching note --------------------------

def rays(root: ET.Element, cx: float, cy: float, inner: float, outer: float, count: int, color: str,
         start: float = 0.0, sweep: float = 360.0, width: float = 3, opacity: float = 0.5) -> None:
    for i in range(count):
        angle = math.radians(start + sweep * i / max(1, count - (0 if sweep >= 360 else 1)))
        el(root, "line", x1=f"{cx + inner * math.cos(angle):.1f}", y1=f"{cy + inner * math.sin(angle):.1f}",
           x2=f"{cx + outer * math.cos(angle):.1f}", y2=f"{cy + outer * math.sin(angle):.1f}",
           stroke=color, stroke_width=width, stroke_opacity=opacity, stroke_linecap="round")


def stars(root: ET.Element, points: list[tuple[float, float]], color: str = "#f4efe3", r: float = 2.2) -> None:
    for x, y in points:
        el(root, "circle", cx=x, cy=y, r=r, fill=color)


def kneeling(parent: ET.Element, x: float, y: float, robe: str, skin: str, scale: float = 1.0, facing: int = 1) -> None:
    """A figure kneeling in prayer whose knees rest at (x, y)."""
    group = ET.SubElement(parent, NS + "g", {"transform": f"translate({x:.1f} {y:.1f}) scale({scale * facing} {scale})"})
    el(group, "path", d="M-26 0 C -28 -14, -18 -20, -8 -20 L-2 -46 C 0 -54, 14 -54, 16 -46 L20 -20 C 22 -10, 16 0, 6 0 Z", fill=robe)
    el(group, "circle", cx=10, cy=-60, r=9, fill=skin)
    el(group, "path", d="M16 -40 L26 -54 L22 -40 Z", fill=skin)


def open_hands() -> ET.Element:
    root = scene("open-hands", "A living offering | 活祭",
                 "Two open hands are lifted toward a warm light, as if offering the whole self to God. | "
                 "一双张开的手向着温暖的光举起，好像把整个人献给神。", "#efe4cf")
    el(root, "circle", cx=400, cy=120, r=150, fill="#f2c56b", fill_opacity=0.18)
    el(root, "circle", cx=400, cy=120, r=80, fill="#f2c56b", fill_opacity=0.28)
    rays(root, 400, 120, 96, 190, 14, "#e2a84a", start=200, sweep=140, width=4, opacity=0.35)
    for side in (-1, 1):
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({400 + side * 70} 300) scale({side} 1)"})
        el(g, "path", d="M-10 150 L-20 40 C -24 10, -10 -10, 10 -14 L60 -24 C 76 -26, 80 -10, 66 -4 L34 6 L40 30 L20 150 Z", fill="#b07a55")
        for i, (dx, length) in enumerate([(18, 70), (34, 82), (50, 76), (64, 60)]):
            el(g, "path", d=f"M{dx - 7} -10 L{dx - 4} {-10 - length} C {dx - 2} {-18 - length}, {dx + 8} {-18 - length}, {dx + 8} {-10 - length} L{dx + 7} -6 Z", fill="#c08a63")
        el(g, "path", d="M-20 150 L-24 110 L40 110 L44 150 Z", fill="#456346")
    return root


def race_course() -> ET.Element:
    root = scene("race-course", "Running with endurance | 存心忍耐奔跑",
                 "Runners move along a track toward a finish line while a great crowd watches from the stands. | "
                 "赛跑的人沿着跑道奔向终点，看台上有许多人在观看。", "#dfe8e4")
    for row in range(3):
        y = 70 + row * 34
        el(root, "rect", x=0, y=y, width=800, height=30, fill="#c9b48a" if row % 2 else "#b9a479")
        for i in range(26):
            el(root, "circle", cx=18 + i * 30 + (row % 2) * 12, cy=y + 6, r=8, fill=SKIN[(i + row) % len(SKIN)])
            el(root, "path", d=f"M{8 + i * 30 + (row % 2) * 12} {y + 30} C {8 + i * 30 + (row % 2) * 12} {y + 14}, {28 + i * 30 + (row % 2) * 12} {y + 14}, {28 + i * 30 + (row % 2) * 12} {y + 30} Z", fill=ROBES[(i + row) % len(ROBES)])
    el(root, "rect", x=0, y=172, width=800, height=278, fill="#b4573f")
    for i in range(5):
        el(root, "line", x1=0, y1=210 + i * 50, x2=800, y2=210 + i * 50, stroke="#f4efe3", stroke_width=3, stroke_opacity=0.8)
    el(root, "rect", x=660, y=172, width=14, height=278, fill="#f4efe3")
    for i in range(14):
        el(root, "rect", x=660 + (i % 2) * 7, y=172 + i * 20, width=7, height=10, fill="#2f3a2f")
    for i, (x, y) in enumerate([(520, 250), (430, 300), (330, 350), (230, 400)]):
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y})"})
        el(g, "circle", cx=8, cy=-62, r=9, fill=SKIN[i])
        el(g, "path", d="M-6 -50 L14 -50 L10 -24 L-8 -24 Z", fill=ROBES[i + 1])
        el(g, "path", d="M-4 -26 L-22 -6 M8 -26 L18 -4 L30 -8", fill="none", stroke=SKIN[i], stroke_width=6, stroke_linecap="round", stroke_linejoin="round")
        el(g, "path", d="M-2 -46 L-20 -34 M12 -46 L26 -56", fill="none", stroke=SKIN[i], stroke_width=5, stroke_linecap="round")
    return root


def river_of_life() -> ET.Element:
    root = scene("river-of-life", "The river of life | 生命河",
                 "A bright river flows from a distant city gate between fruit trees, under a clear morning sky. | "
                 "明亮的河从远处的城门流出，两岸有结果子的树，天空清朗。", "#e4eef0")
    el(root, "circle", cx=400, cy=120, r=110, fill="#f6e7b0", fill_opacity=0.6)
    el(root, "rect", x=310, y=96, width=180, height=110, fill="#e9dcc0")
    el(root, "path", d="M370 206 L370 150 C 370 126, 430 126, 430 150 L430 206 Z", fill="#f8efcf")
    for x in range(310, 491, 30):
        el(root, "rect", x=x, y=84, width=18, height=16, fill="#e9dcc0")
    ground(root, 200, "#9cc07a", 6, 600)
    el(root, "path", d="M380 206 L420 206 C 470 280, 560 340, 640 450 L160 450 C 240 340, 330 280, 380 206 Z", fill="#7fb7c4")
    el(root, "path", d="M400 214 C 380 260, 360 320, 330 450", fill="none", stroke="#d8eef0", stroke_width=6, stroke_opacity=0.7)
    for side, xs in ((-1, (300, 220, 120)), (1, (500, 590, 690))):
        for i, x in enumerate(xs):
            y = 250 + i * 60
            size = 34 + i * 14
            el(root, "rect", x=x - 5, y=y, width=10, height=size * 1.2, fill="#7a5537")
            el(root, "circle", cx=x, cy=y - size * 0.2, r=size, fill="#4f7d45")
            for j in range(4):
                el(root, "circle", cx=x - size * 0.5 + j * size * 0.34, cy=y - size * 0.3 + (j % 2) * 14, r=5, fill="#e2a84a")
    return root


def bethlehem_star() -> ET.Element:
    root = scene("bethlehem-star", "A light for every neighbor | 照亮邻舍的光",
                 "A bright star shines over a small town at night while travelers walk toward an open, lit doorway. | "
                 "夜里一颗明亮的星照在小城上，几位行路人走向一扇敞开、透着灯光的门。", "#1f2b46")
    stars(root, [(80, 60), (160, 110), (260, 40), (520, 70), (640, 120), (720, 50), (340, 90), (60, 170)])
    el(root, "path", d="M560 80 L566 100 L586 106 L566 112 L560 132 L554 112 L534 106 L554 100 Z", fill="#f6e7b0")
    el(root, "path", d="M560 132 L480 330 L640 330 Z", fill="#f6e7b0", fill_opacity=0.10)
    ground(root, 320, "#3b3a30", 8, 600)
    for x, w, h in [(200, 90, 70), (300, 110, 90), (430, 80, 60), (540, 120, 100), (680, 90, 70)]:
        el(root, "rect", x=x - w / 2, y=330 - h, width=w, height=h, fill="#8d7a5a")
        el(root, "rect", x=x - w / 2 - 4, y=330 - h - 8, width=w + 8, height=10, fill="#6f5e44")
    el(root, "rect", x=520, y=270, width=34, height=60, rx=3, fill="#f2c56b")
    el(root, "path", d="M520 330 L554 330 L620 420 L470 420 Z", fill="#f2c56b", fill_opacity=0.18)
    for i, x in enumerate((360, 410)):
        person(root, x, 400, ROBES[i + 2], SKIN[i + 1], 0.9)
    return root


def night_shepherds() -> ET.Element:
    root = scene("night-shepherds", "Good news in the night | 夜里的好消息",
                 "Shepherds and their sheep look up from a dark hillside toward a sky filled with light. | "
                 "牧羊人和羊群在幽暗的山坡上，抬头望向充满亮光的天空。", "#202a40")
    el(root, "circle", cx=520, cy=90, r=200, fill="#f6e7b0", fill_opacity=0.10)
    el(root, "circle", cx=520, cy=90, r=110, fill="#f6e7b0", fill_opacity=0.18)
    rays(root, 520, 90, 30, 140, 16, "#f6e7b0", width=3, opacity=0.4)
    stars(root, [(60, 50), (130, 120), (220, 60), (300, 140), (760, 200), (700, 40)])
    ground(root, 300, "#33402f", 18, 700, 1.2)
    for x, y in [(430, 360), (490, 380), (560, 350), (620, 386), (680, 360)]:
        el(root, "path", d=f"M{x - 22} {y} C {x - 26} {y - 26}, {x + 22} {y - 30}, {x + 24} {y} Z", fill="#e8e1d2")
        el(root, "circle", cx=x + 26, cy=y - 16, r=8, fill="#bdb3a0")
    for i, x in enumerate((180, 250, 310)):
        person(root, x, 380 + (i % 2) * 8, ROBES[(i + 2) % len(ROBES)], SKIN[i], 1.0)
    el(root, "path", d="M268 390 L276 300 C 276 288, 292 288, 290 300", fill="none", stroke="#7a5537", stroke_width=4, stroke_linecap="round")
    return root


def open_cage() -> ET.Element:
    root = scene("open-cage", "Free to live for God | 得自由为神而活",
                 "A cage door stands open and birds fly out toward a bright, open sky. | "
                 "鸟笼的门敞开着，鸟儿飞向明亮开阔的天空。", "#e7eef0")
    el(root, "circle", cx=640, cy=110, r=70, fill="#f2c56b", fill_opacity=0.5)
    el(root, "path", d="M0 380 L800 380 L800 450 L0 450 Z", fill="#c9b48a")
    el(root, "rect", x=150, y=360, width=240, height=20, fill="#8e6644")
    el(root, "path", d="M170 360 L170 200 C 170 120, 370 120, 370 200 L370 360", fill="none", stroke="#6b4e33", stroke_width=5)
    for x in range(190, 370, 22):
        el(root, "line", x1=x, y1=360, x2=x, y2=158 if 230 < x < 320 else 190, stroke="#6b4e33", stroke_width=3)
    el(root, "line", x1=270, y1=128, x2=270, y2=100, stroke="#6b4e33", stroke_width=4)
    el(root, "circle", cx=270, cy=94, r=8, fill="none", stroke="#6b4e33", stroke_width=4)
    el(root, "path", d="M370 260 L460 230 L460 350 L370 340 Z", fill="none", stroke="#6b4e33", stroke_width=4)
    for x, y, s in [(470, 220, 1.0), (540, 170, 0.9), (610, 210, 0.8), (680, 150, 0.7)]:
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y}) scale({s})"})
        el(g, "path", d="M-20 0 C -10 -18, 0 -8, 0 0 C 0 -8, 10 -18, 20 0", fill="none", stroke="#3f6c7a", stroke_width=6, stroke_linecap="round")
    return root


def refining_fire() -> ET.Element:
    root = scene("refining-fire", "Gold in the fire | 火中的金子",
                 "A small crucible of glowing gold sits over a steady fire in a dark workshop. | "
                 "幽暗的作坊里，一个盛着发光金子的坩埚放在稳定的火上。", "#2c2722")
    el(root, "circle", cx=400, cy=250, r=200, fill="#f0a93a", fill_opacity=0.12)
    el(root, "path", d="M0 380 L800 380 L800 450 L0 450 Z", fill="#4a3c2e")
    el(root, "rect", x=270, y=300, width=260, height=80, rx=8, fill="#6b5a48")
    for i, (x, hgt) in enumerate([(320, 40), (360, 58), (400, 70), (440, 58), (480, 40)]):
        el(root, "path", d=f"M{x - 26} 312 C {x - 20} {312 - hgt * 0.6}, {x - 4} {312 - hgt * 0.8}, {x} {312 - hgt} C {x + 4} {312 - hgt * 0.8}, {x + 20} {312 - hgt * 0.6}, {x + 26} 312 Z", fill="#e8742e" if i % 2 else "#f0a93a")
    el(root, "path", d="M330 230 L470 230 L450 290 L350 290 Z", fill="#5a4e40")
    el(root, "path", d="M340 236 L460 236 L456 252 L344 252 Z", fill="#fbe08a")
    rays(root, 400, 236, 30, 90, 7, "#fbe08a", start=200, sweep=140, width=3, opacity=0.4)
    el(root, "line", x1=470, y1=240, x2=620, y2=160, stroke="#8f8576", stroke_width=6, stroke_linecap="round")
    return root


def triune_light() -> ET.Element:
    root = scene("triune-light", "Love shared from eternity | 永恒中分享的爱",
                 "Three overlapping circles of warm light form one shared center, a simple sign of the Father, Son, and Spirit. | "
                 "三个交叠的暖光圆环合成一个共同的中心，用简单图形象征父、子、圣灵。", "#f1e8d6")
    rays(root, 400, 230, 160, 230, 24, "#e2a84a", width=3, opacity=0.25)
    for (x, y), color in zip([(400, 170), (345, 265), (455, 265)], ["#c98a45", "#3f6c7a", "#8b4b45"]):
        el(root, "circle", cx=x, cy=y, r=96, fill=color, fill_opacity=0.28)
        el(root, "circle", cx=x, cy=y, r=96, fill="none", stroke=color, stroke_width=4)
    el(root, "circle", cx=400, cy=233, r=16, fill="#fbf3dc")
    return root


def basin_towel() -> ET.Element:
    root = scene("basin-towel", "The basin and the towel | 水盆与手巾",
                 "A water basin, a clay pitcher, and a folded towel sit on a stone floor, ready for washing feet. | "
                 "石地上放着一个水盆、一把陶壶和一条叠好的手巾，预备为人洗脚。", "#ece2cf")
    el(root, "path", d="M0 300 L800 300 L800 450 L0 450 Z", fill="#c9b8a0")
    for x in range(0, 800, 100):
        el(root, "line", x1=x, y1=300, x2=x - 60, y2=450, stroke="#b4a288", stroke_width=2)
    el(root, "line", x1=0, y1=370, x2=800, y2=370, stroke="#b4a288", stroke_width=2)
    el(root, "path", d="M250 330 C 250 400, 470 400, 470 330 Z", fill="#a86f3c")
    el(root, "path", d="M240 326 L480 326 L476 340 L244 340 Z", fill="#8f5c2f")
    el(root, "path", d="M260 334 L460 334 C 450 344, 270 344, 260 334 Z", fill="#7fb7c4")
    el(root, "path", d="M540 340 C 520 300, 530 240, 556 220 L560 196 L590 196 L594 220 C 620 240, 630 300, 610 340 Z", fill="#b5793f")
    el(root, "path", d="M610 240 C 650 240, 650 290, 612 300", fill="none", stroke="#9b6634", stroke_width=8)
    el(root, "path", d="M120 320 L220 312 L230 352 L130 360 Z", fill="#f4efe3", stroke="#c9b8a0", stroke_width=2)
    el(root, "path", d="M126 340 L226 332", stroke="#d8cdb8", stroke_width=3)
    return root


def garden_thorn() -> ET.Element:
    root = scene("garden-thorn", "Beauty and the thorn | 美善与荆棘",
                 "A flowering garden glows in the sun, while one thorny vine creeps in from the edge. | "
                 "阳光下的花园盛开绽放，只有一根带刺的藤蔓从边上爬进来。", "#e6efe0")
    el(root, "circle", cx=150, cy=90, r=56, fill="#f2c56b", fill_opacity=0.7)
    ground(root, 280, "#8fb46e", 10, 560)
    colors = ["#c4574a", "#e2a84a", "#7b5d84", "#f4efe3", "#d47aa0"]
    for i in range(22):
        x = 40 + (i * 37) % 560
        y = 300 + (i * 53) % 120
        el(root, "line", x1=x, y1=y + 30, x2=x, y2=y, stroke="#4f7d45", stroke_width=3)
        for k in range(5):
            angle = math.radians(k * 72)
            el(root, "circle", cx=f"{x + 7 * math.cos(angle):.1f}", cy=f"{y + 7 * math.sin(angle):.1f}", r=6, fill=colors[i % len(colors)])
        el(root, "circle", cx=x, cy=y, r=4, fill="#f6e7b0")
    vine = [(800, 330), (740, 300), (700, 340), (650, 310), (610, 350)]
    el(root, "path", d=path(vine, close=False), fill="none", stroke="#4a3c2e", stroke_width=5, stroke_linecap="round", stroke_linejoin="round")
    for (x1, y1), (x2, y2) in zip(vine, vine[1:]):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        el(root, "path", d=f"M{mx - 4} {my} L{mx} {my - 14} L{mx + 4} {my} Z", fill="#4a3c2e")
    return root


def creation_dawn() -> ET.Element:
    root = scene("creation-dawn", "Creation overflowing | 满溢的创造",
                 "The sun rises over sea and land; birds fly, fish leap, and plants spring up across the hills. | "
                 "太阳从海与陆地之上升起；飞鸟翱翔，鱼儿跃起，山坡上长满草木。", "#f3e2bd")
    el(root, "circle", cx=400, cy=230, r=90, fill="#eaa94a")
    rays(root, 400, 230, 110, 260, 18, "#eaa94a", start=180, sweep=180, width=4, opacity=0.4)
    el(root, "path", d=path([(0, 450)] + wave(0, 800, 250, 6, 200) + [(800, 450)]), fill="#5f97a8")
    el(root, "path", d="M0 300 C 120 250, 240 260, 340 320 L340 450 L0 450 Z", fill="#6f9f4c")
    el(root, "path", d="M800 290 C 700 250, 560 270, 500 340 L500 450 L800 450 Z", fill="#7fae5a")
    for x, y in [(60, 280), (120, 270), (200, 290), (620, 280), (700, 270), (760, 290)]:
        el(root, "path", d=f"M{x} {y} L{x - 14} {y + 30} L{x + 14} {y + 30} Z", fill="#3f6b3a")
    for x, y in [(180, 90), (230, 120), (600, 80), (650, 110)]:
        el(root, "path", d=f"M{x - 16} {y} C {x - 8} {y - 12}, {x} {y - 6}, {x} {y} C {x} {y - 6}, {x + 8} {y - 12}, {x + 16} {y}", fill="none", stroke="#2f3a2f", stroke_width=3, stroke_linecap="round")
    el(root, "path", d="M420 330 C 440 300, 480 300, 490 320 L500 306 L500 336 L490 324 C 470 344, 440 344, 420 330 Z", fill="#e2a84a")
    return root


def high_priest() -> ET.Element:
    root = scene("high-priest", "Our great High Priest | 我们的大祭司",
                 "A priest in a blue robe and jeweled breastpiece stands before an incense altar and a curtain that has been opened. | "
                 "身穿蓝袍、胸前佩着宝石胸牌的祭司，站在香坛和已被打开的幔子前。", "#efe2c8")
    el(root, "rect", x=420, y=60, width=300, height=300, fill="#f6e7b0", fill_opacity=0.7)
    el(root, "path", d="M420 60 L520 60 C 500 160, 480 260, 420 360 Z", fill="#7b4f6b")
    el(root, "path", d="M720 60 L620 60 C 640 160, 660 260, 720 360 Z", fill="#7b4f6b")
    ground(root, 360, "#d6bf8f", 4, 700)
    el(root, "rect", x=540, y=290, width=60, height=80, fill="#c69a3e")
    el(root, "rect", x=530, y=282, width=80, height=12, fill="#a8743f")
    el(root, "path", d="M570 280 C 550 240, 590 210, 566 170", fill="none", stroke="#9a948a", stroke_width=6, stroke_opacity=0.5, stroke_linecap="round")
    g = ET.SubElement(root, NS + "g", {"transform": "translate(300 390) scale(2.2)"})
    el(g, "path", d="M-16 0 L-11 -46 C -10 -52, 10 -52, 11 -46 L16 0 Z", fill="#3f5f8a")
    el(g, "path", d="M-8 -44 L8 -44 L8 -30 L-8 -30 Z", fill="#e9d6a6")
    for i in range(4):
        for j in range(3):
            el(g, "circle", cx=-5 + j * 5, cy=-41 + i * 3.4, r=1.3, fill=["#8b4b45", "#456346", "#3f6c7a", "#c69a3e"][i])
    el(g, "circle", cx=0, cy=-58, r=8, fill="#b07a55")
    el(g, "path", d="M-8 -62 C -8 -72, 8 -72, 8 -62 Z", fill="#f4efe3")
    for x in range(-14, 16, 6):
        el(g, "circle", cx=x, cy=-1, r=1.5, fill="#c69a3e")
    return root


def shared_yoke() -> ET.Element:
    root = scene("shared-yoke", "Sharing the yoke | 同负一轭",
                 "Two oxen walk side by side under one wooden yoke, plowing a quiet field in the evening light. | "
                 "两头牛同负一个木轭并肩前行，在傍晚的光里耕着安静的田。", "#f1e2c4")
    el(root, "circle", cx=640, cy=150, r=60, fill="#eaa94a", fill_opacity=0.8)
    ground(root, 230, "#b9a479", 6, 700)
    for i in range(7):
        el(root, "path", d=f"M0 {270 + i * 26} C 300 {262 + i * 26}, 500 {276 + i * 26}, 800 {266 + i * 26}", fill="none", stroke="#9c8660", stroke_width=3)
    for x, y, color in ((350, 330, "#a8743f"), (300, 380, "#7a5537")):
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y}) scale(1.5)"})
        el(g, "path", d="M-90 -20 C -90 -60, 30 -66, 40 -40 L40 0 L-90 0 Z", fill=color)
        el(g, "path", d="M40 -46 C 60 -56, 80 -40, 76 -20 L60 -14 L40 -20 Z", fill=color)
        el(g, "path", d="M54 -52 L46 -66 M66 -52 L74 -66", fill="none", stroke="#e9dcc0", stroke_width=4, stroke_linecap="round")
        for leg in (-80, -60, 10, 28):
            el(g, "rect", x=leg, y=-2, width=8, height=30, fill=color)
    el(root, "line", x1=344, y1=322, x2=416, y2=262, stroke="#5a3e28", stroke_width=12, stroke_linecap="round")
    for x, y in ((362, 320), (410, 280)):
        el(root, "path", d=f"M{x - 12} {y - 6} C {x - 14} {y + 20}, {x + 14} {y + 20}, {x + 12} {y - 6}", fill="none", stroke="#5a3e28", stroke_width=4)
    el(root, "line", x1=170, y1=360, x2=90, y2=400, stroke="#5a3e28", stroke_width=6, stroke_linecap="round")
    el(root, "path", d="M80 392 L64 424 L92 414 Z", fill="#6f6a60")
    return root


def mount_teaching() -> ET.Element:
    root = scene("mount-teaching", "Teaching on the mountain | 山上的教导",
                 "On a grassy hillside above a lake, a crowd sits listening to one teacher. | "
                 "湖边青草的山坡上，一群人坐着聆听一位教师讲话。", "#e4eef0")
    el(root, "path", d=path([(0, 210)] + wave(0, 800, 200, 4, 300) + [(800, 260), (0, 260)]), fill="#7fb7c4")
    el(root, "path", d="M0 230 C 200 140, 420 110, 800 200 L800 450 L0 450 Z", fill="#8fb46e")
    person(root, 560, 210, "#f4efe3", "#b07a55", 0.95)
    for i in range(18):
        x = 120 + (i % 9) * 52 + (i // 9) * 20
        y = 300 + (i // 9) * 60 + (i % 3) * 6
        el(root, "circle", cx=x, cy=y - 30, r=8, fill=SKIN[i % len(SKIN)])
        el(root, "path", d=f"M{x - 14} {y} C {x - 14} {y - 24}, {x + 14} {y - 24}, {x + 14} {y} Z", fill=ROBES[i % len(ROBES)])
    for x, y in [(80, 420), (690, 380), (740, 430)]:
        el(root, "path", d=f"M{x} {y} l-6 -16 m6 16 l0 -18 m0 18 l6 -16", fill="none", stroke="#4f7d45", stroke_width=3, stroke_linecap="round")
    return root


def mountain_glory() -> ET.Element:
    root = scene("mountain-glory", "Glory on the mountain | 山上的荣光",
                 "Brilliant light breaks over a high mountain peak and spills down its slopes. | "
                 "灿烂的光从高山顶上发出，倾洒在山坡上。", "#2a3352")
    el(root, "circle", cx=400, cy=120, r=230, fill="#f6e7b0", fill_opacity=0.10)
    el(root, "circle", cx=400, cy=120, r=140, fill="#f6e7b0", fill_opacity=0.16)
    el(root, "circle", cx=400, cy=96, r=48, fill="#fbf3dc", fill_opacity=0.9)
    rays(root, 400, 120, 70, 360, 28, "#f6e7b0", width=4, opacity=0.25)
    el(root, "path", d="M120 450 L400 160 L680 450 Z", fill="#5a5d6e")
    el(root, "path", d="M400 160 L470 232 L430 226 L410 250 L380 226 L340 222 Z", fill="#f4efe3")
    el(root, "path", d="M0 450 L160 300 L300 450 Z M500 450 L660 280 L800 400 L800 450 Z", fill="#3e4152")
    return root


def lowly_valley() -> ET.Element:
    root = scene("lowly-valley", "Blessed are the poor in spirit | 虚心的人有福了",
                 "A person kneels with empty hands in a quiet valley, while morning light falls on a wide green land ahead. | "
                 "一个人空着手跪在安静的山谷里，晨光照在前面广阔的绿地上。", "#e8ecdf")
    el(root, "circle", cx=600, cy=110, r=90, fill="#f2c56b", fill_opacity=0.35)
    el(root, "path", d="M0 120 C 120 140, 220 250, 320 300 L0 300 Z M800 140 C 700 160, 560 250, 470 300 L800 300 Z", fill="#9aa88a")
    ground(root, 290, "#8fb46e", 6, 600)
    el(root, "path", d="M330 450 C 360 380, 420 330, 480 300 L520 300 C 480 340, 470 400, 470 450 Z", fill="#c9b48a", fill_opacity=0.7)
    kneeling(root, 360, 400, "#7b5d84", "#8a5f43", 1.4)
    rays(root, 600, 110, 100, 200, 9, "#f2c56b", start=110, sweep=80, width=4, opacity=0.35)
    return root


def well_cup() -> ET.Element:
    root = scene("well-cup", "Hunger and thirst | 饥渴慕义",
                 "A stone well stands in dry land; a bucket of fresh water and a cup rest on its edge. | "
                 "干旱的地上有一口石井，井边放着一桶清水和一个杯子。", "#f1e2c4")
    el(root, "circle", cx=650, cy=100, r=56, fill="#eaa94a", fill_opacity=0.8)
    ground(root, 300, "#d6bf8f", 6, 700)
    for x, y in [(80, 360), (150, 410), (700, 380), (640, 420)]:
        el(root, "path", d=f"M{x} {y} l-6 -14 m6 14 l0 -16 m0 16 l6 -14", fill="none", stroke="#a39466", stroke_width=3, stroke_linecap="round")
    el(root, "rect", x=290, y=250, width=220, height=120, fill="#a79c8a")
    for row in range(4):
        for col in range(5):
            el(root, "rect", x=290 + col * 44 + (row % 2) * 22, y=250 + row * 30, width=40, height=26, rx=3, fill="#bcb2a0" if (row + col) % 2 else "#b2a794")
    el(root, "rect", x=280, y=240, width=240, height=16, rx=4, fill="#8d8474")
    el(root, "line", x1=300, y1=240, x2=300, y2=130, stroke="#7a5537", stroke_width=10)
    el(root, "line", x1=500, y1=240, x2=500, y2=130, stroke="#7a5537", stroke_width=10)
    el(root, "line", x1=290, y1=136, x2=510, y2=136, stroke="#7a5537", stroke_width=10)
    el(root, "line", x1=420, y1=136, x2=420, y2=200, stroke="#5a4e40", stroke_width=2)
    el(root, "path", d="M400 200 L440 200 L434 236 L406 236 Z", fill="#8f5c2f")
    el(root, "rect", x=404, y=202, width=32, height=6, fill="#7fb7c4")
    el(root, "path", d="M470 222 L494 222 L490 240 L474 240 Z", fill="#c98a45")
    return root


def hill_city() -> ET.Element:
    root = scene("hill-city", "A city on a hill | 山上的城",
                 "At dusk a small city glows on top of a hill, its windows bright, while a lamp burns in the foreground. | "
                 "黄昏时，一座小城在山顶发光，窗户明亮；近处一盏灯正点着。", "#33405e")
    stars(root, [(60, 40), (140, 90), (700, 60), (760, 130), (600, 30)])
    el(root, "path", d="M0 450 L0 330 C 160 300, 260 180, 400 170 C 540 180, 640 300, 800 330 L800 450 Z", fill="#3d4a3a")
    for i, (x, w, h) in enumerate([(320, 50, 50), (370, 44, 70), (420, 60, 60), (480, 40, 44), (345, 30, 90)]):
        el(root, "rect", x=x - w / 2, y=175 - h, width=w, height=h + 10, fill="#d8c49a")
        for j in range(2):
            el(root, "rect", x=x - 6 + (j - 0.5) * 14, y=175 - h + 14, width=8, height=10, fill="#fbe08a")
    el(root, "circle", cx=400, cy=140, r=120, fill="#fbe08a", fill_opacity=0.10)
    el(root, "rect", x=140, y=360, width=12, height=70, fill="#8f5c2f")
    el(root, "path", d="M110 430 L180 430 L166 414 L124 414 Z", fill="#8f5c2f")
    el(root, "path", d="M120 360 C 120 346, 172 346, 180 354 L188 350 L184 362 C 172 370, 132 372, 120 360 Z", fill="#b5793f")
    el(root, "path", d="M184 350 C 180 336, 184 326, 190 318 C 196 328, 196 340, 190 350 Z", fill="#f0a93a")
    el(root, "circle", cx=188, cy=338, r=50, fill="#f2c56b", fill_opacity=0.18)
    el(root, "path", d="M600 430 C 600 404, 660 404, 660 430 Z", fill="#e8e1d2")
    return root


def bridge_reconcile() -> ET.Element:
    root = scene("bridge-reconcile", "Meeting on the bridge | 在桥上相迎",
                 "Two people walk toward each other from opposite banks and meet in the middle of a small bridge. | "
                 "两个人从两岸相向而行，在一座小桥中间相遇。", "#e6eee8")
    el(root, "circle", cx=400, cy=100, r=60, fill="#f2c56b", fill_opacity=0.5)
    el(root, "path", d="M0 260 C 120 250, 200 270, 260 300 L260 450 L0 450 Z", fill="#8fb46e")
    el(root, "path", d="M800 260 C 680 250, 600 270, 540 300 L540 450 L800 450 Z", fill="#8fb46e")
    el(root, "path", d="M240 330 L560 330 L560 450 L240 450 Z", fill="#7fb7c4")
    el(root, "path", d="M200 300 C 300 240, 500 240, 600 300 L600 316 C 500 258, 300 258, 200 316 Z", fill="#8e6644")
    for x in range(240, 580, 40):
        top = 300 - 60 * (1 - ((x - 400) / 200) ** 2)
        el(root, "line", x1=x, y1=f"{top:.1f}", x2=x, y2=f"{top - 30:.1f}", stroke="#6b4e33", stroke_width=4)
    el(root, "path", d="M220 268 C 300 214, 500 214, 580 268", fill="none", stroke="#6b4e33", stroke_width=4)
    person(root, 370, 254, "#3f6c7a", "#8a5f43", 1.0)
    person(root, 430, 254, "#8b4b45", "#c08a63", 1.0)
    el(root, "path", d="M380 220 C 392 212, 408 212, 420 220", fill="none", stroke="#b07a55", stroke_width=5, stroke_linecap="round")
    return root


def secret_room() -> ET.Element:
    root = scene("secret-room", "Prayer in the quiet room | 在内屋祷告",
                 "In a small room with the door shut, a person kneels in prayer while light falls through a high window. | "
                 "在关上门的小屋里，一个人跪着祷告，光从高窗照进来。", "#4a3f36")
    el(root, "path", d="M0 340 L800 340 L800 450 L0 450 Z", fill="#6b5a48")
    el(root, "rect", x=520, y=80, width=90, height=70, fill="#f6e7b0")
    el(root, "line", x1=565, y1=80, x2=565, y2=150, stroke="#4a3f36", stroke_width=5)
    el(root, "path", d="M520 150 L610 150 L520 420 L300 420 Z", fill="#f6e7b0", fill_opacity=0.16)
    el(root, "rect", x=100, y=150, width=110, height=190, fill="#5a4630", stroke="#3a2e22", stroke_width=6)
    el(root, "circle", cx=190, cy=250, r=6, fill="#c69a3e")
    kneeling(root, 420, 400, "#3f6c7a", "#b07a55", 1.5)
    el(root, "path", d="M370 400 L520 400 L520 410 L370 410 Z", fill="#8b4b45", fill_opacity=0.8)
    return root


def morning_prayer() -> ET.Element:
    root = scene("morning-prayer", "Growing in prayer | 在祷告中成长",
                 "A person kneels beside a young tree on a hilltop at sunrise; the tree's roots reach deep into the soil. | "
                 "日出时，一个人跪在山顶一棵小树旁；小树的根深深扎进土里。", "#f3e2bd")
    el(root, "circle", cx=640, cy=210, r=80, fill="#eaa94a")
    el(root, "path", d=path([(0, 250)] + wave(0, 800, 240, 8, 400) + [(800, 300), (0, 300)]), fill="#c9a874")
    el(root, "path", d="M0 300 C 200 250, 500 260, 800 300 L800 450 L0 450 Z", fill="#7a6a4e")
    el(root, "path", d="M0 300 C 200 250, 500 260, 800 300 L800 316 C 500 276, 200 266, 0 316 Z", fill="#6f9f4c")
    el(root, "line", x1=360, y1=280, x2=360, y2=170, stroke="#7a5537", stroke_width=10)
    el(root, "circle", cx=360, cy=160, r=50, fill="#4f7d45")
    el(root, "circle", cx=330, cy=180, r=30, fill="#5f8f50")
    el(root, "circle", cx=392, cy=178, r=32, fill="#5f8f50")
    for dx, depth in [(-60, 120), (-24, 150), (20, 140), (64, 110)]:
        el(root, "path", d=f"M360 290 C {360 + dx * 0.4} {290 + depth * 0.4}, {360 + dx} {290 + depth * 0.6}, {360 + dx * 1.2} {290 + depth}", fill="none", stroke="#b89a62", stroke_width=4, stroke_linecap="round")
    kneeling(root, 470, 282, "#8b4b45", "#c08a63", 1.1, facing=-1)
    return root


def hidden_treasure() -> ET.Element:
    root = scene("hidden-treasure", "Treasure in heaven | 积攒财宝在天上",
                 "An open chest glows in a field, while a moth-eaten cloth and rusted coins lie forgotten nearby. | "
                 "田间一个打开的宝箱发着光；旁边被虫蛀的布和生锈的钱币被丢在一边。", "#e9efe0")
    ground(root, 280, "#8fb46e", 8, 600)
    el(root, "circle", cx=420, cy=300, r=130, fill="#fbe08a", fill_opacity=0.18)
    el(root, "rect", x=350, y=290, width=140, height=80, rx=6, fill="#8e6644")
    el(root, "rect", x=350, y=318, width=140, height=10, fill="#c69a3e")
    el(root, "path", d="M350 290 L380 230 L520 230 L490 290 Z", fill="#7a5537")
    el(root, "path", d="M360 290 L480 290 L470 270 L370 270 Z", fill="#fbe08a")
    rays(root, 420, 270, 30, 120, 9, "#fbe08a", start=200, sweep=140, width=4, opacity=0.5)
    el(root, "path", d="M120 380 L220 370 L230 410 L130 420 Z", fill="#b8ad98")
    for x, y in [(150, 390), (190, 384), (176, 404), (206, 400)]:
        el(root, "circle", cx=x, cy=y, r=5, fill="#8fb46e")
    for x, y in [(600, 400), (624, 394), (646, 404)]:
        el(root, "circle", cx=x, cy=y, r=10, fill="#9a6a4a")
        el(root, "circle", cx=x + 3, cy=y - 2, r=3, fill="#6b4e33")
    return root


def lilies_birds() -> ET.Element:
    root = scene("lilies-birds", "Birds of the air, lilies of the field | 天上的飞鸟，野地的百合",
                 "Birds glide across a calm sky above a meadow full of wild lilies. | "
                 "飞鸟在平静的天空中滑翔，下面的草地上开满野百合。", "#e4eef0")
    el(root, "circle", cx=150, cy=100, r=50, fill="#f2c56b", fill_opacity=0.6)
    for x, y, s in [(420, 90, 1.2), (500, 130, 1.0), (580, 80, 0.9), (650, 140, 0.8), (340, 140, 0.8)]:
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y}) scale({s})"})
        el(g, "path", d="M-24 0 C -12 -18, 0 -8, 0 0 C 0 -8, 12 -18, 24 0", fill="none", stroke="#2f3a2f", stroke_width=4, stroke_linecap="round")
    ground(root, 270, "#8fb46e", 8, 500)
    for i in range(20):
        x = 30 + (i * 41) % 760
        y = 320 + (i * 37) % 110
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y}) scale(1.7) translate({-x} {-y})"})
        el(g, "line", x1=x, y1=y + 36, x2=x, y2=y, stroke="#4f7d45", stroke_width=3)
        el(g, "path", d=f"M{x} {y} C {x - 16} {y - 6}, {x - 18} {y - 20}, {x - 10} {y - 26} C {x - 6} {y - 16}, {x - 2} {y - 14}, {x} {y - 28} C {x + 2} {y - 14}, {x + 6} {y - 16}, {x + 10} {y - 26} C {x + 18} {y - 20}, {x + 16} {y - 6}, {x} {y} Z", fill="#f4efe3" if i % 3 else "#e8c9d8")
    return root


NOTE_ARTWORKS: dict[str, Callable[[], ET.Element]] = {
    "open-hands.svg": open_hands,
    "race-course.svg": race_course,
    "river-of-life.svg": river_of_life,
    "bethlehem-star.svg": bethlehem_star,
    "night-shepherds.svg": night_shepherds,
    "open-cage.svg": open_cage,
    "refining-fire.svg": refining_fire,
    "triune-light.svg": triune_light,
    "basin-towel.svg": basin_towel,
    "garden-thorn.svg": garden_thorn,
    "creation-dawn.svg": creation_dawn,
    "high-priest.svg": high_priest,
    "shared-yoke.svg": shared_yoke,
    "mount-teaching.svg": mount_teaching,
    "mountain-glory.svg": mountain_glory,
    "lowly-valley.svg": lowly_valley,
    "well-cup.svg": well_cup,
    "hill-city.svg": hill_city,
    "bridge-reconcile.svg": bridge_reconcile,
    "secret-room.svg": secret_room,
    "morning-prayer.svg": morning_prayer,
    "hidden-treasure.svg": hidden_treasure,
    "lilies-birds.svg": lilies_birds,
}



# --- Fifth set: guide pages ------------------------------------------------

def john_signs() -> ET.Element:
    root = scene("john-signs", "Signs and sayings in John | 约翰福音的记号与宣告",
                 "A still life on a table: six stone water jars, a loaf of bread, a lit lamp, a grapevine, and a small gate. | "
                 "桌上的静物：六口石缸、一块饼、一盏点亮的灯、一枝葡萄藤和一扇小门。", "#efe5d2")
    el(root, "rect", x=0, y=330, width=800, height=120, fill="#8e6644")
    el(root, "rect", x=0, y=322, width=800, height=12, fill="#a87a50")
    for i in range(6):
        x = 70 + i * 52
        hgt = 110 - (i % 2) * 14
        el(root, "path", d=f"M{x - 20} 322 L{x - 24} {322 - hgt + 20} C {x - 24} {322 - hgt}, {x + 24} {322 - hgt}, {x + 24} {322 - hgt + 20} L{x + 20} 322 Z", fill="#b8ad98")
        el(root, "rect", x=x - 16, y=322 - hgt - 6, width=32, height=10, rx=3, fill="#9c917c")
    el(root, "path", d="M420 322 C 410 286, 520 276, 520 322 Z", fill="#c98a45")
    el(root, "path", d="M440 300 L452 288 M466 296 L478 284 M492 298 L504 286", fill="none", stroke="#a86f3c", stroke_width=3, stroke_linecap="round")
    el(root, "circle", cx=580, cy=240, r=70, fill="#f2c56b", fill_opacity=0.2)
    el(root, "path", d="M548 300 C 548 286, 610 284, 618 292 L628 288 L624 300 C 610 310, 556 312, 548 300 Z", fill="#b5793f")
    el(root, "rect", x=578, y=300, width=12, height=22, fill="#8f5c2f")
    el(root, "path", d="M624 288 C 618 272, 624 260, 630 250 C 636 262, 638 276, 630 288 Z", fill="#f0a93a")
    el(root, "path", d="M660 120 C 700 160, 650 200, 700 240 C 730 260, 700 300, 720 322", fill="none", stroke="#6b4e33", stroke_width=5)
    for x, y in [(690, 150), (676, 200), (710, 236), (712, 290)]:
        el(root, "path", d=f"M{x} {y} C {x + 20} {y - 18}, {x + 40} {y - 4}, {x + 30} {y + 14} C {x + 20} {y + 6}, {x + 6} {y + 8}, {x} {y} Z", fill="#5f8f50")
    for x, y in [(700, 176), (712, 182), (706, 192), (718, 196), (712, 206)]:
        el(root, "circle", cx=x, cy=y, r=6, fill="#7b4f6b")
    el(root, "rect", x=372, y=214, width=4, height=108, fill="#6b4e33")
    el(root, "rect", x=372, y=232, width=36, height=80, fill="none", stroke="#7a5537", stroke_width=5)
    for x in range(381, 408, 9):
        el(root, "line", x1=x, y1=232, x2=x, y2=312, stroke="#7a5537", stroke_width=3)
    return root


def weighing_evidence() -> ET.Element:
    root = scene("weighing-evidence", "Weighing the evidence | 衡量证据",
                 "A balance scale holds scrolls on one pan and a stack of notes on the other, with a magnifying glass resting nearby. | "
                 "天平一边放着书卷，另一边放着一叠笔记，旁边放着一把放大镜。", "#e9e4d8")
    el(root, "rect", x=0, y=350, width=800, height=100, fill="#8e6644")
    el(root, "rect", x=0, y=342, width=800, height=12, fill="#a87a50")
    el(root, "path", d="M360 342 L440 342 L420 322 L380 322 Z", fill="#6b4e33")
    el(root, "rect", x=394, y=110, width=12, height=214, fill="#7a5537")
    el(root, "circle", cx=400, cy=104, r=12, fill="#c69a3e")
    el(root, "line", x1=220, y1=128, x2=580, y2=116, stroke="#7a5537", stroke_width=8, stroke_linecap="round")
    for x, y in ((230, 128), (570, 116)):
        el(root, "line", x1=x, y1=y, x2=x - 50, y2=y + 120, stroke="#5a4e40", stroke_width=2)
        el(root, "line", x1=x, y1=y, x2=x + 50, y2=y + 120, stroke="#5a4e40", stroke_width=2)
        el(root, "path", d=f"M{x - 70} {y + 120} L{x + 70} {y + 120} C {x + 60} {y + 146}, {x - 60} {y + 146}, {x - 70} {y + 120} Z", fill="#c69a3e")
    for i in range(3):
        y = 236 - i * 16
        el(root, "rect", x=184, y=y, width=92, height=14, rx=7, fill="#e9d6a6", stroke="#b89a62", stroke_width=1.5)
    for i in range(4):
        el(root, "rect", x=530 + (i % 2) * 4, y=222 - i * 8, width=80, height=8, fill="#f4efe3", stroke="#c9b8a0", stroke_width=1)
    el(root, "circle", cx=640, cy=310, r=30, fill="#c9dde3", fill_opacity=0.6, stroke="#3a3530", stroke_width=6)
    el(root, "line", x1=662, y1=330, x2=700, y2=342, stroke="#3a3530", stroke_width=9, stroke_linecap="round")
    return root


def wanderer_home() -> ET.Element:
    root = scene("wanderer-home", "The long road home | 回家的长路",
                 "At dusk a lone traveler walks a winding road across the hills toward a distant house with a lit window. | "
                 "黄昏时，一位独行的旅人沿着蜿蜒的山路，走向远处一扇亮着灯的房子。", "#4a4f6e")
    stars(root, [(80, 50), (180, 90), (300, 40), (460, 70), (620, 40), (720, 90), (560, 120)])
    el(root, "path", d="M0 260 C 160 220, 320 250, 480 230 C 600 216, 700 230, 800 220 L800 450 L0 450 Z", fill="#5d5a5e")
    el(root, "path", d="M0 320 C 200 290, 420 330, 800 300 L800 450 L0 450 Z", fill="#47483f")
    el(root, "path", d="M120 450 C 200 400, 160 360, 300 330 C 420 304, 460 280, 600 250 L612 252 C 480 290, 440 316, 320 344 C 200 372, 240 410, 180 450 Z", fill="#8d8474")
    el(root, "rect", x=616, y=216, width=44, height=34, fill="#8d7a5a")
    el(root, "path", d="M610 218 L638 196 L666 218 Z", fill="#6f5e44")
    el(root, "rect", x=630, y=226, width=12, height=12, fill="#fbe08a")
    el(root, "circle", cx=636, cy=232, r=26, fill="#fbe08a", fill_opacity=0.18)
    person(root, 236, 400, "#7b5d84", "#8a5f43", 1.0)
    el(root, "line", x1=252, y1=400, x2=258, y2=340, stroke="#7a5537", stroke_width=4, stroke_linecap="round")
    return root


def branching_tree() -> ET.Element:
    root = scene("branching-tree", "One trunk, many branches | 同一树干，许多枝子",
                 "A broad tree rises from a single trunk and spreads into several large limbs, each with leaves of a slightly different green. | "
                 "一棵大树从同一根树干长出，分成几根大枝，每根枝上的叶子绿得略有不同。", "#e8eee2")
    ground(root, 360, "#8fb46e", 6, 600)
    el(root, "path", d="M380 380 L372 250 C 370 230, 430 230, 428 250 L420 380 Z", fill="#7a5537")
    limbs = [(250, 140, "#4f7d45"), (330, 90, "#5f8f50"), (470, 90, "#3f6b3a"), (550, 140, "#6f9f4c"), (400, 70, "#557f4a")]
    for x, y, color in limbs:
        el(root, "path", d=f"M400 260 C {400 + (x - 400) * 0.4} 220, {x} {y + 70}, {x} {y + 30}", fill="none", stroke="#7a5537", stroke_width=12, stroke_linecap="round")
    for x, y, color in limbs:
        el(root, "circle", cx=x, cy=y, r=62, fill=color)
        el(root, "circle", cx=x - 30, cy=y + 22, r=34, fill=color)
        el(root, "circle", cx=x + 32, cy=y + 20, r=36, fill=color)
    for dx in (-40, -14, 14, 40):
        el(root, "path", d=f"M400 378 C {400 + dx} 400, {400 + dx * 2} 410, {400 + dx * 3} 430", fill="none", stroke="#7a5537", stroke_width=5, stroke_linecap="round")
    return root


def translation_books() -> ET.Element:
    root = scene("translation-books", "One message, many languages | 同一信息，多种语言",
                 "Several open books sit side by side, their lines of text drawn in different patterns to suggest different scripts. | "
                 "几本打开的书并排摆放，书页上的文字线条形态各异，表示不同的文字。", "#eae3d3")
    el(root, "rect", x=0, y=340, width=800, height=110, fill="#8e6644")
    for i, (x, color) in enumerate([(110, "#7c5a3a"), (300, "#456346"), (490, "#3f6c7a"), (680, "#8b4b45")]):
        el(root, "path", d=f"M{x - 86} 330 L{x} 342 L{x + 86} 330 L{x + 86} 200 L{x} 212 L{x - 86} 200 Z", fill=color)
        el(root, "path", d=f"M{x - 80} 322 L{x - 2} 334 L{x - 2} 214 L{x - 80} 202 Z", fill="#fbf8f0")
        el(root, "path", d=f"M{x + 80} 322 L{x + 2} 334 L{x + 2} 214 L{x + 80} 202 Z", fill="#f4efe3")
        for side in (-1, 1):
            for row in range(6):
                y = 222 + row * 16
                x0, x1 = x + side * 10, x + side * 70
                if i == 0:
                    el(root, "line", x1=x0, y1=y, x2=x1, y2=y - side * 0, stroke="#8a8172", stroke_width=3)
                elif i == 1:
                    for k in range(5):
                        cx = x0 + side * (6 + k * 12)
                        el(root, "rect", x=cx - 4, y=y - 4, width=8, height=8, fill="none", stroke="#8a8172", stroke_width=1.5)
                elif i == 2:
                    el(root, "path", d=f"M{x0} {y} " + " ".join(f"Q {x0 + side * (k * 12 + 6)} {y - 6}, {x0 + side * (k * 12 + 12)} {y}" for k in range(5)), fill="none", stroke="#8a8172", stroke_width=2)
                else:
                    for k in range(4):
                        el(root, "line", x1=x0 + side * k * 16, y1=y, x2=x0 + side * (k * 16 + 10), y2=y, stroke="#8a8172", stroke_width=3)
    return root


def word_cards() -> ET.Element:
    root = scene("word-cards", "Words to learn | 要学的词",
                 "Index cards are spread on a desk beside a pencil and an open notebook, ready for learning new words. | "
                 "书桌上摊着几张卡片，旁边有一支铅笔和一本打开的笔记本，预备学习新词。", "#e6dcc8")
    el(root, "rect", x=0, y=0, width=800, height=450, rx=18, fill="#a87a50")
    for i in range(6):
        el(root, "line", x1=0, y1=40 + i * 75, x2=800, y2=60 + i * 75, stroke="#9b6e46", stroke_width=3)
    cards = [(170, 150, -8, "#fbf8f0"), (330, 120, 5, "#f6e7b0"), (230, 290, 4, "#e4eef0"), (420, 260, -6, "#fbf8f0"), (560, 140, 9, "#e8eee2")]
    for x, y, angle, color in cards:
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y}) rotate({angle})"})
        el(g, "rect", x=-80, y=-50, width=160, height=100, rx=6, fill=color, stroke="#c9b8a0", stroke_width=1.5)
        el(g, "line", x1=-64, y1=-24, x2=40, y2=-24, stroke="#456346", stroke_width=6, stroke_linecap="round")
        for row in range(3):
            el(g, "line", x1=-64, y1=0 + row * 16, x2=60 - row * 18, y2=0 + row * 16, stroke="#a39466", stroke_width=3, stroke_linecap="round")
    el(root, "path", d="M600 280 L760 300 L740 420 L580 400 Z", fill="#fbf8f0")
    el(root, "line", x1=670, y1=290, x2=650, y2=410, stroke="#c9b8a0", stroke_width=3)
    el(root, "line", x1=500, y1=420, x2=640, y2=330, stroke="#e2a84a", stroke_width=10, stroke_linecap="round")
    el(root, "path", d="M640 330 L654 320 L648 336 Z", fill="#3a3530")
    return root


GUIDE_ARTWORKS: dict[str, Callable[[], ET.Element]] = {
    "john-signs.svg": john_signs,
    "weighing-evidence.svg": weighing_evidence,
    "wanderer-home.svg": wanderer_home,
    "branching-tree.svg": branching_tree,
    "translation-books.svg": translation_books,
    "word-cards.svg": word_cards,
}



# --- Sixth set: storyline stages ------------------------------------------

def ark_rainbow() -> ET.Element:
    root = scene("ark-rainbow", "After the flood | 洪水之后",
                 "A large wooden ark rests on a mountainside as the water recedes, with a rainbow arching across the clearing sky and a dove in flight. | "
                 "洪水退去，一只巨大的木方舟停在山坡上；天空放晴，彩虹横跨天际，一只鸽子在飞翔。", "#dfe8ec")
    for i, color in enumerate(["#c4574a", "#e2a84a", "#e9d36a", "#6f9f4c", "#3f6c7a", "#7b5d84"]):
        r = 330 - i * 14
        el(root, "path", d=f"M{400 - r} 330 A {r} {r} 0 0 1 {400 + r} 330", fill="none", stroke=color, stroke_width=14, stroke_opacity=0.55)
    el(root, "path", d="M0 300 C 120 200, 260 190, 380 260 C 460 300, 560 250, 800 280 L800 450 L0 450 Z", fill="#7d8a6a")
    el(root, "path", d=path([(0, 450)] + wave(0, 800, 360, 8, 220) + [(800, 450)]), fill="#5f97a8")
    el(root, "path", d="M150 258 L470 258 L440 310 L180 310 Z", fill="#7a5537")
    for y in (270, 284, 298):
        el(root, "line", x1=168, y1=y, x2=452, y2=y, stroke="#5a3e28", stroke_width=2)
    el(root, "rect", x=220, y=206, width=180, height=54, fill="#8e6644")
    el(root, "path", d="M206 210 L310 176 L414 210 Z", fill="#6b4e33")
    for x in (250, 300, 350):
        el(root, "rect", x=x - 8, y=222, width=16, height=14, fill="#3a2e22")
    el(root, "path", d="M600 120 C 610 108, 622 112, 626 120 C 636 108, 648 106, 656 112 C 646 118, 640 126, 628 128 L636 140 L622 132 C 614 134, 604 130, 600 120 Z", fill="#fbf8f0")
    el(root, "path", d="M656 112 L672 108 L664 118 Z", fill="#6f9f4c")
    return root


def abraham_stars() -> ET.Element:
    root = scene("abraham-stars", "Count the stars | 数一数天上的星",
                 "An old man stands outside his tent on a hill at night, looking up at a sky crowded with stars. | "
                 "夜里，一位老人站在山坡的帐棚外，仰望满天繁星。", "#1c2540")
    for i in range(90):
        x = (i * 97) % 790 + 5
        y = (i * 53) % 260 + 10
        el(root, "circle", cx=x, cy=y, r=1.2 + (i % 4) * 0.5, fill="#f4efe3", fill_opacity=0.55 + (i % 3) * 0.15)
    ground(root, 330, "#2e3328", 16, 640, 0.6)
    el(root, "path", d="M480 360 L560 280 L640 360 Z", fill="#8d7a5a")
    el(root, "path", d="M540 360 L560 300 L580 360 Z", fill="#3a2e22")
    el(root, "path", d="M560 280 L700 300 L640 360 Z", fill="#6f5e44")
    g = ET.SubElement(root, NS + "g", {"transform": "translate(330 372) scale(1.4)"})
    el(g, "path", d="M-13 0 L-9 -44 C -8 -50, 8 -50, 9 -44 L13 0 Z", fill="#7b5d84")
    el(g, "circle", cx=2, cy=-57, r=9, fill="#8a5f43")
    el(g, "path", d="M-5 -52 C -4 -44, 8 -44, 9 -52 C 6 -40, -2 -40, -5 -52 Z", fill="#e8e1d2")
    el(g, "line", x1=14, y1=0, x2=20, y2=-62, stroke="#7a5537", stroke_width=3, stroke_linecap="round")
    return root


TIMELINE_ARTWORKS: dict[str, Callable[[], ET.Element]] = {
    "ark-rainbow.svg": ark_rainbow,
    "abraham-stars.svg": abraham_stars,
}



# --- Seventh set: research pages ------------------------------------------

def papyrus_codex() -> ET.Element:
    root = scene("papyrus-codex", "An early papyrus book | 早期的蒲草纸抄本",
                 "An open papyrus codex with ragged edges lies on a dark table; its pages hold columns of faded handwriting drawn as simple lines. | "
                 "一本边缘残破的蒲草纸册子摊开在深色桌面上，书页上褪色的手写字迹以简单线条表示。", "#3a322a")
    el(root, "circle", cx=400, cy=220, r=260, fill="#f2c56b", fill_opacity=0.08)
    el(root, "path", d="M0 360 L800 360 L800 450 L0 450 Z", fill="#2a241e")
    for side in (-1, 1):
        x0 = 400
        x1 = 400 + side * 300
        edge = [(x1 + side * (6 if i % 2 else -4), 80 + i * 28) for i in range(11)]
        pts = [(x0, 70)] + [(x0 + side * 290, 64)] + edge + [(x0 + side * 290, 372), (x0, 380)]
        el(root, "path", d=path(pts), fill="#d9c28e" if side < 0 else "#dcc896")
        for i in range(12):
            y = 104 + i * 21
            length = 230 - (i % 3) * 18 - (40 if i == 11 else 0)
            start = 128 if side < 0 else 434
            el(root, "line", x1=start, y1=y, x2=start + length, y2=y, stroke="#6b4e33", stroke_width=3, stroke_opacity=0.55, stroke_dasharray="14 5 8 6 20 4")
        for i in range(9):
            el(root, "line", x1=x0 + side * 20, y1=90 + i * 34, x2=x0 + side * 280, y2=88 + i * 34, stroke="#c4ab76", stroke_width=1, stroke_opacity=0.6)
    el(root, "line", x1=400, y1=70, x2=400, y2=380, stroke="#8a7550", stroke_width=4)
    el(root, "path", d="M640 120 C 660 140, 650 170, 680 190 L700 160 C 670 150, 676 128, 640 120 Z", fill="#3a322a")
    el(root, "path", d="M140 300 C 120 320, 128 350, 104 366 L130 372 C 140 350, 150 330, 140 300 Z", fill="#3a322a")
    return root


def story_procession() -> ET.Element:
    root = scene("story-procession", "People of the story | 故事中的人物",
                 "A long line of people of many ages and backgrounds walks along one winding road from a dim dawn on the left toward a bright horizon on the right. | "
                 "许多年龄和背景各不相同的人沿着同一条蜿蜒的路，从左边微明的清晨走向右边明亮的地平线。", "#e9e2d3")
    for i in range(8):
        el(root, "rect", x=i * 50, y=0, width=50, height=450, fill="#b9b3a8", fill_opacity=f"{0.42 - i * 0.05:.2f}")
    el(root, "circle", cx=720, cy=170, r=120, fill="#f2c56b", fill_opacity=0.35)
    el(root, "circle", cx=720, cy=170, r=60, fill="#f2c56b", fill_opacity=0.6)
    ground(root, 250, "#a9b88e", 10, 640)
    el(root, "path", d="M0 410 C 160 380, 260 330, 400 320 C 540 310, 640 270, 800 240 L800 262 C 650 292, 540 334, 410 344 C 280 354, 170 404, 0 440 Z", fill="#d6c8a4")
    for i in range(14):
        t = i / 13
        x = 40 + t * 700
        y = 418 - 150 * t + 12 * math.sin(t * 6)
        scale = 1.05 - 0.45 * t
        person(root, x, y, ROBES[i % len(ROBES)], SKIN[(i * 2) % len(SKIN)], scale)
    return root


def parchment_map() -> ET.Element:
    root = scene("parchment-map", "An old map | 一幅旧地图",
                 "A sheet of old parchment shows hills, a sea with waves, a winding dotted road between small towns, and a compass rose in the corner. | "
                 "一张旧羊皮纸上画着山丘、起伏的海、连接几座小城的蜿蜒虚线道路，角落里有一个罗盘。", "#5a4630")
    el(root, "path", d="M70 50 L730 40 L750 400 L60 410 Z", fill="#e9d6a6")
    el(root, "path", d="M70 50 L730 40 L750 400 L60 410 Z", fill="none", stroke="#b89a62", stroke_width=6)
    el(root, "path", d="M60 410 C 120 380, 140 300, 110 250 C 90 200, 130 140, 120 50 L70 50 Z", fill="#9cc0c8", fill_opacity=0.7)
    for y in (120, 180, 240, 300, 360):
        el(root, "path", d=f"M78 {y} q 8 -6 16 0 t 16 0", fill="none", stroke="#3f6c7a", stroke_width=2)
    for x, y, size in [(330, 130, 34), (372, 120, 44), (414, 134, 30), (560, 270, 36), (600, 262, 46)]:
        el(root, "path", d=f"M{x - size} {y + size * 0.6} L{x} {y - size * 0.6} L{x + size} {y + size * 0.6} Z", fill="#c4a777", stroke="#7a5537", stroke_width=2)
    road = [(170, 330), (240, 300), (300, 320), (380, 260), (460, 240), (520, 300), (640, 340), (700, 300)]
    el(root, "path", d=path(road, close=False), fill="none", stroke="#8b4b45", stroke_width=4, stroke_dasharray="10 8", stroke_linecap="round")
    for x, y in (road[0], road[3], road[5], road[7]):
        el(root, "rect", x=x - 10, y=y - 12, width=20, height=14, fill="#8e6644")
        el(root, "path", d=f"M{x - 13} {y - 12} L{x} {y - 22} L{x + 13} {y - 12} Z", fill="#6b4e33")
    cx, cy = 640, 120
    el(root, "circle", cx=cx, cy=cy, r=46, fill="none", stroke="#7a5537", stroke_width=2)
    for angle, length in ((0, 52), (90, 52), (180, 52), (270, 52), (45, 30), (135, 30), (225, 30), (315, 30)):
        a = math.radians(angle - 90)
        tip = (cx + length * math.cos(a), cy + length * math.sin(a))
        left = (cx + 8 * math.cos(a - math.pi / 2), cy + 8 * math.sin(a - math.pi / 2))
        right = (cx + 8 * math.cos(a + math.pi / 2), cy + 8 * math.sin(a + math.pi / 2))
        el(root, "path", d=path([left, tip, right]), fill="#8b4b45" if angle == 0 else "#7a5537")
    el(root, "circle", cx=cx, cy=cy, r=5, fill="#e9d6a6", stroke="#7a5537", stroke_width=2)
    return root


def lost_sheep() -> ET.Element:
    root = scene("lost-sheep", "The sheep that was found | 找回的羊",
                 "On a rocky hillside at sunset, a shepherd walks home carrying a found sheep across his shoulders, with the rest of the flock waiting below. | "
                 "夕阳下的石头山坡上，牧人把找回的羊扛在肩上走回家，其余的羊群在山下等候。", "#f1dcc0")
    el(root, "circle", cx=160, cy=150, r=70, fill="#eaa94a", fill_opacity=0.75)
    el(root, "path", d="M0 300 C 160 230, 320 250, 480 200 C 600 170, 700 190, 800 160 L800 450 L0 450 Z", fill="#b9a479")
    el(root, "path", d="M0 380 C 200 350, 420 380, 800 340 L800 450 L0 450 Z", fill="#8fa06a")
    for x, y in [(520, 214), (600, 196), (690, 186), (90, 300)]:
        el(root, "path", d=f"M{x - 22} {y} C {x - 18} {y - 18}, {x + 18} {y - 18}, {x + 22} {y} Z", fill="#9c8d72")
    for x, y in [(110, 392), (170, 404), (230, 396), (150, 376)]:
        el(root, "path", d=f"M{x - 20} {y} C {x - 24} {y - 24}, {x + 20} {y - 28}, {x + 22} {y} Z", fill="#f4efe3")
        el(root, "circle", cx=x + 24, cy=y - 14, r=7, fill="#cfc4ae")
    g = ET.SubElement(root, NS + "g", {"transform": "translate(430 330) scale(2.1)"})
    el(g, "path", d="M-13 0 L-9 -44 C -8 -50, 8 -50, 9 -44 L13 0 Z", fill="#4f6b52")
    el(g, "path", d="M-26 -42 C -28 -56, -10 -60, 0 -57 C 10 -60, 28 -56, 26 -42 C 20 -36, -20 -36, -26 -42 Z", fill="#f4efe3")
    el(g, "circle", cx=-29, cy=-48, r=5.5, fill="#cfc4ae")
    for x in (-22, -16, 16, 22):
        el(g, "line", x1=x, y1=-40, x2=x + (2 if x > 0 else -2), y2=-31, stroke="#cfc4ae", stroke_width=2, stroke_linecap="round")
    el(g, "circle", cx=0, cy=-62, r=8.5, fill="#b07a55")
    el(g, "line", x1=16, y1=0, x2=22, y2=-60, stroke="#7a5537", stroke_width=2.4, stroke_linecap="round")
    el(g, "path", d="M22 -60 C 22 -68, 30 -68, 30 -62", fill="none", stroke="#7a5537", stroke_width=2.4, stroke_linecap="round")
    return root


def lamp_path() -> ET.Element:
    root = scene("lamp-path", "A lamp for the path | 脚前的灯",
                 "At night, a small oil lamp held low lights the next few steps of a winding path through dark hills. | "
                 "夜里，一盏放低的小油灯照亮了穿过幽暗山丘的蜿蜒小路上接下来的几步。", "#1f2638")
    stars(root, [(90, 50), (210, 90), (330, 40), (520, 70), (650, 110), (740, 50)])
    el(root, "path", d="M0 230 C 160 190, 320 220, 460 200 C 600 180, 700 200, 800 190 L800 450 L0 450 Z", fill="#2b3229")
    el(root, "path", d="M0 300 C 200 270, 420 300, 800 270 L800 450 L0 450 Z", fill="#323a2e")
    el(root, "path", d="M300 450 C 330 400, 300 360, 380 330 C 440 310, 470 290, 520 260 L532 262 C 486 296, 456 318, 396 340 C 324 368, 352 406, 336 450 Z", fill="#4a4a3c")
    el(root, "circle", cx=330, cy=392, r=120, fill="#f2c56b", fill_opacity=0.10)
    el(root, "circle", cx=330, cy=392, r=70, fill="#f2c56b", fill_opacity=0.16)
    el(root, "path", d="M300 450 C 330 400, 300 360, 380 330 L396 340 C 324 368, 352 406, 336 450 Z", fill="#c9b48a", fill_opacity=0.55)
    el(root, "path", d="M290 382 C 290 368, 344 366, 352 374 L364 370 L360 384 C 344 392, 300 394, 290 382 Z", fill="#b5793f")
    el(root, "path", d="M360 370 C 354 354, 360 342, 366 332 C 372 344, 374 358, 368 370 Z", fill="#f0a93a")
    el(root, "path", d="M362 366 C 360 358, 362 350, 366 344 C 369 352, 369 360, 366 366 Z", fill="#fbe08a")
    el(root, "path", d="M300 386 C 290 404, 270 414, 250 420", fill="none", stroke="#b07a55", stroke_width=12, stroke_linecap="round")
    return root


def incense_rising() -> ET.Element:
    root = scene("incense-rising", "Prayer like incense | 祷告如香",
                 "In a dim room, thin smoke curls up from a small bronze incense bowl on a stand toward a high window full of light. | "
                 "昏暗的屋子里，一缕细烟从架上的小铜香炉袅袅升起，飘向一扇充满光亮的高窗。", "#3a3430")
    el(root, "rect", x=470, y=50, width=130, height=150, rx=60, fill="#f6e7b0")
    el(root, "line", x1=535, y1=50, x2=535, y2=200, stroke="#3a3430", stroke_width=5)
    el(root, "line", x1=470, y1=130, x2=600, y2=130, stroke="#3a3430", stroke_width=5)
    el(root, "path", d="M470 200 L600 200 L520 450 L250 450 Z", fill="#f6e7b0", fill_opacity=0.06)
    el(root, "path", d="M0 380 L800 380 L800 450 L0 450 Z", fill="#4e4339")
    el(root, "rect", x=318, y=300, width=14, height=80, fill="#8f5c2f")
    el(root, "path", d="M290 380 L360 380 L346 366 L304 366 Z", fill="#8f5c2f")
    el(root, "path", d="M286 280 C 288 308, 362 308, 364 280 Z", fill="#b5793f")
    el(root, "rect", x=282, y=274, width=86, height=10, rx=4, fill="#c69a3e")
    for i, (dx, op) in enumerate([(0, 0.55), (14, 0.4), (-12, 0.35)]):
        x = 325 + dx
        el(root, "path", d=f"M{x} 272 C {x - 30} 236, {x + 30} 206, {x} 170 C {x - 30} 136, {x + 40} 110, {x + 90 + i * 20} 80",
           fill="none", stroke="#d8d2c6", stroke_width=5 - i, stroke_opacity=op, stroke_linecap="round")
    el(root, "circle", cx=325, cy=276, r=26, fill="#f0a93a", fill_opacity=0.15)
    return root


def notebook_pen() -> ET.Element:
    root = scene("notebook-pen", "Notes to keep | 记下的笔记",
                 "An open notebook with neat lines of handwriting lies beside a pen, an open Bible, and a cup on a wooden table. | "
                 "木桌上摊着一本写满整齐字迹的笔记本，旁边有一支笔、一本打开的圣经和一只杯子。", "#e9e1cf")
    el(root, "rect", x=0, y=0, width=800, height=450, rx=18, fill="#b08a62")
    for i in range(6):
        el(root, "line", x1=0, y1=50 + i * 72, x2=800, y2=70 + i * 72, stroke="#a07c56", stroke_width=3)
    el(root, "path", d="M90 300 L250 320 L410 300 L410 120 L250 140 L90 120 Z", fill="#7c5a3a")
    el(root, "path", d="M100 296 L246 314 L246 146 L100 128 Z", fill="#f4efe3")
    el(root, "path", d="M400 296 L254 314 L254 146 L400 128 Z", fill="#fbf8f0")
    for side, x0 in ((-1, 112), (1, 266)):
        for r in range(7):
            y = 160 + r * 19
            el(root, "line", x1=x0, y1=y + (r * 0.4), x2=x0 + 120 - (r % 3) * 14, y2=y + (r * 0.4), stroke="#9a8f7c", stroke_width=2.4, stroke_linecap="round")
    el(root, "rect", x=470, y=150, width=210, height=150, rx=6, fill="#fbf8f0", stroke="#c9b8a0", stroke_width=2)
    el(root, "line", x1=495, y1=150, x2=495, y2=300, stroke="#c4574a", stroke_width=2, stroke_opacity=0.6)
    for r in range(6):
        el(root, "line", x1=508, y1=178 + r * 20, x2=660 - (r % 2) * 30, y2=178 + r * 20, stroke="#3f6c7a", stroke_width=2.4, stroke_linecap="round", stroke_dasharray="18 6 30 8" if r % 2 else "26 5 12 7")
    el(root, "line", x1=520, y1=350, x2=700, y2=270, stroke="#2f3a2f", stroke_width=9, stroke_linecap="round")
    el(root, "path", d="M700 270 L716 263 L708 278 Z", fill="#c69a3e")
    el(root, "circle", cx=690, cy=380, r=40, fill="#8f5c2f")
    el(root, "circle", cx=690, cy=380, r=30, fill="#5a3e28")
    el(root, "path", d="M730 372 C 752 372, 752 396, 728 394", fill="none", stroke="#8f5c2f", stroke_width=7)
    return root


def study_desk() -> ET.Element:
    root = scene("study-desk", "Reading with a guide | 带着导读来读",
                 "A desk lamp shines on a stack of books, one open book with a bookmark, and a small notebook beside it. | "
                 "台灯照着一摞书、一本夹着书签的打开的书，旁边放着一本小笔记本。", "#2f3a35")
    el(root, "circle", cx=520, cy=210, r=230, fill="#f2c56b", fill_opacity=0.10)
    el(root, "path", d="M0 330 L800 330 L800 450 L0 450 Z", fill="#6b4e33")
    el(root, "rect", x=0, y=322, width=800, height=12, fill="#8e6644")
    for i, (w, color) in enumerate([(200, "#456346"), (186, "#8b4b45"), (210, "#3f6c7a"), (176, "#c69a3e")]):
        el(root, "rect", x=90 + (i % 2) * 8, y=300 - i * 30, width=w, height=26, rx=3, fill=color)
        el(root, "line", x1=100 + (i % 2) * 8, y1=313 - i * 30, x2=80 + w, y2=313 - i * 30, stroke="#f4efe3", stroke_width=2, stroke_opacity=0.5)
    el(root, "path", d="M360 318 L470 300 L580 318 L580 250 L470 232 L360 250 Z", fill="#7c5a3a")
    el(root, "path", d="M368 314 L466 298 L466 238 L368 254 Z", fill="#f4efe3")
    el(root, "path", d="M572 314 L474 298 L474 238 L572 254 Z", fill="#fbf8f0")
    el(root, "path", d="M520 244 L532 244 L532 300 L526 292 L520 300 Z", fill="#c4574a")
    el(root, "rect", x=610, y=286, width=90, height=34, rx=4, fill="#e9d6a6")
    el(root, "line", x1=700, y1=330, x2=700, y2=170, stroke="#3a3530", stroke_width=8)
    el(root, "path", d="M700 170 L620 130 L600 170 L660 190 Z", fill="#456346")
    el(root, "path", d="M610 175 L650 188 L520 300 L430 300 Z", fill="#fbe08a", fill_opacity=0.18)
    el(root, "rect", x=670, y=322, width=60, height=10, rx=3, fill="#3a3530")
    return root


def lyre_dawn() -> ET.Element:
    root = scene("lyre-dawn", "A song at dawn | 黎明的诗歌",
                 "At dawn, a simple wooden lyre rests against a rock beside still water, with the first light on the hills. | "
                 "黎明时分，一把简朴的木制竖琴靠在静水边的岩石上，山丘上映着第一道晨光。", "#f0dcc4")
    el(root, "circle", cx=600, cy=250, r=110, fill="#f2c56b", fill_opacity=0.45)
    el(root, "circle", cx=600, cy=250, r=60, fill="#eaa94a", fill_opacity=0.85)
    el(root, "path", d="M0 250 C 140 200, 300 230, 440 210 C 560 194, 680 220, 800 200 L800 290 L0 290 Z", fill="#b9a479")
    el(root, "path", d=path([(0, 290)] + wave(0, 800, 290, 3, 260) + [(800, 450), (0, 450)]), fill="#9cc0c8")
    for y in (320, 350, 385):
        el(root, "line", x1=520, y1=y, x2=680, y2=y, stroke="#f6e7b0", stroke_width=3, stroke_opacity=0.5, stroke_linecap="round")
    el(root, "path", d="M80 450 C 90 360, 180 330, 300 340 C 360 346, 390 400, 400 450 Z", fill="#8d8474")
    g = ET.SubElement(root, NS + "g", {"transform": "translate(250 340) rotate(-12)"})
    el(g, "path", d="M-60 0 C -70 -60, -60 -120, -40 -150 L-28 -146 C -44 -116, -50 -60, -44 0 Z", fill="#8e6644")
    el(g, "path", d="M60 0 C 70 -60, 60 -120, 40 -150 L28 -146 C 44 -116, 50 -60, 44 0 Z", fill="#8e6644")
    el(g, "rect", x=-50, y=-158, width=100, height=14, rx=5, fill="#6b4e33")
    el(g, "path", d="M-60 -6 L60 -6 L56 26 L-56 26 Z", fill="#7a5537")
    for x in range(-36, 40, 12):
        el(g, "line", x1=x, y1=-146, x2=x * 0.9, y2=-6, stroke="#f4efe3", stroke_width=1.6, stroke_opacity=0.85)
    return root


def booths_harvest() -> ET.Element:
    root = scene("booths-harvest", "Living in booths | 住在棚里",
                 "Under a starry autumn sky, small shelters roofed with leafy branches glow with lamplight, beside baskets of grapes and bundles of grain. | "
                 "秋夜星空下，几座用带叶树枝盖顶的小棚透出灯光，旁边有一筐筐葡萄和一捆捆谷物。", "#1f2b46")
    stars(root, [(60, 50), (150, 100), (260, 40), (380, 80), (520, 50), (640, 90), (740, 40)])
    el(root, "circle", cx=680, cy=110, r=34, fill="#f4efe3", fill_opacity=0.9)
    ground(root, 330, "#3b3a30", 8, 600)
    for x, w in [(140, 170), (380, 190), (620, 160)]:
        el(root, "rect", x=x - w / 2, y=230, width=w, height=110, fill="#6b4e2e")
        el(root, "circle", cx=x, cy=300, r=60, fill="#f2c56b", fill_opacity=0.28)
        for px in (x - w / 2, x + w / 2 - 8):
            el(root, "rect", x=px, y=226, width=8, height=114, fill="#7a5537")
        for i in range(7):
            cx = x - w / 2 + 10 + i * (w - 20) / 6
            el(root, "circle", cx=f"{cx:.1f}", cy=222 + (i % 2) * 6, r=22, fill="#4f7d45" if i % 2 else "#5f8f50")
        el(root, "circle", cx=x, cy=300, r=8, fill="#fbe08a")
        el(root, "circle", cx=x, cy=300, r=26, fill="#fbe08a", fill_opacity=0.2)
    for x in (270, 510):
        el(root, "path", d=f"M{x - 24} 372 L{x + 24} 372 L{x + 18} 400 L{x - 18} 400 Z", fill="#a86f3c")
        for j in range(6):
            el(root, "circle", cx=x - 15 + (j % 3) * 15, cy=364 - (j // 3) * 10, r=7, fill="#7b4f6b")
    for x in (720, 60):
        for k in range(5):
            el(root, "line", x1=x + k * 4, y1=400, x2=x - 10 + k * 8, y2=340, stroke="#d8b47a", stroke_width=3)
        el(root, "line", x1=x - 4, y1=378, x2=x + 22, y2=378, stroke="#8e6644", stroke_width=4)
    return root


def loaves_fish() -> ET.Element:
    root = scene("loaves-fish", "Five loaves and two fish | 五饼二鱼",
                 "On green grass by a lake, a woven basket holds five round loaves and two small fish. | "
                 "湖边的青草地上，一只编织篮里放着五个圆饼和两条小鱼。", "#e4eef0")
    el(root, "path", d=path([(0, 200)] + wave(0, 800, 196, 4, 260) + [(800, 240), (0, 240)]), fill="#7fb7c4")
    el(root, "path", d="M0 230 C 200 210, 520 236, 800 214 L800 450 L0 450 Z", fill="#8fb46e")
    for x, y in [(80, 300), (150, 410), (640, 290), (720, 400), (560, 420)]:
        el(root, "path", d=f"M{x} {y} l-6 -16 m6 16 l0 -18 m0 18 l6 -16", fill="none", stroke="#4f7d45", stroke_width=3, stroke_linecap="round")
    el(root, "path", d="M240 300 C 240 400, 560 400, 560 300 Z", fill="#b5793f")
    for i in range(6):
        y = 312 + i * 13
        el(root, "path", d=f"M{246 + i * 6} {y} C {320} {y + 8}, {480} {y + 8}, {554 - i * 6} {y}", fill="none", stroke="#8f5c2f", stroke_width=2)
    el(root, "path", d="M232 300 L568 300 L560 314 L240 314 Z", fill="#9b6634")
    for x, y in [(300, 288), (360, 280), (420, 284), (480, 290), (390, 262)]:
        el(root, "ellipse" if False else "circle", cx=x, cy=y, r=30, fill="#d9a35c")
        el(root, "path", d=f"M{x - 16} {y - 6} C {x - 6} {y - 14}, {x + 6} {y - 14}, {x + 16} {y - 6}", fill="none", stroke="#b5793f", stroke_width=3, stroke_linecap="round")
    for x, y, flip in [(330, 250, 1), (450, 246, -1)]:
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y}) scale({flip} 1) rotate(-12)"})
        el(g, "path", d="M-46 0 C -30 -18, 20 -18, 34 0 C 20 18, -30 18, -46 0 Z", fill="#8a9aa6")
        el(g, "path", d="M34 0 L54 -14 L50 0 L54 14 Z", fill="#7a8a96")
        el(g, "circle", cx=-30, cy=-3, r=3, fill="#2f3a2f")
    return root


def scribe_copying() -> ET.Element:
    root = scene("scribe-copying", "Copying by hand | 手抄流传",
                 "By the light of an oil lamp, a scribe at a low table copies lines from an open scroll onto a fresh sheet, with ink and a reed pen beside him. | "
                 "油灯光下，一位抄写员坐在矮桌前，把展开的书卷上的字一行行抄到新的纸上，旁边放着墨水和芦苇笔。", "#3a322a")
    el(root, "circle", cx=520, cy=240, r=220, fill="#f2c56b", fill_opacity=0.10)
    el(root, "path", d="M0 360 L800 360 L800 450 L0 450 Z", fill="#2a241e")
    el(root, "rect", x=300, y=300, width=420, height=20, rx=4, fill="#8e6644")
    for x in (320, 690):
        el(root, "rect", x=x, y=318, width=14, height=50, fill="#6b4e33")
    el(root, "rect", x=330, y=284, width=170, height=18, rx=9, fill="#d9c28e")
    el(root, "circle", cx=330, cy=293, r=12, fill="#c4ab76")
    el(root, "circle", cx=500, cy=293, r=12, fill="#c4ab76")
    for i in range(3):
        el(root, "line", x1=350, y1=289 + i * 4, x2=480, y2=289 + i * 4, stroke="#6b4e33", stroke_width=1.5, stroke_opacity=0.6)
    el(root, "path", d="M530 300 L650 300 L644 282 L536 282 Z", fill="#f4efe3")
    for i in range(3):
        el(root, "line", x1=546, y1=287 + i * 4, x2=600 + i * 10, y2=287 + i * 4, stroke="#6b4e33", stroke_width=1.5, stroke_opacity=0.7)
    el(root, "rect", x=664, y=284, width=16, height=16, rx=3, fill="#2f2a26")
    el(root, "path", d="M710 262 C 700 270, 712 282, 722 276 L726 284 L732 270 C 734 262, 720 256, 710 262 Z", fill="#b5793f")
    el(root, "path", d="M728 264 C 724 250, 730 240, 734 232 C 740 242, 740 254, 734 264 Z", fill="#f0a93a")
    g = ET.SubElement(root, NS + "g", {"transform": "translate(230 360) scale(2.2)"})
    el(g, "path", d="M-24 0 C -26 -14, -16 -22, -6 -22 L-2 -48 C 0 -56, 16 -56, 18 -48 L24 -20 C 30 -14, 32 -6, 30 0 Z", fill="#7b5d84")
    el(g, "circle", cx=8, cy=-62, r=9, fill="#8a5f43")
    el(g, "path", d="M-1 -66 C 0 -74, 16 -74, 17 -66 Z", fill="#e8e1d2")
    el(g, "line", x1=18, y1=-40, x2=40, y2=-34, stroke="#8a5f43", stroke_width=5, stroke_linecap="round")
    el(g, "line", x1=40, y1=-34, x2=46, y2=-44, stroke="#c69a3e", stroke_width=1.5)
    return root


def burning_bush() -> ET.Element:
    root = scene("burning-bush", "The bush that was not consumed | 荆棘被火烧着却没有烧毁",
                 "In a quiet desert below a mountain, a thorny bush burns with bright flames while its branches stay whole; a pair of sandals lies on the sand nearby. | "
                 "山脚下寂静的旷野里，一丛荆棘燃着明亮的火焰，枝子却完好无损；旁边的沙地上放着一双鞋。", "#3b2f3f")
    stars(root, [(70, 60), (180, 110), (300, 50), (610, 70), (700, 120), (760, 50)])
    el(root, "path", d="M0 300 L150 190 L240 240 L360 130 L470 220 L560 170 L700 260 L800 230 L800 330 L0 330 Z", fill="#4a3b48")
    ground(root, 320, "#8a6a4a", 6, 600)
    el(root, "circle", cx=400, cy=270, r=170, fill="#f2c56b", fill_opacity=0.10)
    el(root, "circle", cx=400, cy=270, r=100, fill="#f6b04f", fill_opacity=0.16)
    el(root, "line", x1=400, y1=372, x2=400, y2=300, stroke="#5a3e2a", stroke_width=9, stroke_linecap="round")
    for x1, y1, x2, y2 in [(400, 338, 362, 300), (400, 330, 440, 296)]:
        el(root, "line", x1=x1, y1=y1, x2=x2, y2=y2, stroke="#5a3e2a", stroke_width=6, stroke_linecap="round")
    for x, y, r in [(340, 292, 26), (372, 276, 30), (410, 270, 32), (448, 282, 28), (466, 300, 20), (330, 308, 18), (400, 300, 30)]:
        el(root, "circle", cx=x, cy=y, r=r, fill="#5b4a2e")
    flames = [(404, 150, 64, 280), (360, 196, 44, 286), (450, 192, 46, 288), (330, 232, 28, 296), (476, 230, 28, 298)]
    for x, top, w, base in flames:
        el(root, "path", d=f"M{x - w / 2} {base} C {x - w / 2} {base - 50}, {x - w / 6} {top + 40}, {x} {top} C {x + w / 6} {top + 40}, {x + w / 2} {base - 50}, {x + w / 2} {base} C {x + w / 4} {base + 14}, {x - w / 4} {base + 14}, {x - w / 2} {base} Z",
           fill="#ef8a3a", fill_opacity=0.88)
        el(root, "path", d=f"M{x - w / 4} {base} C {x - w / 4} {base - 30}, {x - w / 10} {top + 60}, {x} {top + 34} C {x + w / 10} {top + 60}, {x + w / 4} {base - 30}, {x + w / 4} {base} C {x + w / 8} {base + 8}, {x - w / 8} {base + 8}, {x - w / 4} {base} Z",
           fill="#fbe08a", fill_opacity=0.92)
    for x1, y1, x2, y2 in [(372, 280, 352, 238), (410, 272, 404, 222), (448, 284, 468, 244)]:
        el(root, "line", x1=x1, y1=y1, x2=x2, y2=y2, stroke="#5a3e2a", stroke_width=4, stroke_linecap="round")
    el(root, "path", d="M356 374 C 380 362, 420 362, 444 374 Z", fill="#6b5038")
    for x in (178, 208):
        el(root, "rect", x=x, y=372, width=20, height=46, rx=10, fill="#7a5537")
        for y in (384, 400):
            el(root, "line", x1=x + 2, y1=y, x2=x + 18, y2=y, stroke="#4e3624", stroke_width=3)
    return root


def temple_courts() -> ET.Element:
    root = scene("temple-courts", "The temple courts | 圣殿的院子",
                 "In morning light, a tall white sanctuary rises above long colonnades on a great stone platform, as small figures climb the broad steps. | "
                 "晨光中，一座高大的白色圣所矗立在巨大石台上的长廊之上，几个小小的人影正走上宽阔的台阶。", "#efe4cc")
    el(root, "circle", cx=130, cy=90, r=40, fill="#f2c56b", fill_opacity=0.8)
    el(root, "path", d=path([(0, 330)] + wave(0, 800, 320, 10, 500, 0.3) + [(800, 450), (0, 450)]), fill="#c9b48a")
    el(root, "rect", x=120, y=250, width=560, height=80, fill="#d9c9a3")
    for i in range(9):
        el(root, "line", x1=120, y1=262 + i * 8, x2=680, y2=262 + i * 8, stroke="#c6b48c", stroke_width=1.5)
    el(root, "rect", x=140, y=212, width=520, height=38, fill="#e9dfc6")
    el(root, "rect", x=134, y=204, width=532, height=10, fill="#cdbb92")
    for i in range(27):
        x = 150 + i * 19.5
        el(root, "rect", x=f"{x:.1f}", y=214, width=7, height=36, fill="#c9b78f")
    el(root, "rect", x=330, y=110, width=140, height=102, fill="#f6f1e4")
    el(root, "rect", x=320, y=100, width=160, height=14, fill="#e2d5b4")
    el(root, "rect", x=376, y=140, width=48, height=72, fill="#d8b46a")
    el(root, "rect", x=384, y=150, width=32, height=62, fill="#b98c4a")
    el(root, "rect", x=300, y=170, width=30, height=42, fill="#efe6d0")
    el(root, "rect", x=470, y=170, width=30, height=42, fill="#efe6d0")
    el(root, "path", d="M400 98 C 392 80, 410 70, 402 52 C 396 40, 410 34, 406 24", fill="none", stroke="#b8ab95", stroke_width=4, stroke_linecap="round", stroke_opacity=0.7)
    el(root, "path", d="M330 330 L470 330 L500 400 L300 400 Z", fill="#e3d4b0")
    for i in range(6):
        y = 340 + i * 10
        el(root, "line", x1=330 - i * 5, y1=y, x2=470 + i * 5, y2=y, stroke="#cbb88f", stroke_width=2)
    person(root, 360, 392, "#7a5f8f", "#c99a6e", 0.55)
    person(root, 430, 372, "#4f7d6a", "#b8875c", 0.5)
    person(root, 452, 396, "#a35d3c", "#c99a6e", 0.55)
    return root


def dig_layers() -> ET.Element:
    root = scene("dig-layers", "Layers in the ground | 地下的地层",
                 "A cut-away view of an excavation shows soil layers stacked one above another, with pottery shards, a coin, and old wall stones, and a trowel and brush resting at the top. | "
                 "考古发掘的剖面图：一层层土壤上下叠压，夹着陶片、一枚钱币和古老的墙石，顶上放着一把小铲和一把刷子。", "#e4ecee")
    el(root, "path", d="M0 120 L800 120 L800 450 L0 450 Z", fill="#c9a87a")
    layers = [(120, 170, "#8fa86a"), (170, 230, "#b88f5e"), (230, 290, "#a57a4e"), (290, 350, "#c4a173"), (350, 410, "#8e6a46"), (410, 450, "#77593c")]
    for top, bottom, color in layers:
        el(root, "path", d=path([(0, top)] + wave(0, 800, top, 4, 300, top / 90) + [(800, bottom), (0, bottom)]), fill=color)
    for x in range(30, 800, 70):
        el(root, "line", x1=x, y1=170, x2=x + 8, y2=150, stroke="#5f7d45", stroke_width=3, stroke_linecap="round")
    for x, y, rot in [(190, 262, -12), (520, 250, 18), (330, 382, 8), (640, 320, -20)]:
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({x} {y}) rotate({rot})"})
        el(g, "path", d="M-26 -6 C -12 -16, 12 -16, 26 -6 L20 10 L-20 10 Z", fill="#c06a3c")
        el(g, "path", d="M-20 -2 C -8 -9, 8 -9, 20 -2", fill="none", stroke="#8f4a28", stroke_width=2)
    el(root, "circle", cx=420, cy=316, r=11, fill="#d8b46a")
    el(root, "circle", cx=420, cy=316, r=6, fill="none", stroke="#a8823e", stroke_width=2)
    for i, x in enumerate(range(560, 760, 46)):
        el(root, "rect", x=x, y=360 + (i % 2) * 4, width=42, height=24, rx=3, fill="#9b958a")
        el(root, "rect", x=x + 22, y=386 + (i % 2) * 4, width=42, height=22, rx=3, fill="#8a8479")
    el(root, "line", x1=110, y1=114, x2=190, y2=112, stroke="#7a5537", stroke_width=7, stroke_linecap="round")
    el(root, "path", d="M190 104 L250 112 L190 120 Z", fill="#8a9aa6")
    el(root, "line", x1=540, y1=114, x2=610, y2=112, stroke="#a86f3c", stroke_width=6, stroke_linecap="round")
    el(root, "rect", x=606, y=100, width=26, height=22, rx=4, fill="#6b4e33")
    for k in range(5):
        el(root, "line", x1=632, y1=103 + k * 4, x2=652, y2=101 + k * 5, stroke="#d8c39a", stroke_width=2)
    return root


def seven_lamps() -> ET.Element:
    root = scene("seven-lamps", "Seven lampstands | 七个灯台",
                 "Seven golden lampstands with small flames stand in a gentle arc against a deep night sky, their light shining together. | "
                 "七个金灯台排成一道柔和的弧线，立在深色夜空下，小小的火焰一同发光。", "#1f2b46")
    stars(root, [(60, 50), (160, 110), (260, 40), (400, 70), (540, 40), (650, 100), (750, 60)])
    el(root, "path", d="M0 360 C 240 340, 560 340, 800 360 L800 450 L0 450 Z", fill="#2c3550")
    for i in range(7):
        x = 100 + i * 100
        base = 360 - 26 * (1 - ((i - 3) / 3) ** 2)
        el(root, "path", d=f"M{x - 26} {base} L{x + 26} {base} L{x + 14} {base - 16} L{x - 14} {base - 16} Z", fill="#d9a441")
        el(root, "rect", x=x - 5, y=base - 126, width=10, height=112, fill="#e2b24f")
        for k in (0.3, 0.6):
            el(root, "rect", x=x - 9, y=base - 126 + 112 * k, width=18, height=6, rx=3, fill="#c99436")
        el(root, "path", d=f"M{x - 20} {base - 128} C {x - 18} {base - 116}, {x + 18} {base - 116}, {x + 20} {base - 128} Z", fill="#d9a441")
        el(root, "path", d=f"M{x} {base - 172} C {x - 14} {base - 152}, {x - 13} {base - 130}, {x} {base - 128} C {x + 13} {base - 130}, {x + 14} {base - 152}, {x} {base - 172} Z", fill="#ef8a3a")
        el(root, "path", d=f"M{x} {base - 160} C {x - 8} {base - 146}, {x - 7} {base - 132}, {x} {base - 130} C {x + 7} {base - 132}, {x + 8} {base - 146}, {x} {base - 160} Z", fill="#fbe08a")
    return root


def five_scrolls() -> ET.Element:
    root = scene("five-scrolls", "Five scrolls | 五卷书",
                 "Five rolled scrolls lie side by side on a wooden table, lit by a small oil lamp. | "
                 "五卷卷起的书卷并排放在木桌上，旁边一盏小油灯照着它们。", "#3a322a")
    el(root, "circle", cx=640, cy=270, r=170, fill="#f2c56b", fill_opacity=0.10)
    el(root, "path", d="M0 330 L800 330 L800 450 L0 450 Z", fill="#2a241e")
    el(root, "rect", x=90, y=300, width=620, height=24, rx=4, fill="#8e6644")
    for x in (120, 670):
        el(root, "rect", x=x, y=322, width=16, height=80, fill="#6b4e33")
    for i in range(5):
        x = 140 + i * 92
        y = 254
        el(root, "rect", x=x, y=y, width=56, height=46, rx=4, fill="#e9d9b4")
        for k in range(3):
            el(root, "line", x1=x + 8, y1=y + 12 + k * 11, x2=x + 48, y2=y + 12 + k * 11, stroke="#cdb88c", stroke_width=2)
        for cx in (x, x + 56):
            el(root, "rect", x=cx - 6, y=y - 6, width=12, height=58, rx=5, fill="#a8784a")
            el(root, "circle", cx=cx, cy=y - 8, r=5, fill="#7a5537")
            el(root, "circle", cx=cx, cy=y + 54, r=5, fill="#7a5537")
    el(root, "path", d="M610 300 C 610 278, 670 278, 670 300 Z", fill="#b5793f")
    el(root, "path", d="M664 286 L692 278 L690 290 L668 296 Z", fill="#b5793f")
    el(root, "path", d="M690 278 C 680 262, 692 250, 690 236 C 704 250, 706 268, 690 278 Z", fill="#fbe08a")
    return root


def split_crown() -> ET.Element:
    root = scene("split-crown", "A kingdom divided | 王国分裂",
                 "A golden crown lies broken into two halves on a stone, with a gap between them, under a gray sky. | "
                 "灰色天空下，一顶金冠断成两半，放在石头上，两半之间隔着一道缝隙。", "#d9dde0")
    el(root, "path", d=path([(0, 300)] + wave(0, 800, 292, 10, 520, 0.4) + [(800, 450), (0, 450)]), fill="#a9a08c")
    el(root, "path", d="M160 330 C 200 290, 600 290, 640 330 L660 380 L140 380 Z", fill="#8a8479")
    el(root, "path", d="M160 330 C 260 316, 540 316, 640 330", fill="none", stroke="#a39d92", stroke_width=4)
    for dx, sign in ((-34, -1), (34, 1)):
        g = ET.SubElement(root, NS + "g", {"transform": f"translate({400 + dx} 318) rotate({sign * 8})"})
        if sign < 0:
            pts = [(-130, 0), (-130, -70), (-100, -40), (-70, -90), (-40, -40), (-12, -76), (0, -60), (-8, -30), (4, 0)]
        else:
            pts = [(-4, 0), (8, -30), (0, -60), (12, -76), (40, -40), (70, -90), (100, -40), (130, -70), (130, 0)]
        el(g, "path", d=path(pts), fill="#d9a441")
        x0 = -130 if sign < 0 else -4
        el(g, "rect", x=x0, y=-22, width=134, height=22, fill="#c99436")
        for gx in ((-100, -60, -24) if sign < 0 else (24, 60, 100)):
            el(g, "circle", cx=gx, cy=-11, r=6, fill="#8e3b46" if gx % 3 else "#3f6f8f")
    return root


def roman_road() -> ET.Element:
    root = scene("roman-road", "The road to the cities | 通往城市的大路",
                 "A paved stone road with a milestone winds over green hills toward a harbor city, where a ship with a square sail waits on the sea. | "
                 "一条铺石大路经过一块里程碑，蜿蜒越过绿色山丘，通向海港城市；海面上停着一艘方帆船。", "#e4eef0")
    el(root, "path", d=path([(0, 200)] + wave(0, 800, 196, 4, 260) + [(800, 230), (0, 230)]), fill="#7fb7c4")
    el(root, "rect", x=0, y=226, width=800, height=8, fill="#7fb7c4")
    for x, w, h in [(560, 40, 40), (604, 30, 56), (640, 50, 34), (696, 36, 48), (736, 44, 30)]:
        el(root, "rect", x=x, y=230 - h, width=w, height=h, fill="#efe6d0")
        el(root, "rect", x=x, y=230 - h, width=w, height=6, fill="#c96f4a")
    el(root, "path", d="M470 200 L470 168 L500 182 Z", fill="#f4efe3")
    el(root, "path", d="M452 202 L520 202 L512 212 L460 212 Z", fill="#7a5537")
    el(root, "line", x1=486, y1=202, x2=486, y2=160, stroke="#5a3e2a", stroke_width=3)
    el(root, "rect", x=474, y=166, width=26, height=30, fill="#efe2c4")
    el(root, "path", d="M0 240 C 220 220, 520 250, 800 228 L800 450 L0 450 Z", fill="#8fb46e")
    el(root, "path", d="M0 300 C 240 270, 560 300, 800 276 L800 450 L0 450 Z", fill="#7aa35c")
    el(root, "path", d="M120 450 C 200 380, 360 330, 560 236 L590 238 C 420 340, 300 400, 280 450 Z", fill="#c9b48a")
    for i in range(14):
        t = i / 13
        x1 = 120 + (560 - 120) * t + (1 - t) * t * 60
        x2 = 280 + (590 - 280) * t + (1 - t) * t * 40
        y = 450 - (450 - 236) * t
        el(root, "line", x1=f"{x1:.1f}", y1=f"{y:.1f}", x2=f"{x2:.1f}", y2=f"{y:.1f}", stroke="#ad9a72", stroke_width=2)
    el(root, "rect", x=236, y=318, width=24, height=56, rx=10, fill="#b8b2a6")
    el(root, "line", x1=242, y1=336, x2=254, y2=336, stroke="#8a8479", stroke_width=3)
    el(root, "line", x1=242, y1=346, x2=254, y2=346, stroke="#8a8479", stroke_width=3)
    for x, y in [(60, 330), (700, 330), (740, 380), (90, 400)]:
        el(root, "circle", cx=x, cy=y, r=20, fill="#4f7d45")
        el(root, "rect", x=x - 3, y=y + 14, width=6, height=16, fill="#6b4e33")
    return root


def scroll_jars() -> ET.Element:
    root = scene("scroll-jars", "Scrolls kept in jars | 存放在陶罐里的书卷",
                 "Inside the mouth of a rocky cave, tall clay jars hold rolled scrolls, while the desert and a pale sky show through the opening. | "
                 "岩洞口内，几只高高的陶罐里放着卷起的书卷，透过洞口可以看见旷野和淡色的天空。", "#5a4a3c")
    el(root, "path", d="M210 60 C 330 20, 520 30, 600 90 C 640 140, 630 240, 600 330 L200 330 C 170 240, 160 120, 210 60 Z", fill="#f0e2c4")
    el(root, "path", d="M200 330 C 300 290, 500 300, 600 330 Z", fill="#d8b98a")
    el(root, "path", d="M240 300 C 320 260, 420 250, 560 290 L600 330 L200 330 Z", fill="#e3c58e")
    el(root, "path", d="M0 330 L800 330 L800 450 L0 450 Z", fill="#4a3d32")
    for x, h in [(270, 130), (360, 150), (450, 120), (540, 140)]:
        base = 400
        el(root, "path", d=f"M{x - 30} {base} C {x - 44} {base - h * 0.5}, {x - 36} {base - h + 10}, {x - 18} {base - h} L{x + 18} {base - h} C {x + 36} {base - h + 10}, {x + 44} {base - h * 0.5}, {x + 30} {base} Z", fill="#c48a52")
        el(root, "rect", x=x - 22, y=base - h - 8, width=44, height=10, rx=4, fill="#a86f3c")
        for k in (0.35, 0.6):
            el(root, "line", x1=x - 34, y1=base - h * k, x2=x + 34, y2=base - h * k, stroke="#a86f3c", stroke_width=2)
        el(root, "rect", x=x - 7, y=base - h - 30, width=14, height=26, rx=6, fill="#e9d9b4")
    for x, y in [(650, 404), (690, 410)]:
        el(root, "rect", x=x - 26, y=y - 10, width=52, height=18, rx=8, fill="#e9d9b4")
    return root


def four_clocks() -> ET.Element:
    root = scene("four-clocks", "Four kinds of time | 四种时间",
                 "Four round dials stand in a row; inside them are a small figure walking a path, a pen, a scroll, and an open book, for the time of the story, the writing, the copies, and later readers. | "
                 "四个圆形表盘排成一行，里面分别是一个走在路上的小人、一支笔、一卷书和一本打开的书，代表故事发生、写作成书、抄本流传和后人阅读的时间。", "#e9ecef")
    el(root, "path", d="M0 330 C 260 316, 540 316, 800 330 L800 450 L0 450 Z", fill="#cfd6cf")
    colors = ["#c96f4a", "#d9a441", "#4f7d6a", "#3f6f8f"]
    for i, color in enumerate(colors):
        cx = 130 + i * 180
        cy = 210
        el(root, "circle", cx=cx, cy=cy, r=74, fill="#f7f4ec", stroke=color, stroke_width=10)
        for k in range(12):
            a = math.radians(k * 30)
            el(root, "line", x1=f"{cx + 58 * math.sin(a):.1f}", y1=f"{cy - 58 * math.cos(a):.1f}", x2=f"{cx + 64 * math.sin(a):.1f}", y2=f"{cy - 64 * math.cos(a):.1f}", stroke="#b8b2a6", stroke_width=3)
        if i == 0:
            el(root, "path", d=f"M{cx - 40} {cy + 30} C {cx - 10} {cy + 10}, {cx + 10} {cy + 34}, {cx + 40} {cy + 14}", fill="none", stroke="#d8b47a", stroke_width=6, stroke_linecap="round")
            person(root, cx, cy + 16, color, "#c99a6e", 0.6)
        elif i == 1:
            el(root, "path", d=f"M{cx - 30} {cy + 34} L{cx + 24} {cy - 30} L{cx + 34} {cy - 22} L{cx - 20} {cy + 42} Z", fill=color)
            el(root, "path", d=f"M{cx - 30} {cy + 34} L{cx - 36} {cy + 50} L{cx - 20} {cy + 42} Z", fill="#5a3e2a")
        elif i == 2:
            el(root, "rect", x=cx - 26, y=cy - 26, width=52, height=52, rx=3, fill="#e9d9b4")
            for k in range(3):
                el(root, "line", x1=cx - 18, y1=cy - 12 + k * 12, x2=cx + 18, y2=cy - 12 + k * 12, stroke="#cdb88c", stroke_width=2)
            for x in (cx - 30, cx + 30):
                el(root, "rect", x=x - 6, y=cy - 32, width=12, height=64, rx=5, fill=color)
        else:
            el(root, "path", d=f"M{cx} {cy - 22} C {cx - 16} {cy - 30}, {cx - 34} {cy - 28}, {cx - 40} {cy - 22} L{cx - 40} {cy + 26} C {cx - 30} {cy + 20}, {cx - 14} {cy + 20}, {cx} {cy + 28} Z", fill="#f2e6c8", stroke=color, stroke_width=3)
            el(root, "path", d=f"M{cx} {cy - 22} C {cx + 16} {cy - 30}, {cx + 34} {cy - 28}, {cx + 40} {cy - 22} L{cx + 40} {cy + 26} C {cx + 30} {cy + 20}, {cx + 14} {cy + 20}, {cx} {cy + 28} Z", fill="#f2e6c8", stroke=color, stroke_width=3)
        el(root, "rect", x=cx - 8, y=cy + 74, width=16, height=50, fill="#b8b2a6")
    return root


def eleven_threads() -> ET.Element:
    root = scene("eleven-threads", "Threads through the story | 贯穿故事的线",
                 "Eleven colored threads run side by side across a wooden loom, crossing a band of woven cloth. | "
                 "十一条彩色的线并排穿过一架木织机，越过一段已经织好的布。", "#f1ebdf")
    el(root, "rect", x=80, y=70, width=24, height=320, rx=6, fill="#8e6644")
    el(root, "rect", x=696, y=70, width=24, height=320, rx=6, fill="#8e6644")
    el(root, "rect", x=70, y=60, width=660, height=20, rx=6, fill="#7a5537")
    el(root, "rect", x=70, y=380, width=660, height=20, rx=6, fill="#7a5537")
    colors = ["#c96f4a", "#d9a441", "#8fb46e", "#4f7d6a", "#3f6f8f", "#7a5f8f", "#a35d3c", "#c99436", "#5f8f50", "#8e3b46", "#4a6fa0"]
    for i, color in enumerate(colors):
        y = 112 + i * 25
        el(root, "path", d=f"M104 {y} C 260 {y - 8}, 540 {y + 8}, 696 {y}", fill="none", stroke=color, stroke_width=7, stroke_linecap="round")
    el(root, "rect", x=300, y=96, width=200, height=276, fill="#e9dfc6", fill_opacity=0.55)
    for k in range(10):
        x = 310 + k * 20
        el(root, "line", x1=x, y1=96, x2=x, y2=372, stroke="#b8a888", stroke_width=4, stroke_opacity=0.7)
    return root


def stepping_stones() -> ET.Element:
    root = scene("stepping-stones", "One step to the next | 一步接一步",
                 "A line of flat stepping stones crosses a gentle stream from one green bank to the other. | "
                 "一排平整的踏脚石横过一条平缓的小溪，从一边绿岸通到另一边。", "#e4eef0")
    el(root, "path", d="M0 180 C 200 150, 380 200, 560 160 C 680 136, 760 150, 800 140 L800 450 L0 450 Z", fill="#8fb46e")
    el(root, "path", d="M0 250 C 220 230, 520 270, 800 230 L800 340 C 540 380, 260 330, 0 360 Z", fill="#7fb7c4")
    for k in range(5):
        y = 270 + k * 18
        el(root, "path", d=f"M{60 + k * 90} {y} q 20 -6 40 0", fill="none", stroke="#a9d1da", stroke_width=3, stroke_linecap="round")
        el(root, "path", d=f"M{500 + k * 50} {y + 6} q 20 -6 40 0", fill="none", stroke="#a9d1da", stroke_width=3, stroke_linecap="round")
    stones = [(110, 390, 46), (210, 352, 42), (310, 322, 40), (410, 300, 38), (505, 284, 36), (595, 268, 34), (680, 250, 32)]
    for x, y, r in stones:
        el(root, "path", d=f"M{x - r} {y} C {x - r} {y - r * 0.5}, {x + r} {y - r * 0.5}, {x + r} {y} C {x + r} {y + r * 0.35}, {x - r} {y + r * 0.35}, {x - r} {y} Z", fill="#b8b2a6")
        el(root, "path", d=f"M{x - r * 0.7} {y - r * 0.12} C {x - r * 0.3} {y - r * 0.3}, {x + r * 0.3} {y - r * 0.3}, {x + r * 0.7} {y - r * 0.12}", fill="none", stroke="#d4cfc4", stroke_width=3)
    for x, y in [(60, 210), (740, 180), (700, 410), (40, 420)]:
        el(root, "path", d=f"M{x} {y} l-6 -16 m6 16 l0 -18 m0 18 l6 -16", fill="none", stroke="#4f7d45", stroke_width=3, stroke_linecap="round")
    return root


def signpost() -> ET.Element:
    root = scene("signpost", "Which way to go | 往哪里走",
                 "At a crossroads in open country, a wooden signpost with four blank arrows points down different paths. | "
                 "旷野的十字路口，一根木路标上有四块空白的箭头牌，指向不同的道路。", "#eaf0e6")
    el(root, "path", d=path([(0, 250)] + wave(0, 800, 244, 8, 500, 0.2) + [(800, 450), (0, 450)]), fill="#9cbf7a")
    el(root, "path", d="M370 450 L410 260 L430 260 L470 450 Z", fill="#d8c39a")
    el(root, "path", d="M0 330 C 200 320, 330 300, 420 290 C 520 300, 640 330, 800 340 L800 360 C 640 352, 520 316, 420 306 C 330 316, 200 340, 0 350 Z", fill="#d8c39a")
    el(root, "rect", x=412, y=110, width=16, height=230, fill="#7a5537")
    signs = [(140, 1, "#c96f4a"), (180, -1, "#4f7d6a"), (222, 1, "#d9a441"), (262, -1, "#3f6f8f")]
    for y, d, color in signs:
        if d > 0:
            el(root, "path", d=f"M420 {y} L540 {y} L566 {y + 15} L540 {y + 30} L420 {y + 30} Z", fill=color)
        else:
            el(root, "path", d=f"M420 {y} L300 {y} L274 {y + 15} L300 {y + 30} L420 {y + 30} Z", fill=color)
    el(root, "circle", cx=420, cy=106, r=10, fill="#6b4e33")
    for x, y in [(120, 230), (680, 236), (220, 410), (640, 420)]:
        el(root, "circle", cx=x, cy=y, r=22, fill="#5f8f50")
        el(root, "rect", x=x - 3, y=y + 16, width=6, height=16, fill="#6b4e33")
    return root


def compass_rose() -> ET.Element:
    root = scene("compass-rose", "Finding your way | 找到方向",
                 "A brass compass rests on an unfolded parchment map with faint hills, a river, and a dotted route. | "
                 "一个黄铜指南针放在展开的羊皮纸地图上，地图上有淡淡的山丘、一条河和一条虚线路线。", "#e9e2d0")
    el(root, "path", d="M90 70 L710 50 L730 400 L70 410 Z", fill="#f2e6c8")
    el(root, "path", d="M300 60 L310 405 M520 54 L530 402", fill="none", stroke="#e0d0aa", stroke_width=3)
    el(root, "path", d="M110 300 C 200 260, 260 320, 360 280 C 460 240, 560 300, 700 250", fill="none", stroke="#9cc3cc", stroke_width=8, stroke_linecap="round")
    for x, y in [(160, 150), (210, 130), (620, 140), (660, 160)]:
        el(root, "path", d=f"M{x - 30} {y + 20} L{x} {y - 14} L{x + 30} {y + 20}", fill="none", stroke="#b8a888", stroke_width=4, stroke_linejoin="round")
    el(root, "path", d="M140 360 C 240 330, 320 220, 420 200 C 520 180, 580 110, 650 100", fill="none", stroke="#a35d3c", stroke_width=4, stroke_dasharray="10 10", stroke_linecap="round")
    el(root, "circle", cx=650, cy=100, r=9, fill="#a35d3c")
    cx, cy = 420, 230
    el(root, "circle", cx=cx, cy=cy, r=96, fill="#c99436")
    el(root, "circle", cx=cx, cy=cy, r=82, fill="#f7f1df")
    for k in range(16):
        a = math.radians(k * 22.5)
        r1 = 66 if k % 4 else 58
        el(root, "line", x1=f"{cx + r1 * math.sin(a):.1f}", y1=f"{cy - r1 * math.cos(a):.1f}", x2=f"{cx + 76 * math.sin(a):.1f}", y2=f"{cy - 76 * math.cos(a):.1f}", stroke="#b8a888", stroke_width=2)
    el(root, "path", d=f"M{cx} {cy - 64} L{cx + 12} {cy} L{cx} {cy + 64} L{cx - 12} {cy} Z", fill="#7a8a96")
    el(root, "path", d=f"M{cx} {cy - 64} L{cx + 12} {cy} L{cx - 12} {cy} Z", fill="#c96f4a")
    el(root, "path", d=f"M{cx - 64} {cy} L{cx} {cy - 10} L{cx + 64} {cy} L{cx} {cy + 10} Z", fill="#b8b2a6", fill_opacity=0.7)
    el(root, "circle", cx=cx, cy=cy, r=7, fill="#6b4e33")
    el(root, "circle", cx=cx, cy=cy - 100, r=10, fill="#c99436")
    return root


def evidence_kinds() -> ET.Element:
    root = scene("evidence-kinds", "Different kinds of evidence | 不同种类的旁证",
                 "On a cloth, a clay jar, a coin, an inscribed stone, and a scroll fragment lie side by side under a large magnifying glass. | "
                 "一块布上并排放着陶罐、钱币、刻字的石块和一片书卷残片，上方有一个大放大镜。", "#e6ebe6")
    el(root, "path", d="M40 260 L760 260 L790 420 L10 420 Z", fill="#c9b9a0")
    el(root, "path", d="M40 260 L760 260", stroke="#b0a088", stroke_width=4)
    el(root, "path", d="M110 350 C 96 300, 110 250, 140 236 L180 236 C 210 250, 224 300, 210 350 Z", fill="#c06a3c")
    el(root, "rect", x=134, y=224, width=52, height=14, rx=4, fill="#a35a33")
    el(root, "line", x1=116, y1=290, x2=204, y2=290, stroke="#a35a33", stroke_width=3)
    el(root, "circle", cx=300, cy=330, r=30, fill="#d8b46a")
    el(root, "circle", cx=300, cy=330, r=20, fill="none", stroke="#a8823e", stroke_width=3)
    el(root, "path", d="M292 322 L308 338 M308 322 L292 338", stroke="#a8823e", stroke_width=3)
    el(root, "path", d="M390 360 L400 268 L520 262 L530 356 Z", fill="#a9a39a")
    for k in range(4):
        y = 286 + k * 18
        el(root, "line", x1=410, y1=y, x2=512, y2=y - 2, stroke="#7f7a71", stroke_width=3, stroke_dasharray="8 6")
    el(root, "path", d="M580 290 L690 280 L700 300 L688 330 L700 360 L590 366 L600 336 Z", fill="#e9d9b4")
    for k in range(3):
        y = 304 + k * 16
        el(root, "line", x1=604, y1=y, x2=678, y2=y - 3, stroke="#cdb88c", stroke_width=2)
    el(root, "circle", cx=440, cy=150, r=78, fill="#dce9ee", fill_opacity=0.55, stroke="#6b4e33", stroke_width=12)
    el(root, "line", x1=496, y1=206, x2=580, y2=250, stroke="#6b4e33", stroke_width=16, stroke_linecap="round")
    el(root, "path", d="M400 112 C 412 100, 430 96, 446 98", fill="none", stroke="#ffffff", stroke_width=5, stroke_linecap="round", stroke_opacity=0.8)
    return root


def unfolded_map() -> ET.Element:
    root = scene("unfolded-map", "The whole route on one sheet | 一张纸上的全程",
                 "A long folded map opens across a table, its panels marked with small icons for a tent, a crown, a temple, and a cross along one continuous line. | "
                 "一张折叠的长地图在桌上展开，各个折页上有帐篷、王冠、圣殿和十字架等小图标，由一条连续的线连在一起。", "#3f4a5a")
    el(root, "path", d="M0 300 L800 300 L800 450 L0 450 Z", fill="#6b4e33")
    panels = [(70, 120, "#f2e6c8"), (240, 132, "#ebdcb8"), (410, 120, "#f2e6c8"), (580, 132, "#ebdcb8")]
    for x, y, color in panels:
        el(root, "path", d=f"M{x} {y} L{x + 170} {y + (12 if y == 120 else -12)} L{x + 170} {y + 230 + (12 if y == 120 else -12)} L{x} {y + 230} Z", fill=color)
    el(root, "path", d="M100 300 C 180 240, 240 280, 320 230 C 400 180, 460 260, 540 220 C 620 180, 680 210, 720 170", fill="none", stroke="#a35d3c", stroke_width=5, stroke_linecap="round")
    el(root, "path", d="M140 250 L160 214 L180 250 Z", fill="#8e6644")
    el(root, "path", d="M300 196 L306 176 L316 190 L326 172 L336 190 L346 176 L352 196 Z", fill="#d9a441")
    el(root, "rect", x=476, y=178, width=40, height=30, fill="#c9a86a")
    el(root, "rect", x=488, y=190, width=16, height=18, fill="#8e6644")
    el(root, "rect", x=470, y=170, width=52, height=10, fill="#a8823e")
    el(root, "rect", x=672, y=116, width=8, height=44, fill="#7a5537")
    el(root, "rect", x=660, y=128, width=32, height=8, fill="#7a5537")
    for x, y in [(100, 300), (320, 230), (540, 220), (720, 170)]:
        el(root, "circle", cx=x, cy=y, r=8, fill="#a35d3c")
    return root


def winding_path() -> ET.Element:
    root = scene("winding-path", "A long road with markers | 有路标的长路",
                 "A path winds from the foreground into distant hills, with small colored flags marking stages along the way. | "
                 "一条小路从近处蜿蜒伸向远方的山丘，沿途插着几面小彩旗，标出路上的各个阶段。", "#e8eef2")
    el(root, "path", d="M0 210 L120 150 L240 190 L380 120 L520 180 L660 130 L800 170 L800 260 L0 260 Z", fill="#b9c7cf")
    el(root, "path", d="M0 230 C 260 210, 540 240, 800 220 L800 450 L0 450 Z", fill="#9cbf7a")
    el(root, "path", d="M0 320 C 260 290, 540 330, 800 300 L800 450 L0 450 Z", fill="#8ab06a")
    el(root, "path", d="M300 450 C 260 400, 560 380, 520 330 C 490 292, 300 300, 330 262 C 352 236, 470 236, 480 222 L496 224 C 486 246, 372 246, 354 266 C 330 296, 524 300, 552 334 C 590 384, 320 404, 380 450 Z", fill="#e3d4b0")
    for x, y, color, sc in [(560, 360, "#c96f4a", 1.0), (318, 290, "#d9a441", 0.8), (470, 240, "#4f7d6a", 0.6), (494, 214, "#3f6f8f", 0.45)]:
        el(root, "line", x1=x, y1=y, x2=x, y2=y - 60 * sc, stroke="#6b4e33", stroke_width=4 * sc)
        el(root, "path", d=f"M{x} {y - 60 * sc} L{x + 34 * sc} {y - 50 * sc} L{x} {y - 40 * sc} Z", fill=color)
    return root


def reading_generations() -> ET.Element:
    root = scene("reading-generations", "Read by every generation | 代代相读",
                 "Three seated readers of different ages, each holding an open book, sit in a row beneath a warm lamp. | "
                 "三位年龄不同的读者坐成一排，每人手里捧着一本打开的书，上方有一盏温暖的灯。", "#f1e7d6")
    el(root, "circle", cx=400, cy=92, r=110, fill="#f2c56b", fill_opacity=0.14)
    el(root, "line", x1=400, y1=0, x2=400, y2=60, stroke="#6b4e33", stroke_width=3)
    el(root, "path", d="M370 60 L430 60 L414 86 L386 86 Z", fill="#8e6644")
    el(root, "circle", cx=400, cy=92, r=10, fill="#fbe08a")
    el(root, "path", d="M0 360 L800 360 L800 450 L0 450 Z", fill="#c9b48a")
    for x, robe, sc in [(220, "#7a5f8f", 1.0), (400, "#4f7d6a", 0.85), (580, "#a35d3c", 0.7)]:
        el(root, "rect", x=x - 50 * sc, y=360 - 60 * sc, width=100 * sc, height=60 * sc, rx=6, fill="#8e6644")
        el(root, "path", d=f"M{x - 34 * sc} {360 - 60 * sc} L{x - 26 * sc} {360 - 150 * sc} C {x - 20 * sc} {360 - 162 * sc}, {x + 20 * sc} {360 - 162 * sc}, {x + 26 * sc} {360 - 150 * sc} L{x + 34 * sc} {360 - 60 * sc} Z", fill=robe)
        el(root, "circle", cx=x, cy=360 - 182 * sc, r=22 * sc, fill="#c99a6e")
        bx, by = x, 360 - 104 * sc
        el(root, "path", d=f"M{bx} {by} L{bx - 34 * sc} {by - 10 * sc} L{bx - 34 * sc} {by + 20 * sc} L{bx} {by + 28 * sc} Z", fill="#f2e6c8")
        el(root, "path", d=f"M{bx} {by} L{bx + 34 * sc} {by - 10 * sc} L{bx + 34 * sc} {by + 20 * sc} L{bx} {by + 28 * sc} Z", fill="#e9d9b4")
    return root


def sinai_cloud() -> ET.Element:
    root = scene("sinai-cloud", "The mountain of the covenant | 立约的山",
                 "A rocky mountain rises from the desert, its top wrapped in dark cloud with flashes of lightning, while small tents stand at its foot. | "
                 "一座石山从旷野中升起，山顶被乌云包围，闪电划过，山脚下立着一些小帐篷。", "#c9cdd2")
    el(root, "path", d="M150 360 L300 170 L360 210 L420 120 L500 200 L560 170 L700 360 Z", fill="#8a6a55")
    el(root, "path", d="M420 120 L500 200 L460 200 L430 160 Z", fill="#a3826a")
    el(root, "path", d="M300 170 L360 210 L330 214 Z", fill="#a3826a")
    for cx, cy, r in [(330, 120, 60), (400, 96, 74), (480, 112, 64), (540, 132, 46), (270, 140, 40), (420, 140, 60)]:
        el(root, "circle", cx=cx, cy=cy, r=r, fill="#4a4f5a")
    el(root, "path", d="M240 150 C 300 168, 520 170, 580 150", fill="none", stroke="#5c6270", stroke_width=6, stroke_linecap="round")
    el(root, "path", d="M388 150 L372 196 L392 192 L378 236", fill="none", stroke="#fbe08a", stroke_width=5, stroke_linejoin="round", stroke_linecap="round")
    el(root, "path", d="M500 156 L490 182 L504 180 L494 206", fill="none", stroke="#fbe08a", stroke_width=4, stroke_linejoin="round", stroke_linecap="round")
    ground(root, 350, "#d8b98a", 6, 600)
    for x, y, color in [(120, 400, "#c96f4a"), (200, 386, "#e9d9b4"), (290, 404, "#a35d3c"), (520, 398, "#e9d9b4"), (610, 388, "#c96f4a"), (690, 404, "#a35d3c")]:
        el(root, "path", d=f"M{x - 30} {y} L{x} {y - 34} L{x + 30} {y} Z", fill=color)
        el(root, "path", d=f"M{x - 6} {y} L{x} {y - 16} L{x + 6} {y} Z", fill="#5a3e2a")
    return root


def daily_bread() -> ET.Element:
    root = scene("daily-bread", "Bread for today | 今日的饮食",
                 "Morning light falls through a small window onto a wooden table, where a round loaf of bread sits beside a cup of water. | "
                 "晨光从一扇小窗照进来，落在木桌上；桌上放着一个圆面包，旁边有一杯水。", "#3f3530")
    el(root, "rect", x=520, y=60, width=140, height=150, rx=6, fill="#f3e2b8")
    el(root, "line", x1=590, y1=60, x2=590, y2=210, stroke="#3f3530", stroke_width=8)
    el(root, "line", x1=520, y1=135, x2=660, y2=135, stroke="#3f3530", stroke_width=8)
    el(root, "path", d="M520 210 L660 210 L580 300 L270 300 Z", fill="#f3e2b8", fill_opacity=0.16)
    el(root, "path", d="M0 330 L800 330 L800 450 L0 450 Z", fill="#2c2420")
    el(root, "rect", x=120, y=300, width=560, height=26, rx=4, fill="#8e6644")
    for x in (150, 630):
        el(root, "rect", x=x, y=324, width=20, height=90, fill="#6b4e33")
    el(root, "path", d="M250 300 C 250 236, 410 236, 410 300 Z", fill="#d9a35c")
    for x in (290, 330, 370):
        el(root, "path", d=f"M{x - 12} 262 C {x - 4} 254, {x + 4} 254, {x + 12} 262", fill="none", stroke="#b5793f", stroke_width=4, stroke_linecap="round")
    el(root, "path", d="M470 300 L476 250 L516 250 L522 300 Z", fill="#c8d8de")
    el(root, "path", d="M474 268 L518 268 L521 298 L471 298 Z", fill="#9cc3cc")
    return root


def salt_light() -> ET.Element:
    root = scene("salt-light", "Salt and light | 盐和光",
                 "On a wooden shelf, a small clay oil lamp burns on a tall stand, lighting the room, beside an open bowl heaped with white salt. | "
                 "木架上，一盏小陶油灯放在高高的灯台上燃着，照亮屋子；旁边是一只盛满白盐的敞口碗。", "#33302e")
    el(root, "circle", cx=402, cy=150, r=170, fill="#f2c56b", fill_opacity=0.10)
    el(root, "path", d="M0 330 L800 330 L800 450 L0 450 Z", fill="#26221f")
    el(root, "rect", x=140, y=310, width=520, height=22, rx=4, fill="#8e6644")
    el(root, "path", d="M330 310 L390 310 L378 296 L342 296 Z", fill="#7a5537")
    el(root, "rect", x=352, y=196, width=16, height=100, fill="#8e6644")
    el(root, "path", d="M324 196 L396 196 L386 184 L334 184 Z", fill="#7a5537")
    el(root, "path", d="M330 184 C 330 160, 380 160, 384 172 L404 166 L398 180 C 392 186, 340 188, 330 184 Z", fill="#c06a3c")
    el(root, "circle", cx=352, cy=168, r=5, fill="#8f4a28")
    el(root, "path", d="M402 166 C 392 146, 404 132, 400 116 C 416 132, 418 152, 402 166 Z", fill="#ef8a3a")
    el(root, "path", d="M402 162 C 397 150, 404 142, 402 132 C 410 142, 411 154, 402 162 Z", fill="#fbe08a")
    el(root, "path", d="M478 294 C 490 272, 520 264, 525 264 C 532 264, 560 272, 572 294 Z", fill="#f4f1ea")
    el(root, "path", d="M462 292 L588 292 C 584 320, 466 320, 462 292 Z", fill="#6f8ea0")
    el(root, "path", d="M462 292 L588 292", stroke="#58778a", stroke_width=4)
    for x, y in [(500, 284), (520, 276), (545, 282)]:
        el(root, "circle", cx=x, cy=y, r=2.5, fill="#dcd6ca")
    return root


def voices_together() -> ET.Element:
    root = scene("voices-together", "Saying it together | 一同宣认",
                 "A row of people of different ages and colors stands side by side beneath three tall arched windows filled with warm light. | "
                 "一排年龄不同、衣着各异的人并肩站在三扇高高的拱形窗下，窗中透进温暖的光。", "#e8e1d4")
    for x in (190, 400, 610):
        el(root, "path", d=f"M{x - 60} 280 L{x - 60} 120 C {x - 60} 40, {x + 60} 40, {x + 60} 120 L{x + 60} 280 Z", fill="#f6e3b0")
        el(root, "line", x1=x, y1=60, x2=x, y2=280, stroke="#e8e1d4", stroke_width=6)
        el(root, "line", x1=x - 60, y1=160, x2=x + 60, y2=160, stroke="#e8e1d4", stroke_width=6)
    el(root, "path", d="M0 300 L800 300 L800 450 L0 450 Z", fill="#c9b48a")
    el(root, "path", d="M130 300 L670 300 L760 450 L40 450 Z", fill="#f6e3b0", fill_opacity=0.25)
    people = [(110, "#7a5f8f", "#c99a6e", 1.0), (190, "#4f7d6a", "#b8875c", 0.9), (265, "#a35d3c", "#8e6a46", 1.05), (345, "#3f6f8f", "#c99a6e", 0.75),
              (420, "#d9a441", "#b8875c", 1.0), (500, "#8e3b46", "#c99a6e", 0.95), (580, "#5f8f50", "#8e6a46", 0.8), (660, "#c96f4a", "#b8875c", 1.0)]
    for x, robe, skin, sc in people:
        person(root, x, 380, robe, skin, 1.4 * sc)
    return root


RESEARCH_ARTWORKS: dict[str, Callable[[], ET.Element]] = {
    "papyrus-codex.svg": papyrus_codex,
    "story-procession.svg": story_procession,
    "parchment-map.svg": parchment_map,
    "lost-sheep.svg": lost_sheep,
    "lamp-path.svg": lamp_path,
    "incense-rising.svg": incense_rising,
    "notebook-pen.svg": notebook_pen,
    "study-desk.svg": study_desk,
    "lyre-dawn.svg": lyre_dawn,
    "booths-harvest.svg": booths_harvest,
    "loaves-fish.svg": loaves_fish,
    "scribe-copying.svg": scribe_copying,
    "burning-bush.svg": burning_bush,
    "temple-courts.svg": temple_courts,
    "dig-layers.svg": dig_layers,
    "seven-lamps.svg": seven_lamps,
    "five-scrolls.svg": five_scrolls,
    "split-crown.svg": split_crown,
    "roman-road.svg": roman_road,
    "scroll-jars.svg": scroll_jars,
    "four-clocks.svg": four_clocks,
    "eleven-threads.svg": eleven_threads,
    "stepping-stones.svg": stepping_stones,
    "signpost.svg": signpost,
    "compass-rose.svg": compass_rose,
    "evidence-kinds.svg": evidence_kinds,
    "unfolded-map.svg": unfolded_map,
    "winding-path.svg": winding_path,
    "reading-generations.svg": reading_generations,
    "sinai-cloud.svg": sinai_cloud,
    "daily-bread.svg": daily_bread,
    "salt-light.svg": salt_light,
    "voices-together.svg": voices_together,
}


ARTWORKS: dict[str, Callable[[], ET.Element]] = {
    "jacob-ladder.svg": jacob_ladder,
    "lamb-altar.svg": lamb_altar,
    "stone-tablets.svg": stone_tablets,
    "jericho-walls.svg": jericho_walls,
    "anointing.svg": anointing,
    "golden-calf.svg": golden_calf,
    "burning-coal.svg": burning_coal,
    "exile-road.svg": exile_road,
    "water-tunnel.svg": water_tunnel,
    "found-scroll.svg": found_scroll,
    "ruined-city.svg": ruined_city,
    "potter-wheel.svg": potter_wheel,
    "dry-bones.svg": dry_bones,
    "royal-scepter.svg": royal_scepter,
    "sunrise-field.svg": sunrise_field,
    "whirlwind.svg": whirlwind,
    "seasons-tree.svg": seasons_tree,
    "jordan-dove.svg": jordan_dove,
    "galilee-boat.svg": galilee_boat,
    "sower.svg": sower,
    "palm-road.svg": palm_road,
    "chariot-road.svg": chariot_road,
    "table-fellowship.svg": table_fellowship,
    "jars-of-clay.svg": jars_of_clay,
    "anchor-hope.svg": anchor_hope,
    "lamp-light.svg": lamp_light,
    "joseph-granary.svg": joseph_granary,
    "sea-crossing.svg": sea_crossing,
    "wilderness-camp.svg": wilderness_camp,
    "barley-harvest.svg": barley_harvest,
    "david-harp.svg": david_harp,
    "carmel-altar.svg": carmel_altar,
    "lions-den.svg": lions_den,
    "bread-cup.svg": bread_cup,
    "empty-tomb.svg": empty_tomb,
    "pentecost.svg": pentecost,
    "paul-ship.svg": paul_ship,
    "bible-library.svg": library,
    "jonah.svg": jonah,
    "shepherd.svg": shepherd,
    "letter.svg": letter,
    "rebuilding.svg": rebuilding,
    "open-bible.svg": open_book,
    **NOTE_ARTWORKS,
    **GUIDE_ARTWORKS,
    **TIMELINE_ARTWORKS,
    **RESEARCH_ARTWORKS,
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
