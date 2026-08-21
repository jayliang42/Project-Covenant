# Contributing Guide | 参与整理指南

> Use this guide when adding, translating, reorganizing, or reviewing public material in Project Covenant.
>
> 新增、翻译、重整或审阅 Project Covenant 的公开资料时，请遵守本指南。

[Project Home｜项目首页](./README.md) · [Master Index｜总索引](./INDEX.md) · [Agent Instructions｜代理说明](./AGENTS.md)

## 1. Language Status Vocabulary | 语言状态词

Use one of the following labels consistently in hubs and indexes.

请在入口页与索引中统一使用以下状态词。

| Status | Definition |
| --- | --- |
| **Full bilingual｜完整双语** | Substantive English and Chinese content are both present. A translated title or a few isolated sentences are not enough.｜实质英文与中文内容都已提供；只有翻译标题或少量零散句子不算完成。 |
| **Chinese full + English orientation｜中文全文＋英文导读** | The full research body is Chinese; English readers receive an accurate title, scope, status note, and route.｜完整研究正文为中文；英文读者可获得准确标题、范围、状态说明与使用路线。 |
| **English full + Chinese orientation｜英文全文＋中文导读** | The full guide is English; Chinese readers receive a reliable orientation or summary.｜完整正文为英文；中文读者可获得可靠导读或摘要。 |
| **Bilingual navigation｜双语导航** | A hub or index is bilingual, while linked files may have different translation status.｜入口或索引本身为双语；所链接文件的翻译状态可能不同。 |
| **Navigation / maintenance｜导航／维护** | A catalog, policy, audit, or maintenance log rather than a study essay.｜目录、规范、审计或维护记录，不是研读正文。 |
| **Supplemental study｜补充查考** | A study created from named sources; it is not presented as a recovered sermon transcript or missing original chapter.｜依据具名来源编写的查考；不冒充已恢复的讲道逐字稿或缺失原章。 |

The language status describes the repository document, not the language of the original Bible translation, sermon, or copyrighted book.

语言状态描述的是仓库文件，不代表原始圣经译本、讲道或受版权保护书籍本身的语言状态。

## 2. Bilingual Writing Standard | 双语写作标准

- Use a bilingual H1 title in the form `English | 中文` for every public Markdown document.
- Pair substantive paragraphs or sections in English and Chinese when claiming full bilingual status.
- Preserve source-language quotations, but explain their purpose and limits bilingually.
- Prefer translating a coherent guide or section over scattering disconnected translated sentences.
- Mark uncertainty, inference, missing source material, and translation boundaries explicitly.

- 每份公开 Markdown 文件都使用 `English | 中文` 形式的双语一级标题。
- 只有实质段落或章节具备成对英文与中文时，才可标为完整双语。
- 可以保留来源原文引语，但必须用双语说明其用途与边界。
- 优先完整翻译一篇导读或一个连贯章节，不要零散拼接互不相连的译句。
- 明确标注不确定处、推断、缺失来源与翻译边界。

## 3. Index and Reachability Rules | 索引与可达性规则

Every public Markdown file must be discoverable through repository navigation rather than only through GitHub’s file browser.

每份公开 Markdown 文件都必须能通过仓库导航找到，不能只依赖 GitHub 文件浏览器。

1. Link every new file from the nearest section hub or canonical index.
   每个新文件都加入最近的分区入口或权威索引。
2. Add major new routes to [INDEX.md](./INDEX.md); add primary entry points to [README.md](./README.md) when appropriate.
   重要新路线加入 [INDEX.md](./INDEX.md)；主要入口在合适时也加入 [README.md](./README.md)。
3. Put every dated sermon or fellowship note in [Bilingual_Notes/INDEX_Chronological.md](./Bilingual_Notes/INDEX_Chronological.md).
   每篇带日期的讲道或团契笔记都加入 [Bilingual_Notes/INDEX_Chronological.md](./Bilingual_Notes/INDEX_Chronological.md)。
4. Link every Bible Timeline research file from [Bible_Timeline/README.md](./Bible_Timeline/README.md) or from a clearly linked canonical sub-index.
   每份圣经时间线研究文件都应从 [Bible_Timeline/README.md](./Bible_Timeline/README.md) 或一个已被明确链接的权威子索引进入。
5. When a guide commonly opens as a deep link, provide a route back to its section hub or the master index.
   经常作为深层链接打开的长篇导读，应提供返回所属入口或总索引的路线。
6. Do not maintain duplicate exhaustive lists unless one is generated automatically; duplicate lists drift.
   除非由程序自动生成，否则不要维护多份重复的完整清单；重复清单容易失去同步。

## 4. Research and Evidence Standard | 研究与证据标准

- Prefer primary sources, museum or archive records, excavation publications, critical editions, official publisher records, and peer-reviewed scholarship.
- Distinguish biblical narrative, event evidence, historical background, manuscripts, reception history, philosophy, natural science, testimony, and theological interpretation.
- Record both what a source can support and what it cannot establish.
- Separate material type from judgment strength. An early manuscript may be strong MS evidence while providing no direct EV evidence for an event inside the book.
- Present materially disputed dates, identifications, readings, or models as disputes rather than resolved facts.
- Do not turn correlation into proof, absence of evidence into automatic disproof, or a later citation into proof of traditional authorship or every narrated event.

- 优先使用一手来源、博物馆或档案记录、发掘报告、校勘本、出版社正式记录与同行评议研究。
- 区分圣经叙事、事件旁证、历史背景、抄本、接收史、哲学、自然科学、见证与神学解释。
- 同时记录材料能支持什么、不能建立什么。
- 分开材料类型与判断强度。早期抄本可以是强 MS 证据，却不一定为卷内事件提供直接 EV 证据。
- 对有实质争议的年代、认定、释读或模型，应呈现争议，不写成已经解决的事实。
- 不把对应关系扩大为证明，不把“尚未发现”自动写成反证，也不把后期引文扩大成对传统作者或全部叙事事件的证明。

## 5. File Placement and Naming | 文件位置与命名

| Material | Directory | Required navigation update |
| --- | --- | --- |
| Sermon, fellowship, or discipleship note｜讲道、团契或门训笔记 | `Bilingual_Notes/` | Notes hub and chronological index｜笔记中心与时间索引 |
| Bible-wide guide, study plan, evidence index, or historical dossier｜整本圣经导读、计划、旁证索引或历史专题 | `Bible_Timeline/` | Timeline hub and, for major routes, master index｜时间线中心；重要路线还须加入总索引 |
| Christian book guide｜基督教书籍导读 | `Book_Studies/` | Book Studies hub and master index｜书籍研读中心与总索引 |
| Bible translation access or reading guide｜圣经译本获取或阅读指南 | `Bible_Translations/` | Translation hub and master index｜译本中心与总索引 |
| Audit or maintenance automation｜审计或维护自动化 | `scripts/` or `.github/workflows/` | Maintenance section of the master index when user-facing｜若面向使用者，应加入总索引维护分区 |

Keep existing filenames stable. If a rename is necessary, update every repository link in the same change. Use relative Markdown links; never commit local absolute paths, `file://` URLs, editor-only links, credentials, or private identifiers.

保持现有文件名稳定。若确需改名，必须在同一次修改中更新仓库内所有链接。仓库文件使用相对 Markdown 链接；不得提交本机绝对路径、`file://`、编辑器专用链接、凭证或私人识别信息。

## 6. Copyright and Source Boundaries | 版权与来源边界

- Do not commit complete copyrighted Bible translations, commercial books, raw sermon transcripts without permission, proprietary application modules, or private downloads.
- Summarize and analyze rather than reproducing substantial source text.
- State the edition or public structure used when books differ by edition.
- Use official access instructions for copyrighted resources and preserve any permission note.
- Never reconstruct a private or unavailable table of contents as though it were verified.

- 不得提交受版权保护的整本圣经译文、商业书籍、未经许可的完整讲道逐字稿、专有应用模块或私人下载文件。
- 应总结、分析，而不是大量复制来源正文。
- 原书版本有差异时，说明导读依据的版本或公开结构。
- 对受版权保护资源使用官方获取说明，并保留授权注记。
- 不得把私人或无法取得的目录虚构成已经核实的目录。

## 7. Verification Workflow | 验证流程

Before publishing a documentation change:

发布文档修改前：

1. Inspect the target file, its section hub, and existing incoming links.
   检查目标文件、所属入口与现有进入链接。
2. Make the smallest complete change that resolves the navigation, language, or research issue.
   做解决导航、语言或研究问题所需的最小完整修改。
3. Run `python3 scripts/audit_markdown.py` from the repository root.
   在仓库根目录运行 `python3 scripts/audit_markdown.py`。
4. Run `git diff --check` in a local checkout when available.
   若使用本地检出，运行 `git diff --check`。
5. Review the exact diff for broken links, stale status labels, accidental source reproduction, and unrelated edits.
   复核精确差异，检查失效链接、过期状态词、意外复制来源正文与无关修改。
6. Publish through a focused branch and pull request rather than editing the default branch directly.
   通过聚焦的分支与拉取请求发布，不直接修改默认分支。

Run the Markdown audit before opening or merging a pull request. If repository CI is added later, it should invoke the same command so local and automated checks stay aligned.

在创建或合并拉取请求前运行 Markdown 审计。若以后加入仓库 CI，应调用同一命令，使本地检查与自动检查保持一致。

[Back to Project Home｜返回项目首页](./README.md) · [Open Master Index｜打开总索引](./INDEX.md)
