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
        el(root, "line", x1=600, y1=230, x2=600 + 420 * math.cos(angle) * -1, y2=230 + 420 * math.sin(angle),
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
