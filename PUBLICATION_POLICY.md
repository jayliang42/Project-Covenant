# Privacy and Publication Policy | 隐私与发布政策

## Purpose | 目的

Project Covenant is a public reading library. Public pages may explain Scripture, historical research, archaeology, Christian books, and teaching themes, but they must not disclose the maintainer's identity, contact details, private history, or personal participation.

Project Covenant 是一个供公众阅读的资料库。公开页面可以整理圣经、历史研究、考古、基督教书籍和讲道主题，但不得披露维护者的身份、联系方式、私人经历或个人参与情况。

## What May Be Published | 可以发布什么

- Biblical people, historical people, published authors, and other people already identified by a cited public source may be named when the name is necessary to understand the material.
- A church name may remain when it is relevant to the source. It must not be combined with a private person's role, attendance, home-group location, contact details, pastoral-care information, or other facts that could identify that person.
- Teaching dates are source-session dates. They describe the material being summarized and do not state that the maintainer attended the session.

- 为理解资料所必需时，可以写出圣经人物、历史人物、已出版作者，以及由所引公开来源明确识别的其他人物。
- 教会名称与来源有关时可以保留，但不得与私人个人的职分、出席情况、家庭小组地点、联系方式、牧养关怀信息或其他可重新识别个人的事实组合出现。
- 讲道日期是来源聚会的日期，只用于说明所整理的材料，不表示维护者参加过该聚会。

## What Must Stay Private | 不得公开什么

- The maintainer's or a private participant's real name, personal username, email address, phone number, social-media profile, street address, school, employer, family details, or contact route.
- Personal immigration or asylum information, legal case information, document numbers, medical or mental-health history, conversion or baptism story, testimony, discipleship history, attendance history, or other autobiographical experience.
- Raw transcripts, recordings, private downloads, meeting invitations, access codes, credentials, private keys, environment files, and unreviewed attachments.
- A private anecdote must be removed or generalized into a non-identifying teaching point. Changing only the person's name is not sufficient when the remaining details can still identify the person.

- 维护者或私人参与者的真实姓名、个人用户名、电子邮箱、电话号码、社交媒体主页、街道地址、学校、雇主、家庭信息或联系入口。
- 个人移民或庇护信息、法律案件信息、证件号码、医疗或心理健康经历、信主或受洗经历、个人见证、门徒训练经历、聚会出席记录，以及其他自传性经历。
- 原始逐字稿、录音录像、私人下载文件、会议邀请、访问码、凭证、私钥、环境文件及未经审核的附件。
- 私人轶事必须删除，或改写成无法识别个人的一般教学要点。若其余细节仍能识别人，仅删除姓名并不够。

## Publication Review | 发布审核

Every tracked file is scanned for common personal identifiers, secrets, local paths, contact routes, and autobiographical disclosures. Sermon notes also require human review because a scanner cannot reliably distinguish a general illustration from a recognizable personal story.

所有 Git 跟踪文件都要扫描常见个人识别信息、密钥、本机路径、联系入口和自传性披露。讲道笔记还必须经过人工复核，因为扫描器无法可靠地区分一般例证和可识别的个人故事。

Run these checks before publishing:

发布前运行以下检查：

```bash
python3 scripts/audit_markdown.py
python3 scripts/audit_publication.py
python3 scripts/audit_publication.py --history-content
git diff --check
```

Use `python3 scripts/audit_publication.py --history` for the stricter audit that also checks redacted Git author, email, tagger, and remote-owner metadata. After transfer to a reviewed neutral owner, pass that public account with `--approved-remote-owner OWNER`. The command is expected to pass only after neutral ownership and sanitized history have been established.

使用 `python3 scripts/audit_publication.py --history` 运行更严格的检查；它还会以脱敏形式检查 Git 作者、邮箱、标签作者和远端所有者元数据。仓库转移到经过复核的中性所有者后，用 `--approved-remote-owner OWNER` 明确传入该公开账号。只有中性账号归属和脱敏历史都已经建立之后，这项检查才应通过。

## Future Website Boundary | 未来网站的发布边界

The future website must read only the exact files listed in [`publication/site-content.txt`](./publication/site-content.txt). It must never copy the repository recursively. Files not on the list are excluded from the website by default; if they are tracked in this public repository, they are still readable on GitHub.

未来网站只能读取 [`publication/site-content.txt`](./publication/site-content.txt) 明确列出的文件，绝不能递归复制整个仓库。未列入清单的文件默认不进入网站；若这些文件已被公开仓库跟踪，它们仍可在 GitHub 上阅读。

Inclusion in the list means that a page has passed the privacy and link-boundary review; it does not by itself mean that full bilingual migration is complete. The website must show the language status stated by the library hubs and must never label a Chinese-body research dossier as fully bilingual.

列入清单表示页面已经通过隐私与链接边界复核，并不表示完整双语迁移已经完成。网站必须显示资料导航页标注的语言状态，也不得把中文正文研究专题标成“完整双语”。

Generated pages must be scanned again before deployment. Source maps, image metadata, build logs, hidden drafts, and local filesystem paths must not enter the deployed artifact.

生成的网站页面必须在部署前再次扫描。Source map、图片元数据、构建日志、隐藏草稿和本机文件路径都不得进入部署产物。

## Git Hosting Metadata | Git 托管元数据

Content review does not hide repository ownership, commit author names, commit email addresses, forks, pull requests, or other hosting metadata. A repository that must not identify its maintainer also needs neutral account ownership and sanitized Git history; a clean Markdown tree alone cannot provide that guarantee.

内容审核不会隐藏仓库所有权、提交作者姓名、提交邮箱、fork、pull request 或其他托管平台元数据。如果仓库本身也不能识别维护者，还需要中性的账号归属和已脱敏的 Git 历史；仅有干净的 Markdown 当前树并不能提供这一保证。
