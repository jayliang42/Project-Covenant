"""Rewrite the scripture `text` blocks of the given lessons from the source texts.

    python3 app/tools/fill_scripture.py app/src/content/lessons/new/13-example.md

Write each entry as two lines (`- ref: 约翰福音 3:16` and `refEn: John 3:16`); the tool
adds or replaces `text`. Needs .sources/ (run fetch_sources.py once).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bible  # noqa: E402


def zh_text(vs) -> str:
    t = "".join(bible.chi(n, c, v) for n, c, v in vs)
    t = re.sub(r"（[^）]*）", "", t)
    t = bible.zh_quotes(t).replace("•", "·")
    if t.count("（") != t.count("）"):
        t = t.replace("（", "").replace("）", "")
    return t.strip()


def en_text(vs) -> str:
    t = re.sub(r"\s+", " ", " ".join(bible.web(n, c, v) for n, c, v in vs)).strip()
    if t.startswith("(") and t.endswith(")"):
        t = t[1:-1].strip()
        t = t[0].upper() + t[1:] + "."
    return t


def balance(t: str, pairs=(("“", "”"), ("‘", "’"))) -> str:
    for o, c in pairs:
        while t.count(o) > t.count(c):
            t = t[1:] if t.startswith(o) else t + c
        while t.count(c) > t.count(o):
            t = t[:-1] if t.endswith(c) else o + t
    return t


def block(ref: str, refen: str, indent: str = "  ") -> str:
    vs = bible.expand(refen)
    z, e = balance(zh_text(vs)), balance(en_text(vs), pairs=(("“", "”"),))
    if not z or not e:
        raise ValueError(f"empty text for {refen}")
    i = indent
    return (f"{i}- ref: {ref}\n{i}  refEn: {refen}\n{i}  text:\n"
            f"{i}    zh: {json.dumps(z, ensure_ascii=False)}\n{i}    en: {json.dumps(e, ensure_ascii=False)}\n")


def rewrite(path: str) -> None:
    s = Path(path).read_text(encoding="utf-8")
    m = re.search(r"^scripture:\n(.*?)^(?=\w)", s, re.S | re.M)
    if not m:
        raise ValueError(f"{path}: no scripture block")
    items = re.findall(r'^  - (?:\{ )?ref: "?([^"\n,]+?)"?,?\s*(?:\n    )?refEn: "?([^"\n}]+?)"?\s*\}?\s*$', m.group(1), re.M)
    if not items:
        raise ValueError(f"{path}: no scripture entries")
    out = "scripture:\n" + "".join(block(ref, refen) for ref, refen in items)
    Path(path).write_text(s[:m.start()] + out + s[m.end():], encoding="utf-8")
    print(path.split("lessons/")[-1], [r for _, r in items])


if __name__ == "__main__":
    if not bible.using_sources():
        raise SystemExit("run python3 app/tools/fetch_sources.py first")
    for f in sys.argv[1:]:
        rewrite(f)
