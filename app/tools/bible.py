"""Verse lookup for the lesson checks.

Two back ends:
- sources: the World English Bible JSON and the 1919 Chinese Union text, fetched
  by fetch_sources.py into .sources/ (needs the `opencc` package);
- lock: scripture-lock.json, which holds every verse the lessons cite.

The sources are used when .sources/ exists. Otherwise the lock is used, so the
checks run in CI without any download.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / ".sources"
LOCK_PATH = HERE / "scripture-lock.json"

BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "I Samuel", "II Samuel", "I Kings", "II Kings", "I Chronicles", "II Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
    "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "I Corinthians",
    "II Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "I Thessalonians", "II Thessalonians", "I Timothy", "II Timothy", "Titus", "Philemon",
    "Hebrews", "James", "I Peter", "II Peter", "I John", "II John", "III John", "Jude",
    "Revelation of John",
]
ABBR = {
    "Ps": "Psalms", "Psalm": "Psalms", "Gen": "Genesis", "Exod": "Exodus", "Isa": "Isaiah",
    "Rom": "Romans", "Matt": "Matthew", "Jer": "Jeremiah", "Prov": "Proverbs",
    "Heb": "Hebrews", "Eph": "Ephesians", "Phil": "Philippians", "Col": "Colossians",
    "Gal": "Galatians", "Rev": "Revelation", "Deut": "Deuteronomy",
    "Song of Songs": "Song of Solomon",
}
ROMAN = {"I ": "1", "II ": "2", "III ": "3"}

USED: dict[str, list[str]] = {}
_state: dict[str, object] = {}


class NotInLock(KeyError):
    """A verse is cited that the lock does not hold yet."""


def using_sources() -> bool:
    return (SOURCES / "web" / "json").is_dir() and (SOURCES / "ChiUn.json").is_file()


def _chi_books():
    if "chi" not in _state:
        data = json.loads((SOURCES / "ChiUn.json").read_text(encoding="utf-8"))["books"]
        _state["chi"] = data
        _state["names"] = [b["name"] for b in data]
        from opencc import OpenCC  # only needed with the sources
        _state["cc"] = OpenCC("t2s")
    return _state["chi"], _state["names"], _state["cc"]


def _web_book(name: str):
    key = "web:" + name
    if key not in _state:
        n = name
        for k in ("III ", "II ", "I "):
            if n.startswith(k):
                n = ROMAN[k] + n[len(k):]
                break
        n = n.replace("Revelation of John", "Revelation").lower().replace(" ", "")
        _state[key] = json.loads((SOURCES / "web" / "json" / f"{n}.json").read_text(encoding="utf-8"))
    return _state[key]


def _lock() -> dict[str, list[str]]:
    if "lock" not in _state:
        _state["lock"] = json.loads(LOCK_PATH.read_text(encoding="utf-8"))["verses"] if LOCK_PATH.is_file() else {}
    return _state["lock"]  # type: ignore[return-value]


def _source_web(name: str, ch: int, v: int) -> str:
    parts = [x["value"] for x in _web_book(name)
             if x.get("chapterNumber") == ch and x.get("verseNumber") == v and "value" in x]
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def _source_chi(name: str, ch: int, v: int) -> str:
    books, names, cc = _chi_books()
    book = books[names.index(name)]
    for c in book["chapters"]:
        if c["chapter"] == ch:
            for x in c["verses"]:
                if x["verse"] == v:
                    t = cc.convert(x["text"]).replace("著", "着").replace("甚么", "什么").replace("藉", "借")
                    t = re.sub(r"[A-Za-z]", "", t).replace("倣", "仿")
                    punct = "一-鿿，。；：、！？「」『』（）"
                    return re.sub(rf"(?<=[{punct}]) +| +(?=[{punct}])", "", t).strip()
    return ""


def _pair(name: str, ch: int, v: int) -> list[str]:
    key = f"{name} {ch}:{v}"
    if key not in USED:
        if using_sources():
            USED[key] = [_source_web(name, ch, v), _source_chi(name, ch, v)]
        else:
            lock = _lock()
            if key not in lock:
                raise NotInLock(key)
            USED[key] = lock[key]
    return USED[key]


def web(name: str, ch: int, v: int) -> str:
    return _pair(name, ch, v)[0]


def chi(name: str, ch: int, v: int) -> str:
    return _pair(name, ch, v)[1]


def parse(ref: str):
    m = re.match(r"^(.+?)\s+(\d+):(\d+)(?:-(\d+))?$", ref.strip())
    if not m:
        raise ValueError(f"cannot parse reference: {ref}")
    name, ch, a, b = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4) or m.group(3))
    name = ABBR.get(name, name)
    m2 = re.match(r"^([123]) (.+)$", name)
    if m2:
        name = {"1": "I ", "2": "II ", "3": "III "}[m2.group(1)] + m2.group(2)
    if name == "Revelation":
        name = "Revelation of John"
    if name not in BOOKS:
        raise ValueError(f"unknown book: {name}")
    return name, ch, a, b


def expand(ref: str):
    """'John 1:1, 14' / 'Luke 24:25-27, 44-45' / 'Mark 1:1-3; 2:5' -> [(name, ch, v)]."""
    m = re.match(r"^(.+?)\s+(\d+):(.+)$", ref.strip())
    if not m:
        raise ValueError(f"cannot parse reference: {ref}")
    name, ch, rest = m.group(1), int(m.group(2)), m.group(3)
    name, _, _, _ = parse(f"{name} {ch}:1")
    out = []
    for part in re.split(r"[,;]", rest):
        part = part.strip()
        if ":" in part:
            c2, vv = part.split(":")
            ch = int(c2)
            part = vv
        a, _, b = part.partition("-")
        out += [(name, ch, v) for v in range(int(a), int(b or a) + 1)]
    return out


def zh_quotes(t: str) -> str:
    return t.replace("「", "“").replace("」", "”").replace("『", "‘").replace("』", "’")


def write_lock() -> int:
    verses = {k: USED[k] for k in sorted(USED, key=_sort_key)}
    payload = {
        "note": "Generated by check_lessons.py --update-lock. English: World English Bible. "
                "Chinese: Chinese Union Version (1919), simplified. Both are public domain.",
        "verses": verses,
    }
    LOCK_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(verses)


def _sort_key(key: str):
    name, cv = key.rsplit(" ", 1)
    c, v = cv.split(":")
    return BOOKS.index(name), int(c), int(v)


if __name__ == "__main__":
    import sys
    for ref in sys.argv[1:]:
        vs = expand(ref)
        print("##", ref)
        print("EN:", " ".join(web(n, c, v) for n, c, v in vs))
        print("ZH:", zh_quotes("".join(chi(n, c, v) for n, c, v in vs)))
