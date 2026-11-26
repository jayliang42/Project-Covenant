"""Download the two public-domain Bible texts the lesson tools read.

    python3 app/tools/fetch_sources.py

Writes app/tools/.sources/ (ignored by git). Both repositories are pinned to a
commit so the text cannot change under the checks.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE / ".sources"
WEB = ("https://github.com/TehShrike/world-english-bible.git", "68669ba")
CHI = ("https://github.com/scrollmapper/bible_databases.git", "59b18c5", "formats/json/ChiUn.json")


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def main() -> int:
    SOURCES.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        web = Path(tmp) / "web"
        run("git", "clone", "--quiet", WEB[0], str(web))
        run("git", "checkout", "--quiet", WEB[1], cwd=web)
        target = SOURCES / "web"
        if target.exists():
            shutil.rmtree(target)
        target.mkdir()
        shutil.copytree(web / "json", target / "json")

        chi = Path(tmp) / "chi"
        run("git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", CHI[0], str(chi))
        run("git", "checkout", "--quiet", CHI[1], "--", CHI[2], cwd=chi)
        shutil.copy(chi / CHI[2], SOURCES / "ChiUn.json")
    print("sources ready in", SOURCES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
