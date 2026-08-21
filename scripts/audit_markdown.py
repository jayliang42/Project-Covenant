#!/usr/bin/env python3
"""Audit bilingual titles, local links, and index reachability."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CHINESE = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")
H1 = re.compile(r"^# (.+)$", re.MULTILINE)
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
ENTRYPOINTS = ("README.md", "INDEX.md")


def tracked_markdown() -> list[Path]:
    """Return every tracked Markdown file as an absolute resolved path."""

    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(
        (ROOT / Path(item)).resolve()
        for item in result.stdout.decode("utf-8").split("\0")
        if item
    )


def local_target(current: Path, raw_target: str) -> tuple[Path | None, str | None]:
    """Resolve a local Markdown target and optional fragment.

    External URLs return ``(None, None)`` and are outside this repository audit.
    """

    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        # Markdown permits an optional quoted title after the URL. Repository
        # filenames intentionally avoid literal spaces, so the first token is
        # the target used by this audit.
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


def relative_name(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def reachable_files(
    files: set[Path], link_graph: dict[Path, set[Path]]
) -> set[Path]:
    """Walk Markdown links from the public repository entry points."""

    queue: deque[Path] = deque()
    for name in ENTRYPOINTS:
        entry = (ROOT / name).resolve()
        if entry in files:
            queue.append(entry)

    reachable: set[Path] = set()
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        for target in sorted(link_graph.get(current, set())):
            if target in files and target not in reachable:
                queue.append(target)

    return reachable


def main() -> int:
    files = tracked_markdown()
    file_set = set(files)
    texts = {path: path.read_text(encoding="utf-8") for path in files}

    h1_issues: list[str] = []
    duplicate_anchors: list[str] = []
    broken_links: list[str] = []
    unverified_fragments: list[str] = []
    unlinked_index_items: list[str] = []
    unpaired_chinese_lines: list[str] = []
    unpaired_by_file: dict[str, int] = {}
    link_graph: dict[Path, set[Path]] = {path: set() for path in files}
    paired_bilingual_lines = 0
    bilingual_body = 0
    h1_total = 0

    for path in files:
        text = texts[path]
        relative = relative_name(path)

        if CHINESE.search(text) and LATIN.search(text):
            bilingual_body += 1

        # A mixed-script file is not enough: a Chinese paragraph should have
        # a nearby English counterpart. We accept either ordering so existing
        # research dossiers can be migrated incrementally. This is a migration
        # signal rather than a fatal error because tables, quotations, and
        # source lists can legitimately produce false positives.
        lines = text.splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or not CHINESE.search(stripped) or LATIN.search(stripped):
                continue
            nearby_latin = False
            for neighbor_index in (index - 1, index + 1):
                if 0 <= neighbor_index < len(lines):
                    neighbor = lines[neighbor_index].strip()
                    if neighbor and LATIN.search(neighbor):
                        nearby_latin = True
                        break
            if nearby_latin:
                paired_bilingual_lines += 1
            else:
                unpaired_chinese_lines.append(f"{relative}:{index + 1}: {stripped}")
                unpaired_by_file[relative] = unpaired_by_file.get(relative, 0) + 1

        h1s = H1.findall(text)
        h1_total += len(h1s)
        if not h1s:
            h1_issues.append(f"{relative}: missing H1")
        elif len(h1s) > 1:
            h1_issues.append(f"{relative}: multiple H1 headings ({len(h1s)})")
        if h1s and any("|" not in title for title in h1s):
            h1_issues.append(f"{relative}: H1 is not bilingual with `English | 中文`")

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

            try:
                target_path.relative_to(ROOT)
            except ValueError:
                broken_links.append(
                    f"{relative}: [{label}]({raw_target.strip()}) escapes repository root"
                )
                continue

            if not target_path.is_file():
                broken_links.append(f"{relative}: [{label}]({raw_target.strip()})")
                continue

            if target_path.suffix.lower() == ".md" and target_path in file_set:
                link_graph[path].add(target_path)

            if fragment and target_path.suffix.lower() == ".md":
                target_anchors = set(ANCHOR.findall(texts.get(target_path, "")))
                if fragment not in target_anchors:
                    unverified_fragments.append(
                        f"{relative}: [{label}] -> {relative_name(target_path)}#{fragment}"
                    )

        if index_like(path):
            for line_number, line in enumerate(lines, start=1):
                # Only flag list entries that appear to name a concrete file.
                # Explanatory bullets and checklists are not index rows.
                if (
                    LIST_ITEM.match(line)
                    and "[" not in line
                    and CODE_FILE_REFERENCE.search(line)
                ):
                    unlinked_index_items.append(f"{relative}:{line_number}: {line.strip()}")

    reachable = reachable_files(file_set, link_graph)
    unreachable = sorted(file_set - reachable, key=relative_name)

    print(f"markdown_files={len(files)}")
    print(f"reachable_markdown_files={len(reachable)}/{len(files)}")
    print(f"bilingual_body_files={bilingual_body}/{len(files)}")
    print(f"bilingual_h1={h1_total - len([item for item in h1_issues if 'not bilingual' in item])}/{h1_total}")
    print(f"h1_issues={len(h1_issues)}")
    print(f"broken_local_links={len(broken_links)}")
    print(f"duplicate_explicit_anchors={len(duplicate_anchors)}")
    print(f"fragments_needing_github_slug_review={len(unverified_fragments)}")
    print(f"unlinked_file_items_in_indexes={len(unlinked_index_items)}")
    print(f"paired_bilingual_lines={paired_bilingual_lines}")
    print(f"unpaired_chinese_lines={len(unpaired_chinese_lines)}")
    print(
        "largest_unpaired_files="
        + ", ".join(
            f"{path}:{count}"
            for path, count in sorted(
                unpaired_by_file.items(), key=lambda item: (-item[1], item[0])
            )[:12]
        )
    )

    report_sections = (
        ("h1_issues", h1_issues),
        ("broken_links", broken_links),
        ("duplicate_explicit_anchors", duplicate_anchors),
        (
            "unreachable_markdown_files",
            [relative_name(path) for path in unreachable],
        ),
        ("fragments_needing_github_slug_review", unverified_fragments),
        ("unlinked_file_items_in_indexes", unlinked_index_items),
        ("unpaired_chinese_lines_sample", unpaired_chinese_lines[:80]),
    )
    for heading, entries in report_sections:
        if entries:
            print(f"\n[{heading}]")
            print("\n".join(entries))

    fatal = bool(h1_issues or broken_links or duplicate_anchors or unreachable)
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
