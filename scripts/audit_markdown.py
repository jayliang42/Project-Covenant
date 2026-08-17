#!/usr/bin/env python3
"""Audit bilingual titles and local Markdown navigation for Project Covenant."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CHINESE = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")
H1 = re.compile(r"^# (.+)$", re.MULTILINE)
HEADING = re.compile(r"^#{1,6} (.+)$", re.MULTILINE)
ANCHOR = re.compile(r'<a\s+id=["\']([^"\']+)["\']\s*></a>', re.IGNORECASE)
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\n]+)\)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+] |\d+[.)] )")
CODE_FILE_REFERENCE = re.compile(r"`[^`*\n]+\.(?:md|txt|pdf|json)`", re.IGNORECASE)
INDEX_MARKERS = (
    "README.md",
    "INDEX",
    "总索引",
    "路线图",
    "导航",
    "总表",
    "Cheat_Sheet",
    "Summary",
)


def tracked_markdown() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / Path(item) for item in result.stdout.decode("utf-8").split("\0") if item]


def local_target(current: Path, raw_target: str) -> tuple[Path | None, str | None]:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None, None

    fragment = unquote(parsed.fragment) or None
    relative = unquote(parsed.path)
    target_path = (current.parent / relative).resolve() if relative else current
    return target_path, fragment


def index_like(path: Path) -> bool:
    return any(marker in path.name for marker in INDEX_MARKERS)


def main() -> int:
    files = tracked_markdown()
    missing_h1: list[str] = []
    duplicate_anchors: list[str] = []
    broken_links: list[str] = []
    unverified_fragments: list[str] = []
    unlinked_index_items: list[str] = []
    bilingual_body = 0
    h1_total = 0

    for path in files:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        if CHINESE.search(text) and LATIN.search(text):
            bilingual_body += 1

        h1s = H1.findall(text)
        h1_total += len(h1s)
        if h1s and any("|" not in title for title in h1s):
            missing_h1.append(relative)

        anchors = ANCHOR.findall(text)
        seen: set[str] = set()
        for anchor in anchors:
            if anchor in seen:
                duplicate_anchors.append(f"{relative}#{anchor}")
            seen.add(anchor)

        for label, raw_target in LINK.findall(text):
            target_path, fragment = local_target(path, raw_target)
            if target_path is None:
                continue
            if not target_path.is_file():
                broken_links.append(f"{relative}: [{label}]({raw_target.strip()})")
                continue
            if fragment:
                target_text = target_path.read_text(encoding="utf-8")
                target_anchors = set(ANCHOR.findall(target_text))
                if fragment not in target_anchors:
                    unverified_fragments.append(
                        f"{relative}: [{label}] -> {target_path.relative_to(ROOT)}#{fragment}"
                    )

        if index_like(path):
            for line_number, line in enumerate(text.splitlines(), start=1):
                # Only flag list entries that appear to name a concrete file.
                # Explanatory bullets and checklists are not index rows.
                if (
                    LIST_ITEM.match(line)
                    and "[" not in line
                    and CODE_FILE_REFERENCE.search(line)
                ):
                    unlinked_index_items.append(f"{relative}:{line_number}: {line.strip()}")

    print(f"markdown_files={len(files)}")
    print(f"bilingual_body_files={bilingual_body}/{len(files)}")
    print(f"bilingual_h1={h1_total - len(missing_h1)}/{h1_total}")
    print(f"broken_local_links={len(broken_links)}")
    print(f"duplicate_explicit_anchors={len(duplicate_anchors)}")
    print(f"fragments_needing_github_slug_review={len(unverified_fragments)}")
    print(f"unlinked_file_items_in_indexes={len(unlinked_index_items)}")

    for heading, entries in (
        ("missing_h1", missing_h1),
        ("broken_links", broken_links),
        ("duplicate_explicit_anchors", duplicate_anchors),
        ("fragments_needing_github_slug_review", unverified_fragments),
        ("unlinked_file_items_in_indexes", unlinked_index_items),
    ):
        if entries:
            print(f"\n[{heading}]")
            print("\n".join(entries))

    return 1 if missing_h1 or broken_links or duplicate_anchors else 0


if __name__ == "__main__":
    sys.exit(main())
