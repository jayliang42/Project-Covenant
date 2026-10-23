# About This Library | 关于本资料库

> Status: Draft (AI draft; not human reviewed) | 状态：Draft（AI 草稿，未人工审阅）

> How Project Covenant is written and reviewed, what its language labels mean, where its research stops, and how to build or read it offline.<br>
> 本页说明 Project Covenant 如何编写和审阅、语言标注的含义、研究的边界，以及如何构建或离线阅读。

<a id="what-this-library-does"></a>
## What This Library Does | 这个资料库在做什么

Project Covenant reads Scripture as one connected story: creation, fall, covenant, kingdom, exile, promise, Christ, church, and new creation. It combines biblical theology, historical context, manuscripts, and archaeology while distinguishing what each kind of evidence can—and cannot—show.<br>
Project Covenant 把圣经读成一条连贯的故事线：创造、堕落、圣约、国度、被掳、应许、基督、教会与新创造。资料库同时使用圣经神学、历史语境、抄本和考古材料，并清楚区分每类证据能支持什么、不能支持什么。

<a id="how-this-library-is-made"></a>
## How This Library Is Made | 资料库如何编写

AI assists with drafting, organizing, and translating this library. Sermon notes are summaries based on sermon content; supplemental studies and editorial inferences must be identified as such. Each major content page begins with a review status. AI assistance and automated checks do not establish historical accuracy, quotation permission, or human review.<br>
本资料库由 AI 辅助起草、整理和翻译。讲道笔记依据讲道内容整理；补充查考与编辑推论须明确说明。每个主要内容页开头标注审阅状态。AI 辅助与自动检查不能证明史料准确、引文已获许可或内容已经人工审阅。

| Status / 状态 | Meaning / 含义 |
| --- | --- |
| Draft | AI draft; not human reviewed. / AI 草稿，未人工审阅。 |
| Reviewed | Human reviewed; assigned only after an actual human review. / 已人工审阅，仅在完成人工审阅后标注。 |

All major content pages in this cleanup remain Draft. Language coverage and technical privacy checks are separate from this content-review status. Historical statements marked “Pending verification / 待核实” remain unresolved.<br>
本次整理的主要内容页全部保留 Draft。语言覆盖程度、技术隐私检查与内容审阅状态分别记录。标为“待核实”的历史说法仍未解决。

<a id="bilingual-reading-status"></a>
## Bilingual Reading Status | 双语阅读状态

| Content / 内容 | English status / 英文状态 | Chinese status / 中文状态 |
| --- | --- | --- |
| Main entry points and core timeline guides / 主要入口与核心时间线导读 | English/Chinese body text paired as Draft; reading aids continue to improve | 中英正文已配对为Draft；阅读辅助仍在完善 |
| Sermon and fellowship notes / 讲道与团契笔记 | Existing English/Chinese note text paired as Draft; source verification remains separate | 现有笔记中英正文已配对为Draft；来源核实另行记录 |
| Book-study guides / 书籍导读 | Paired English/Chinese Draft text; edition questions remain flagged | 中英草稿正文已配对；版本问题继续保留标注 |
| Historical, archaeological, and manuscript research dossiers / 历史、考古与抄本研究专题 | Paired English/Chinese Draft text; human review pending | 中英逐段配对Draft正文；待人工审阅 |

The current approved pages have paired Draft text. Human review is still needed for translation, interpretation, and sources; paragraph pairing does not establish accuracy.<br>
当前获准页面已配对为Draft正文。翻译、解释与来源仍需人工审阅；逐段配对并不证明内容准确。

<a id="research-boundaries"></a>
## Research Boundaries | 研究边界

Historical and archaeological materials can illuminate people, places, institutions, texts, and historical settings. They do not automatically prove every narrative detail, authorial claim, miracle, or theological conclusion. Each research file therefore records both **what a source can support** and **where interpretation must stop**.<br>
史料与考古可以照明人物、地点、制度、文本与历史处境，却不会自动证明每一项叙事细节、作者传统、神迹或神学结论。因此每份研究稿都同时记录“材料能支持什么”与“解释必须停在哪里”。

<a id="privacy-and-publication"></a>
## Privacy and Publication | 隐私与发布

Page content does not include the maintainer's personal experiences, testimony, church attendance records, or contact information. The other privacy restrictions, including sensitive personal records and identifiable private anecdotes, still apply. Source churches are described generically, without their names, websites, or meeting details. Raw transcripts and private downloads are not public reading material.<br>
页面内容不包含维护者的个人经历、见证、聚会出席记录和联系方式。其他隐私限制仍然适用，包括敏感个人记录及可识别的私人轶事。来源教会只以泛称描述，不写名称、网址或聚会细节。原始逐字稿和私人下载文件不属于公开阅读内容。

See [Privacy and Publication Policy | 隐私与发布政策](./PUBLICATION_POLICY.md) for the review rules and the website's publication boundary.<br>
审核规则与网站的发布边界，见 [Privacy and Publication Policy | 隐私与发布政策](./PUBLICATION_POLICY.md)。

A deterministic, Git-history-free content snapshot can be generated for the website or for a clean repository import. This removes repository history from the transferred files, but it does not anonymize the GitHub account that publishes them.<br>
项目可以为网站或干净仓库导入生成可重现、不带 Git 历史的内容快照。这会去掉待转移文件中的仓库历史，但不会匿名化发布它们的 GitHub 账号。

The reviewed snapshot can also be rendered as a deterministic static reading site: one HTML page for every approved Markdown page and one local stylesheet plus approved local maps and illustrations. Its only script is a local language switch (中文 / EN / 中英) that makes no network request and remembers the reader's choice in the browser; the site contains no analytics, forms, comments, remote images, remote fonts, source maps, Git history, or publication manifests. Building the files does not deploy them or make the hosting account anonymous.<br>
经过复核的快照还可以生成可重现的静态阅读网站：每份获准 Markdown 对应一个 HTML 页面，另加一份本地样式表及获准的本地地图与插画。站点唯一的脚本是本地语言切换（中文／EN／中英），它不联网，只在浏览器中记住读者的选择；站点不包含分析追踪、表单、评论、远程图片、远程字体、source map、Git 历史或发布清单。生成文件不等于已经部署，也不会自动匿名化托管账号。

<a id="build-and-offline-reading"></a>
## Build and Offline Reading | 构建与离线阅读

After creating and verifying a clean publication snapshot, build the static site and then create a byte-verifiable offline ZIP from that same snapshot. Do not ZIP the repository or an independently edited site directory.<br>
先生成并验证干净发布快照，再从同一份快照构建静态站点和可逐字节验证的离线 ZIP。不要直接压缩整个仓库，也不要压缩另行编辑过的站点目录。

```bash
python3 scripts/build_static_site.py build \
  --snapshot /tmp/project-covenant-public \
  --expected-content-set-sha256 DIGEST_FROM_EXPORT \
  --output /tmp/project-covenant-site

python3 scripts/build_static_site.py verify \
  --snapshot /tmp/project-covenant-public \
  --expected-content-set-sha256 DIGEST_FROM_EXPORT \
  --input /tmp/project-covenant-site

python3 scripts/package_offline_site.py create \
  --snapshot /tmp/project-covenant-public \
  --expected-content-set-sha256 DIGEST_FROM_EXPORT \
  --output /tmp/project-covenant-offline.zip

python3 scripts/package_offline_site.py verify \
  --snapshot /tmp/project-covenant-public \
  --expected-content-set-sha256 DIGEST_FROM_EXPORT \
  --input /tmp/project-covenant-offline.zip
```

To read without GitHub or a web server, extract the ZIP and open `project-covenant-offline/index.html` in a browser. The package contains only the approved HTML pages, local CSS, the local language-switch script, maps, and illustrations; it contains no Git history, analytics, forms, remote assets, source manifest, or build metadata.<br>
若要脱离 GitHub 和网页服务器阅读，请解压 ZIP，然后在浏览器中打开 `project-covenant-offline/index.html`。离线包只包含获准的 HTML 页面、本地 CSS、本地语言切换脚本、地图和插画，不包含 Git 历史、分析追踪、表单、远程资源、源白名单或构建元数据。

The current release tools require a POSIX system. Before placing the files on any public host, follow [Static Mirror Deployment | 静态镜像部署](./STATIC_MIRROR_DEPLOYMENT.md); the reading site is currently published with GitHub Pages from this repository.<br>
当前发布工具要求 POSIX 系统。把文件放到任何公开托管服务之前，请遵循[静态镜像部署](./STATIC_MIRROR_DEPLOYMENT.md)；阅读网站目前由本仓库通过 GitHub Pages 发布。

<a id="library-map"></a>
## Library Map | 资料结构

```text
Project-Covenant/
├── README.md                  # Bilingual project entry | 双语项目入口
├── ABOUT.md                   # About, review status, and build notes | 关于、审阅状态与构建说明
├── LICENSE.md                 # Content and software license map | 内容与软件授权总览
├── LICENSE-CODE               # Canonical MIT software license | MIT 软件许可标准文本
├── CONTRIBUTING.md            # Bilingual writing and source rules | 双语写作与来源规则
├── PUBLICATION_POLICY.md       # Privacy and publication boundary | 隐私与发布边界
├── STATIC_MIRROR_DEPLOYMENT.md # Provider-neutral mirror checklist | 与托管商无关的镜像清单
├── publication/
│   └── site-content.txt        # Exact future-site allowlist | 未来网站精确白名单
├── Bilingual_Notes/
│   ├── README.md              # Notes hub | 笔记中心
│   ├── INDEX_Chronological.md # Chronological note index | 时间索引
│   └── *.md                   # Sermon and fellowship notes | 讲道与团契笔记
├── Book_Studies/
│   ├── README.md              # Christian book-study hub | 基督教书籍研读导航
│   └── *.md                   # Book guides and critical reading maps | 书籍导读与批判性阅读地图
├── Christian_Traditions/
│   ├── README.md              # Christian terminology hub | 基督教术语导航
│   └── *.md                   # Denominations and theological terms | 宗派与神学术语
├── archive/                   # Unmaintained historical topics | 不再维护的旧专题
├── docs/maintenance/          # Snapshot, review, and validation records | 存档、审查及验证记录
├── Bible_Translations/
│   ├── README.md              # Translation-access hub | 圣经译本获取导航
│   └── *.md                   # Access guides and reading profiles | 获取指南与阅读定位
└── Bible_Timeline/
    ├── README.md              # Research hub | 研究导航
    ├── *_Bilingual.md         # Fully bilingual core guides | 核心双语导读
    ├── 52周_*.md / 52卷_*.md   # One-year route and book profiles | 年度路线与逐卷画像
    ├── 史料与考古旁证索引.md    # Evidence index | 史料与考古索引
    └── *_背景与证据边界.md      # Chinese research dossiers with English navigation | 中文研究专题及英文导航
```

<a id="licensing"></a>
## Licensing | 授权说明

Original study guides and explanatory content are available under `CC BY-NC-SA 4.0`; repository scripts, tests, and workflow code use the MIT License. These licenses do not cover third-party Bible translations, published books, quotations, images, transcripts, or other material that Project Covenant contributors do not own. See [Licensing | 授权说明](./LICENSE.md) for the exact scope.<br>
原创研读指南和解释性内容采用 `CC BY-NC-SA 4.0`；仓库脚本、测试和工作流代码采用 MIT License。上述许可证不涵盖第三方圣经译本、已出版书籍、引文、图片、逐字稿或其他 Project Covenant 贡献者并不拥有权利的材料。准确范围见[授权说明](./LICENSE.md)。

<a id="contributing"></a>
## Contributing | 参与整理

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before adding or translating material. It explains the bilingual format, source discipline, naming conventions, and how to avoid overstating historical evidence.<br>
新增、翻译或修订资料前，请阅读[CONTRIBUTING.md](./CONTRIBUTING.md)。其中说明双语格式、来源纪律、命名方式，以及如何避免夸大历史证据。

[Back to Project Covenant | 返回项目首页](./README.md)
