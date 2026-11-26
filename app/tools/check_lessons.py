"""Check every lesson: plain-writing patterns, bilingual pairing, scripture wording, body quotes.

    python3 app/tools/check_lessons.py                 # all lessons
    python3 app/tools/check_lessons.py FILE...         # some lessons
    python3 app/tools/check_lessons.py --update-lock   # rewrite scripture-lock.json (needs .sources/)

Exit status is 1 when a problem is found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bible  # noqa: E402

ROOT = Path(__file__).resolve().parents[1] / "src" / "content" / "lessons"

BAD = [
    (r"不是[^。；！？\n]{0,40}而是", "contrast 不是…而是"),
    (r"不只是|不仅仅?是|不单是|不光是", "不只是"),
    (r"更是", "更是"),
    (r"——", "zh dash"),
    (r"—", "em dash"),
    (r"深刻|震撼|极其|至关重要|令人惊叹|无比|本质上|真正的", "intensifier"),
    (r"(?i)\bnot (just|only|merely|simply)\b", "not just"),
    (r"(?i)\bnot [^.;\n]{0,50}\bbut (rather )?\b", "not X but Y"),
    (r"(?i)\b(profound|crucial|deeply|tapestry|delve|unpack|at its core|game-changer)\b|(?<!-)\bpowerful\b|\btruly\b(?! (God|human))", "en intensifier"),
    (r"(?i)\bhonest(ly)?\b", "honest tic"),
    (r"核心", "核心"),
]

ZH_BOOK = {
    "创": "Genesis", "出": "Exodus", "利": "Leviticus", "民": "Numbers", "申": "Deuteronomy",
    "书": "Joshua", "士": "Judges", "得": "Ruth", "撒上": "1 Samuel", "撒下": "2 Samuel",
    "王上": "1 Kings", "王下": "2 Kings", "代上": "1 Chronicles", "代下": "2 Chronicles",
    "拉": "Ezra", "尼": "Nehemiah", "斯": "Esther", "伯": "Job", "诗": "Psalms", "箴": "Proverbs",
    "传": "Ecclesiastes", "歌": "Song of Solomon", "赛": "Isaiah", "耶": "Jeremiah",
    "哀": "Lamentations", "结": "Ezekiel", "但": "Daniel", "何": "Hosea", "珥": "Joel",
    "摩": "Amos", "俄": "Obadiah", "拿": "Jonah", "弥": "Micah", "鸿": "Nahum", "哈": "Habakkuk",
    "番": "Zephaniah", "该": "Haggai", "亚": "Zechariah", "玛": "Malachi", "太": "Matthew",
    "可": "Mark", "路": "Luke", "约": "John", "徒": "Acts", "罗": "Romans", "林前": "1 Corinthians",
    "林后": "2 Corinthians", "加": "Galatians", "弗": "Ephesians", "腓": "Philippians",
    "西": "Colossians", "帖前": "1 Thessalonians", "帖后": "2 Thessalonians", "提前": "1 Timothy",
    "提后": "2 Timothy", "多": "Titus", "门": "Philemon", "来": "Hebrews", "雅": "James",
    "彼前": "1 Peter", "彼后": "2 Peter", "约壹": "1 John", "约贰": "2 John", "约叁": "3 John",
    "犹": "Jude", "启": "Revelation",
    "创世记": "Genesis", "出埃及记": "Exodus", "利未记": "Leviticus", "民数记": "Numbers",
    "申命记": "Deuteronomy", "诗篇": "Psalms", "箴言": "Proverbs", "以赛亚书": "Isaiah",
    "耶利米书": "Jeremiah", "但以理书": "Daniel", "弥迦书": "Micah", "马太福音": "Matthew",
    "马可福音": "Mark", "路加福音": "Luke", "约翰福音": "John", "使徒行传": "Acts",
    "罗马书": "Romans", "哥林多前书": "1 Corinthians", "哥林多后书": "2 Corinthians",
    "加拉太书": "Galatians", "以弗所书": "Ephesians", "腓立比书": "Philippians",
    "歌罗西书": "Colossians", "希伯来书": "Hebrews", "雅各书": "James", "彼得前书": "1 Peter",
    "约翰一书": "1 John", "启示录": "Revelation",
}


def words(t: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", t.lower().replace("’", "'"))


def cjk(t: str) -> str:
    return re.sub(r"[^一-鿿]", "", t)


def zhcore(t: str) -> str:
    return cjk(re.sub(r"（[^）]*）", "", t))


def contained(part: str, whole: str) -> bool:
    pos = 0
    for seg in [x for x in re.split(r"……|…|\.\.\.", part) if x.strip()]:
        i = whole.find(seg, pos)
        if i < 0:
            return False
        pos = i + len(seg)
    return True


def split(path: Path):
    s = path.read_text(encoding="utf-8")
    if not s.startswith("---\n"):
        raise ValueError("no front matter")
    end = s.index("\n---\n", 4)
    return s, yaml.safe_load(s[4:end]), s[4:end], s[end + 5:]


def check_scripture(fm: dict) -> list[str]:
    probs = []
    for sc in fm.get("scripture", []) or []:
        t = sc.get("text")
        try:
            vs = bible.expand(sc["refEn"])
            en = " ".join(bible.web(n, c, v) for n, c, v in vs)
            zh = bible.zh_quotes("".join(bible.chi(n, c, v) for n, c, v in vs))
        except bible.NotInLock as e:
            probs.append(f"not in scripture-lock.json: {e.args[0]} (run fetch_sources.py, then --update-lock)")
            continue
        except Exception as e:  # noqa: BLE001
            probs.append(f"ref parse {sc.get('refEn')}: {e}")
            continue
        if not t:
            continue
        he, we = " ".join(words(t.get("en", ""))), " ".join(words(en))
        hz, wz = zhcore(t.get("zh", "")), zhcore(zh)
        if he != we:
            probs.append(f"EN mismatch {sc['refEn']}\n   have: {t.get('en')}\n   WEB:  {en}")
        if hz != wz:
            probs.append(f"ZH mismatch {sc['ref']}\n   have: {t.get('zh')}\n   1919: {zh}")
    return probs


def check_style(fm: dict, body: str) -> list[str]:
    probs = []
    fm2 = dict(fm)
    fm2.pop("scripture", None)
    fm2.pop("sources", None)
    prose = yaml.safe_dump(fm2, allow_unicode=True, width=10000) + body
    prose = re.sub(r"“[^”]*”", "“”", prose)  # quoted words are not our prose
    for pat, label in BAD:
        for m in re.finditer(pat, prose):
            a0 = max(0, m.start() - 20)
            probs.append(f"style[{label}]: …{prose[a0:m.end() + 25]}…".replace("\n", " "))
    return probs


def check_pairing(fm: dict, body: str) -> list[str]:
    probs = []
    lines = body.split("\n")
    for i, ln in enumerate(lines):
        st = ln.strip()
        if st.startswith("## ") and " | " not in st:
            probs.append(f"heading without ' | ': {st}")
        if st.endswith("<br>"):
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if not nxt or not re.search(r"[A-Za-z]{4,}", nxt):
                probs.append(f"zh line not followed by English: {st[:40]}")
        elif st and not st.startswith(("#", "|", "<", "---")) and len(re.findall(r"[一-鿿]", st)) > 6 \
                and not re.search(r"[A-Za-z]{4,}.*[A-Za-z]{4,}", st):
            probs.append(f"zh line missing <br>: {st[:40]}")
    for x in fm.get("reflect", []) or []:
        if not x.get("en"):
            probs.append("reflect missing en")
    for q in fm.get("check", []) or []:
        if not q["q"].get("en") or any(not o.get("en") for o in q["options"]):
            probs.append("check missing en")
        if q["answer"] >= len(q["options"]):
            probs.append("answer out of range")
        if q.get("explain") and not q["explain"].get("en"):
            probs.append("explain missing en")
    for src in fm.get("sources", []) or []:
        if not src.get("label", {}).get("en") or not str(src.get("url", "")).startswith("https://"):
            probs.append(f"source needs label.en and an https url: {src}")
    return probs


def _verses(book: str, spec: str, lang: str, keep_notes: bool = False) -> str:
    vs = bible.expand(f"{book} {spec}")
    if lang == "zh":
        t = "".join(bible.chi(n, c, v) for n, c, v in vs)
        return cjk(t) if keep_notes else zhcore(t)
    return " ".join(words(" ".join(bible.web(n, c, v) for n, c, v in vs)))


def check_quotes(raw_fm: str, body: str) -> list[str]:
    """“…”（创 12:1） and “…” (Genesis 12:1) in prose must be wording from the cited verses."""
    out = []
    fm = re.sub(r"^scripture:\n.*?^(?=\w)", "", raw_fm + "\n_end:\n", flags=re.S | re.M)
    text = fm + body
    for m in re.finditer(r"“([^”]{4,})”[^“”（\n]{0,6}（([^（）]+?)）", text):
        q, ref = m.group(1), m.group(2).strip()
        if re.match(r"^[A-Za-z]", ref):
            continue  # a gloss such as （Incarnation，约翰福音 1:14）, not a quotation
        rm = re.match(r"^(\D+?)\s*(\d+[:：]\d+(?:[-–]\d+)?(?:[，,]\s*\d+(?:[-–]\d+)?)*)$", ref)
        if not rm:
            continue
        book = ZH_BOOK.get(rm.group(1).strip())
        spec = rm.group(2).replace("：", ":").replace("，", ",").replace("–", "-")
        if not book:
            out.append(f"quote: unknown book in （{ref}）")
            continue
        try:
            texts = [_verses(book, spec, "zh"), _verses(book, spec, "zh", keep_notes=True)]
        except bible.NotInLock as e:
            out.append(f"not in scripture-lock.json: {e.args[0]} (run fetch_sources.py, then --update-lock)")
            continue
        except Exception:  # noqa: BLE001
            out.append(f"quote: cannot read （{ref}）")
            continue
        segs = [cjk(x) for x in re.split(r"……|…", q) if x.strip()]
        if not any(all(s in t for s in segs) for t in texts):
            out.append(f"quote not in {ref}: “{q}”")
    pat = (r"“([^”]{8,})”[^“”(\n]{0,8}\(([1-3]?\s?[A-Z][a-z]+(?: of [A-Z][a-z]+)?)\s+"
           r"(\d+:\d+(?:[-–]\d+)?(?:,\s*\d+(?:[-–]\d+)?)*)\)")
    for m in re.finditer(pat, text):
        q, book, spec = m.group(1), m.group(2), m.group(3).replace("–", "-")
        try:
            vt = _verses(book, spec, "en")
        except bible.NotInLock as e:
            out.append(f"not in scripture-lock.json: {e.args[0]} (run fetch_sources.py, then --update-lock)")
            continue
        except Exception:  # noqa: BLE001
            continue  # not a Bible reference
        segs = [" ".join(words(x)) for x in re.split(r"\.\.\.|…", q)]
        if not all(x in vt for x in segs if x):
            out.append(f"quote not in {book} {spec}: “{q}”")
    return out


def check(path: Path) -> list[str]:
    _, fm, raw_fm, body = split(path)
    return check_scripture(fm) + check_style(fm, body) + check_pairing(fm, body) + check_quotes(raw_fm, body)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    update = "--update-lock" in sys.argv
    if update and not bible.using_sources():
        print("--update-lock needs the sources: run python3 app/tools/fetch_sources.py first")
        return 2
    files = [Path(a) for a in args] or sorted(ROOT.glob("*/*.md"))
    total = 0
    for f in files:
        for p in check(f):
            total += 1
            print(f"{f.parent.name}/{f.name} | {p}")
    mode = "sources" if bible.using_sources() else "lock"
    print(f"lessons: {len(files)}  problems: {total}  (scripture from {mode})")
    if update and not args:
        print("lock verses:", bible.write_lock())
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
