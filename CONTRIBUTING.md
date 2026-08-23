# Contributing | 参与整理

## English

### Bilingual standard

- Use bilingual titles for new entry pages, indices, and study guides: `English | 中文`.
- A file is **fully bilingual** only when its substantive content is available in both languages.
- If a long research text is currently Chinese-only or English-only, provide an accurate bilingual title and a short navigation summary; do not imply that the full text has already been translated.
- Prefer translating a complete small guide or a coherent section over scattered sentence-by-sentence fragments.

### Research standard

- Link primary sources, museum collections, excavation projects, or peer-reviewed scholarship where possible.
- Separate event evidence, historical background, manuscripts, reception history, and theological interpretation.
- State both what a source can support and what it cannot establish.
- Do not turn an archaeological correlation, an ancient manuscript, or a later citation into automatic proof of an event, author, miracle, or doctrine.

### File structure

- Put sermon and fellowship material in `Bilingual_Notes/` and update its chronological index.
- Put Bible-wide guides, plans, evidence indexes, and research dossiers in `Bible_Timeline/`.
- Link new Bible Timeline material from `Bible_Timeline/README.md`; link major new entry points from the root `README.md`.
- Preserve existing filenames unless a coordinated link update is part of the change.

### Privacy and publication

- Follow [PUBLICATION_POLICY.md](./PUBLICATION_POLICY.md). Do not add a maintainer's or private participant's identity, contact route, personal history, immigration or asylum information, medical history, testimony, attendance history, or identifiable anecdote.
- A church name may remain when relevant, but never pair it with a private person's role, address, contact details, care information, or participation history.
- Treat transcripts, recordings, downloads, meeting links, and attachments as private source material. Publish only a reviewed, non-identifying summary.
- A future website may publish only files explicitly listed in `publication/site-content.txt`.
- Before committing, run `python3 scripts/audit_markdown.py`, `python3 scripts/audit_publication.py`, `python3 scripts/audit_publication.py --history-content`, and `git diff --check`.

## 中文

### 双语标准

- 新入口页、索引和研读指南使用双语标题：`English | 中文`。
- 只有正文实质内容同时具备中英文时，文件才可标为“完整双语”。
- 长篇研究稿若暂时只有中文或英文，须提供准确的双语标题和简短导航说明；不可把尚未完成的翻译写成已完成双语。
- 优先完整翻译一篇短导读或一个连贯章节，不要零散地逐句拼贴。

### 研究标准

- 尽量链接原始文本、博物馆馆藏、发掘项目或同行评议研究。
- 分开事件旁证、历史背景、抄本、接收史与神学解释。
- 同时说明材料“能支持什么”与“不能证明什么”。
- 不把考古对应、古代抄本或后期引文自动扩大成对事件、作者、神迹或教义的证明。

### 文件结构

- 讲道与团契材料放入 `Bilingual_Notes/`，并更新其时间索引。
- 整本圣经导读、计划、旁证索引和研究专题放入 `Bible_Timeline/`。
- 新增圣经时间线资料应从 `Bible_Timeline/README.md` 导航；重大新入口也应加入根目录 `README.md`。
- 除非同步更新所有链接，否则保留现有文件名。

### 隐私与发布

- 遵守 [PUBLICATION_POLICY.md](./PUBLICATION_POLICY.md)。不得加入维护者或私人参与者的身份、联系入口、个人经历、移民或庇护信息、医疗经历、见证、出席记录或可识别轶事。
- 教会名称与资料有关时可以保留，但不得与私人个人的职分、地址、联系方式、关怀信息或参与经历组合出现。
- 逐字稿、录音录像、下载文件、会议链接和附件都视为私人来源；公开内容只能是经过复核、无法识别个人的总结。
- 未来网站只能发布 `publication/site-content.txt` 明确列出的文件。
- 提交前运行 `python3 scripts/audit_markdown.py`、`python3 scripts/audit_publication.py`、`python3 scripts/audit_publication.py --history-content` 和 `git diff --check`。
