# Content Guide | 内容编辑指南

> Status: Draft (AI draft; not human reviewed) | 状态：Draft（AI 草稿，未人工审阅）

All learning content lives in `src/content/`. You only edit Markdown and YAML; the pages, navigation, progress and offline cache update themselves on the next build.<br>
所有课程内容都在 `src/content/` 里。只需要改 Markdown 和 YAML，页面、导航、进度和离线缓存会在下次构建时自动更新。

```text
src/content/
  tracks/            一条路径一个 YAML（好奇 / 慕道 / 初信 / 深耕）
    curious.yaml
    seeking.yaml
    new.yaml
    deeper.yaml
  lessons/           一课一个 Markdown，放在所属路径的文件夹里
    curious/01-a-library-of-books.md
    ...
```

<a id="add-a-lesson"></a>
## Add a Lesson | 加一课

1. Create a file in the track's folder, e.g. `src/content/lessons/new/06-why-church.md`. The file name becomes the URL, so use lowercase English and hyphens.<br>
   在对应路径的文件夹里新建文件，例如 `src/content/lessons/new/06-why-church.md`。文件名会成为网址，请用小写英文和连字符。
2. Copy the template below, fill in the fields, and write the body.<br>
   复制下面的模板，填好字段，再写正文。
3. Run `npm run dev` to preview, or `npm run build` to check everything.<br>
   运行 `npm run dev` 预览，或 `npm run build` 做完整检查。

```markdown
---
title: { zh: 为什么要去教会, en: Why go to church? }
summary:
  zh: 一句话说明这一课讲什么。
  en: One sentence on what this lesson covers.
unit: church            # 必须是该路径 YAML 里某个单元的 id
order: 2                # 单元内的顺序，可以用 1.5 插队
minutes: 6              # 预计阅读分钟数
status: published       # published 上线；planned 只显示“筹备中”
review: draft           # draft 显示“草稿·待人工审阅”；AI 核对过改成 checked（显示“AI 已审阅核对”）；人工审过改成 reviewed
art: table-fellowship   # 可选：../assets/art/ 里的插画名（不带 .svg）
scripture:
  - { ref: "来 10:24-25", refEn: "Hebrews 10:24-25" }
reflect:
  - { zh: 一个思考题。, en: A reflection question. }
check:
  - q: { zh: 一个小测验问题？, en: A quiz question? }
    options:
      - { zh: 选项 A, en: Option A }
      - { zh: 选项 B, en: Option B }
    answer: 1           # 正确选项的位置，从 0 开始数
    explain: { zh: 为什么。, en: Why. }
further:
  - label: { zh: 资料库里的相关页面, en: Related library page }
    path: "Bible_Timeline/Key_Passages_Bilingual.md"
    why: { zh: 一句话说明为什么值得延伸读这篇资料。, en: One sentence on why this deep-dive page is worth reading next. }
sources:                # 可选：核对史实时用的公开资料，显示在课文末尾
  - label: { zh: 资料名称（出处）, en: Source title (publisher) }
    url: "https://example.org/page"
---

## 小标题 | Heading

中文段落。<br>
English paragraph.
```

<a id="yaml-pitfall"></a>
## One YAML Pitfall | 一个 YAML 陷阱

In the one-line `{ zh: ..., en: ... }` form, a value that contains an English comma `,` or a colon followed by a space must be wrapped in double quotes. Chinese punctuation (，：) is fine without quotes. If you forget, the build stops and names the file and the stray key.<br>
在单行的 `{ zh: ..., en: ... }` 写法里，如果值含有英文逗号 `,` 或“冒号＋空格”，必须用双引号包起来；中文标点（，：）不需要。忘了加引号时，构建会报错并指出是哪个文件、哪个多出来的键。

```yaml
summary: { zh: 读经与祷告, en: "Reading, prayer and rest" }   # ✅
summary: { zh: 读经与祷告, en: Reading, prayer and rest }     # ❌ 构建报错
```

For long text, the two-line form avoids the problem entirely:<br>
长文字用分行写法就不会遇到这个问题：

```yaml
summary:
  zh: 这里可以随便用标点，包括英文逗号, 和冒号: 都没问题。
  en: Anything goes here, including commas, and colons.
```

<a id="writing-bilingual"></a>
## Writing in Two Languages | 双语写法

The reader can switch between 中文, EN and 中英. The app works out each paragraph's language automatically, so just write naturally in any of these ways:<br>
读者可以在“中文 / EN / 中英”之间切换。应用会自动判断每段的语言，用下面任意一种写法即可：

- Separate paragraphs: a Chinese paragraph, a blank line, then the English paragraph (either order).<br>分开两段：中文一段，空一行，英文一段（顺序不限）。
- One paragraph with `<br>` between the languages, as in the existing library.<br>同一段里用 `<br>` 隔开两种语言，与现有资料库写法相同。
- Headings as `中文 | English`.<br>标题写成 `中文 | English`。
- List items as `中文<br>English`.<br>列表项写成 `中文<br>English`。

English is optional while drafting; untranslated text is shown in every mode. Tables are always shown in full.<br>
草稿阶段英文可以先不写，没有翻译的内容在所有模式下都会显示。表格总是完整显示。

<a id="plain-writing"></a>
## Plain Writing | 平实的写法

Lessons should read like one person explaining something to a friend. The full rule is section 8 of the repository `AGENTS.md`; the short version is below.<br>
课程读起来应该像一个人在给朋友讲解。完整规则见仓库 `AGENTS.md` 第 8 节，下面是简要版。

- State the point directly. Do not use "not X but Y" or "not just X but also Y".<br>直接说要说的事。不用“不是……而是……”“不只是……更是……”。
- Let people and God do the acting. Use few metaphors and write no slogans.<br>让人和神作动作的主语。少用比喻，不写金句。
- Keep the subject close to its verb, and put one idea in one sentence.<br>主语和谓语靠近，一句话只讲一件事。
- Keep the connecting words a reader needs. Do not compress a sentence until it must be read twice.<br>保留读者需要的连接词。不要把句子压缩到要读两遍才懂。
- Avoid intensifying words such as "profound", "crucial", and "truly".<br>不用“深刻”“极其”“真正”“核心”这类强调词。
- Use a short phrase or a question as a heading. In English, avoid em dashes.<br>标题用短语或问句。中文不用破折号（——）插入补充说明。
- A style edit must leave the facts unchanged.<br>改文风时不能改变事实。

<a id="scripture"></a>
## Scripture | 经文

`refEn` is used to build a link to an online reader (configured in `src/config.ts`). Only put verse wording in `text` if it is public domain: 和合本 (1919) for Chinese and the World English Bible (WEB) for English. Do not paste ESV, NIV, 新译本 or other copyrighted text.<br>
`refEn` 用来生成外部经文阅读链接（在 `src/config.ts` 设置）。只有公有领域的译本才能把经文原文写进 `text`：中文用和合本（1919），英文用 World English Bible（WEB）。不要贴 ESV、NIV、新译本等有版权的经文。

<a id="units-and-tracks"></a>
## Units and Tracks | 单元与路径

- To add, rename or reorder a unit, edit the `units` list in the track's YAML. The order in the list is the order on screen.<br>加单元、改名或调整顺序，改对应路径 YAML 里的 `units` 列表；列表顺序就是显示顺序。
- A unit with no lessons yet shows “coming soon”. A lesson with `status: planned` only needs `title`, `summary`, `unit` and `order`. This is a handy way to plan the roadmap.<br>还没有课的单元会显示“筹备中”。`status: planned` 的课只需要 `title`、`summary`、`unit`、`order`，可以拿来先排课程规划。
- A new track needs a YAML file in `tracks/`, a folder in `lessons/`, and its id added to `TRACK_ORDER` in `src/config.ts`.<br>新增一条路径：在 `tracks/` 加 YAML，在 `lessons/` 加同名文件夹，并把 id 加进 `src/config.ts` 的 `TRACK_ORDER`。

<a id="sources-and-review"></a>
## Sources and Unit Reviews | 资料来源和单元回顾

- List the public sources used to check a lesson's dates, numbers and history under `sources`. They are shown at the end of the lesson. A lesson that only explains Scripture can leave the list empty.<br>核对一课的年代、数字和史实时用过的公开资料，写在 `sources` 里，会显示在课文末尾。只讲解经文的课可以不写。
- When traditions disagree on a topic, describe each view in its own words and name the tradition that holds it. Do not present one view as the only Christian view.<br>各传统看法不同的题目，要按各自的说法分别写出来，并写明是哪个传统的看法。不要把其中一种写成基督教唯一的看法。
- Every unit with two or more published lessons gets a review page at `review/<track>/<unit>/`. The page is built from the lessons: it lists each summary and takes the last quiz question of each lesson. There is nothing extra to write.<br>有两课以上已上线课程的单元，会自动生成单元回顾页 `review/<路径>/<单元>/`。页面内容来自各课：列出每课的摘要，并取每课的最后一道测验题。不需要另外写内容。

<a id="lesson-checks"></a>
## Checking Lessons | 检查课程

`tools/check_lessons.py` checks every lesson for the plain-writing patterns, bilingual pairing, scripture wording against the 1919 Union text and the WEB, and quoted verses in the body. CI runs it on every pull request. See [tools/README.md](./tools/README.md).<br>
`tools/check_lessons.py` 检查每一课的文风、中英配对、经文块是否和 1919 年和合本及 WEB 原文一致，以及正文里引用的经文。每个 PR 的 CI 都会运行它。说明见 [tools/README.md](./tools/README.md)。

<a id="build-checks"></a>
## What the Build Checks | 构建会检查什么

The build fails with a clear message if a lesson names a unit that does not exist, a quiz answer is out of range, a published lesson has no body, a required field is missing, or a track is missing from `TRACK_ORDER`.<br>
如果某课写了不存在的单元、测验答案超出选项范围、已上线的课没有正文、缺少必填字段，或者路径没有写进 `TRACK_ORDER`，构建会失败并给出清楚的提示。

[Back to app README | 返回应用说明](./README.md)
