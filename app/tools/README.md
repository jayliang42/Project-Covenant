# Lesson Tools | 课程工具

> Status: Draft (AI draft; not human reviewed) | 状态：Draft（AI 草稿，未人工审阅）

These scripts check and prepare the lessons in `src/content/lessons/`. They need Python 3 and the `pyyaml` package.<br>
这些脚本用来检查和准备 `src/content/lessons/` 里的课程。运行需要 Python 3 和 `pyyaml` 包。

<a id="check"></a>
## Check the Lessons | 检查课程

```bash
python3 app/tools/check_lessons.py            # all lessons | 全部课程
python3 app/tools/check_lessons.py FILE...    # some lessons | 指定的课程
```

The check reports four kinds of problem:<br>
检查会报告四类问题：

- Plain-writing patterns from section 8 of `AGENTS.md`, such as "not X but Y", intensifiers and dashes.<br>`AGENTS.md` 第 8 节列出的文风问题，例如“不是……而是……”、强调词和破折号。
- A Chinese paragraph without its English pair, or a heading without `中文 | English`.<br>中文段落后面没有对应的英文，或者标题没有写成 `中文 | English`。
- A scripture block whose wording differs from the 1919 Chinese Union Version or the World English Bible.<br>经文块的文字和 1919 年和合本或 World English Bible 不一致。
- A quoted verse in the body, written as `“…”（约 3:16）` or `“…” (John 3:16)`, whose words are not in the cited verses.<br>正文里写成 `“…”（约 3:16）` 或 `“…” (John 3:16)` 的引文，文字不在所引的经节里。

CI runs this check on every pull request. It reads the verses from `scripture-lock.json`, so it needs no download.<br>
每个 PR 的 CI 都会运行这项检查。它从 `scripture-lock.json` 读取经文，不需要下载。

<a id="new-verses"></a>
## Cite a New Verse | 引用新的经文

The lock file holds only the verses the lessons cite. When a lesson cites a verse that is not in it yet, fetch the source texts once, fill the scripture blocks, and rewrite the lock:<br>
锁文件只收录课程引用到的经节。课程引用了锁文件里还没有的经节时，先下载一次原文数据，再填充经文块，然后重写锁文件：

```bash
pip install pyyaml opencc
python3 app/tools/fetch_sources.py
python3 app/tools/fill_scripture.py app/src/content/lessons/new/13-example.md
python3 app/tools/check_lessons.py --update-lock
```

`fetch_sources.py` downloads the two texts into `app/tools/.sources/`, which git ignores. Both downloads are pinned to a commit. `fill_scripture.py` writes the `text` of each scripture entry from those texts, so the wording is never typed by hand.<br>
`fetch_sources.py` 把两份原文下载到 `app/tools/.sources/`，git 会忽略这个目录。两份下载都固定在某一次提交上。`fill_scripture.py` 根据原文写出每条经文的 `text`，所以经文不用手打。

<a id="texts"></a>
## The Two Texts | 两份原文

- English: World English Bible, public domain.<br>英文：World English Bible，公有领域。
- Chinese: Chinese Union Version of 1919, public domain, converted to simplified characters.<br>中文：1919 年出版的和合本，公有领域，已转换成简体字。

[Back to app README | 返回应用说明](../README.md)
