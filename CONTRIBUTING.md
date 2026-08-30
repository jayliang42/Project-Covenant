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

- These instructions apply to the full maintenance checkout. The exported neutral repository is a generated, read-only reading mirror and intentionally contains no scripts, tests, or CI workflow.
- Follow [PUBLICATION_POLICY.md](./PUBLICATION_POLICY.md). Do not add a maintainer's or private participant's identity, contact route, personal history, immigration or asylum information, medical history, testimony, attendance history, or identifiable anecdote.
- A church name may remain when relevant, but never pair it with a private person's role, address, contact details, care information, or participation history.
- Treat transcripts, recordings, downloads, meeting links, and attachments as private source material. Publish only a reviewed, non-identifying summary.
- A future website may publish only files explicitly listed in `publication/site-content.txt`.
- Commit all intended public changes, then export only from a fresh, reviewed, clean checkout. Content selection uses the committed ref, but the running exporter and audit code still come from that checkout.
- Create a Git-history-free snapshot with `python3 scripts/export_publication.py export --ref HEAD --output /tmp/project-covenant-public`. Keep the printed digest separately, then verify with `python3 scripts/export_publication.py verify --input /tmp/project-covenant-public --expected-content-set-sha256 DIGEST_FROM_EXPORT`.
- Build the static reading site only from that verified snapshot with `python3 scripts/build_static_site.py build --snapshot /tmp/project-covenant-public --expected-content-set-sha256 DIGEST_FROM_EXPORT --output /tmp/project-covenant-site`, then repeat the `verify` subcommand against the same snapshot and retained digest.
- The generated site is a deployment artifact, not a second source tree. Do not edit it directly or add scripts, analytics, forms, comments, remote assets, source maps, repository links, or publication metadata.
- Inspect the rendered Markdown manually before release. Automated checks are necessary safeguards, but they cannot prove that every recognizable personal detail has been removed.
- The snapshot does not anonymize the uploading account. An identity-minimized release needs a reviewed neutral owner and a new non-fork repository populated only from the clean snapshot.
- Before committing, run `python3 -m unittest discover -s tests -v`, `python3 scripts/audit_markdown.py`, `python3 scripts/audit_publication.py`, `python3 scripts/audit_publication.py --history-content`, and `git diff --check`.

### Licensing

- Contributions to original written content are submitted under `CC BY-NC-SA 4.0`; contributions to scripts, tests, and workflow code are submitted under the MIT License described in [LICENSE.md](./LICENSE.md).
- Contribute only material you created, material you have permission to license, or properly identified third-party material used under an applicable license or legal exception.
- Do not imply that Project Covenant's licenses cover Bible translations, published books, quotations, images, transcripts, or linked works owned by others.
- Preserve attribution, copyright, permission, and edition notes when revising a page.

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

- 本说明适用于完整维护工作区。导出后的中性仓库是生成的只读阅读镜像，会有意不包含脚本、测试或 CI workflow。
- 遵守 [PUBLICATION_POLICY.md](./PUBLICATION_POLICY.md)。不得加入维护者或私人参与者的身份、联系入口、个人经历、移民或庇护信息、医疗经历、见证、出席记录或可识别轶事。
- 教会名称与资料有关时可以保留，但不得与私人个人的职分、地址、联系方式、关怀信息或参与经历组合出现。
- 逐字稿、录音录像、下载文件、会议链接和附件都视为私人来源；公开内容只能是经过复核、无法识别个人的总结。
- 未来网站只能发布 `publication/site-content.txt` 明确列出的文件。
- 先提交全部预定公开修改，再从全新、经过复核且干净的 checkout 生成快照。内容选择使用已提交 ref，但实际运行的导出器和审计代码仍来自该 checkout。
- 用 `python3 scripts/export_publication.py export --ref HEAD --output /tmp/project-covenant-public` 生成不带 Git 历史的快照。另行保存输出的摘要，再用 `python3 scripts/export_publication.py verify --input /tmp/project-covenant-public --expected-content-set-sha256 DIGEST_FROM_EXPORT` 复核。
- 只能从该已验证快照构建静态阅读站点：运行 `python3 scripts/build_static_site.py build --snapshot /tmp/project-covenant-public --expected-content-set-sha256 DIGEST_FROM_EXPORT --output /tmp/project-covenant-site`，再用同一快照与另行保存的摘要重复运行 `verify` 子命令。
- 生成站点是部署产物，不是第二份源代码树。不得直接编辑，也不得加入脚本、分析追踪、表单、评论、远程资源、source map、仓库链接或发布元数据。
- 发布前必须人工查看 Markdown 的实际渲染结果。自动检查是必要防线，但无法证明所有可识别的个人细节都已清除。
- 快照不会匿名化上传账号。若要尽量降低身份关联，需要经过复核的中性所有者，并把干净快照单独导入全新且非 fork 的仓库。
- 提交前运行 `python3 -m unittest discover -s tests -v`、`python3 scripts/audit_markdown.py`、`python3 scripts/audit_publication.py`、`python3 scripts/audit_publication.py --history-content` 和 `git diff --check`。

<a id="contributing-licensing-zh"></a>
### 授权规则

- 原创文字贡献按 `CC BY-NC-SA 4.0` 提交；脚本、测试和工作流代码按 [LICENSE.md](./LICENSE.md) 所说明的 MIT License 提交。
- 只提交自己创作、有权授权，或已按适用许可证及法律例外明确标注的第三方材料。
- 不得暗示 Project Covenant 的许可证涵盖他人拥有的圣经译本、已出版书籍、引文、图片、逐字稿或链接作品。
- 修订页面时必须保留署名、版权、授权和版本说明。
