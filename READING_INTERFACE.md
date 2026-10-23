# Reading Interface | 阅读界面

> Status: Draft (AI draft; not human reviewed) | 状态：Draft（AI 草稿，未人工审阅）

The static site now presents the approved study library as a book-style reading interface. The existing export, build, verification, and offline-package commands remain unchanged.

静态站点现在以读书式界面呈现经过审核的研读资料库。现有导出、构建、验证和离线打包命令保持不变。

## Reading Features | 阅读功能

The home page is a reader landing page: a short introduction, a start button, topic-guide cards, and the library index. Maintenance material lives on the About page. Reading pages use one centered column with the collection links in the top bar, an outline derived from actual rendered heading IDs at the side, and previous/next documents plus the full collection list at the end. On small screens, native expandable menus replace the top links and the outline.

首页是面向读者的落地页：简短介绍、开始阅读按钮、专题导读卡片和资料索引；维护类内容放在“关于本资料库”页面。阅读页使用居中单栏，栏目链接放在顶部，侧边显示根据正文真实标题锚点生成的页内目录，文末提供上一篇、下一篇和本栏全部篇目。小屏幕使用浏览器原生折叠菜单替代顶部链接和页内目录。

Every article starts with the same header: collection and position, title, the page's own summary, and one meta line with a small review-status badge and the reading time. The site moves or drops only repeated reading aids that the Markdown keeps for GitHub: the review-status quote becomes the badge; a “fully bilingual” language-status box is dropped, and other language-status notes move into an expandable editorial note at the end; a route table that only links to sections of the same page is dropped because the outline replaces it; the per-image “original illustration” line is replaced by one footer note; and a final row of “Back to …” links is replaced by the previous/next navigation. Every anchor ID those blocks carried is kept, so existing links still work.

每篇文章使用统一的开头：栏目与位置、标题、本篇摘要，以及一行包含审阅状态小标签和阅读时间的信息。网站只移动或省略 Markdown 为 GitHub 保留的重复阅读辅助：审阅状态引用框改为小标签；“完整双语”的语言状态框省略，其他语言状态说明移到文末可展开的整理说明；只链接本页小节的路线表由页内目录取代；每张插图下的“原创插画”说明改为页脚统一说明；文末的“返回……”链接行由上一篇／下一篇导航取代。这些区块原有的锚点 ID 全部保留，旧链接仍然有效。

The design includes system-following dark mode, keyboard focus indicators, a skip-to-content link, reduced-motion support, horizontally scrollable tables, and print styles. Credited maps and public-domain illustrations are local files; no remote fonts, images, or runtime dependencies are added.

界面提供跟随系统的深色模式、键盘焦点标识、跳到正文链接、减少动态效果支持、可横向滚动的表格，以及打印样式。地图与公有领域插画以本地文件加载并保留署名；不增加远程字体、图片或运行时依赖。

The number above a document is its position in the current collection, not a record of what the reader has finished. The site does not store progress or bookmarks. Browser bookmarks can retain a document or heading URL.

文章上方的数字表示它在当前栏目中的位置，不是读者已经完成的进度。站点不保存阅读进度或书签；浏览器书签可以保存文章或小节网址。

## Reading Estimates and Print Layout | 阅读时间与打印版式

Long articles receive a short bilingual reading-time estimate (“5 min read | 约 5 分钟”) in the article header. The static builder uses 200 English words or 350 Chinese characters per minute, takes the longer language estimate, and rounds up. It omits estimates below three minutes except on study pages. These are rough reading aids, excluding linked Bible passages, study, and reflection; they do not measure an individual reader. / 长文在文章开头显示简短的双语阅读时间（“5 min read | 约 5 分钟”）。静态构建按每分钟200个英文词或350个汉字，取两种语言较长的估计并向上取整；除研读页外，不足三分钟不显示。这只是粗略提示，不包含另开的经文、研读和思考，也不衡量个别读者。

The reading column is capped at 42rem; body text is 17px with a 1.85–1.9 line height, and in side-by-side mode each language starts on its own line. Wide two-column tables scroll within their own regions; tables with three or more columns become labeled cards on phones. Maps and illustrations shrink to the available width. Print styles hide navigation and introductory controls and constrain images to fit the page. One local reading script supplies the controls described below; no remote font is added. / 正文最大宽度为42rem；正文字号17px、行高1.85–1.9；中英对照模式下两种语言各自另起一行。较宽的两列表格在自身区域横向滚动；三列及以上的表格在手机上按行显示为带字段名的卡片。地图和插画均适应可用宽度。打印时隐藏导航与入口控件，并限制图片高度以适合纸张。下文的交互由同一个本地阅读脚本提供，不增加远程字体。

## Long Reading and Figures | 长文与图像

Articles estimated at twenty minutes or more group third-level entries into expandable sections. The year plan keeps its six parts in the outline and folds each of its 52 weeks separately. Original heading and alias IDs remain intact. A deep link opens its containing section automatically; “Expand all” supports continuous reading and text search. All sections are open without JavaScript and when printing. The outline highlights the current section, and a floating link returns to the article opening. This position is only an aid for the current page, not saved reading progress.

预计二十分钟以上的文章将三级条目整理为可展开的小节。全年计划在目录中保留六大部，52 周分别折叠。原标题与别名锚点全部保留；深层链接会自动展开所在小节。“展开全文”便于连续阅读和全文查找。禁用 JavaScript 或打印时，所有小节均展开。目录高亮当前章节，并提供悬浮返回页首链接。章节位置只是当前页面的阅读提示，不保存阅读进度。

The outline uses Chinese in bilingual mode and follows English or Chinese in single-language mode. Full bilingual headings remain in the article. Headings use the same system sans-serif family as the text, with a lighter weight and separate lines for simple paired titles. Notes, book guides, maps, and the glossary share this hierarchy.

中英模式的目录使用中文，单语言模式则跟随所选语言；正文仍保留完整双语标题。标题与正文使用同一系统无衬线字体族，减轻字重，简单的双语标题分行排列。笔记、书籍导读、地图与词汇表共用这一层级。

Maps fit the reading column in full. The image and its caption link to the verified local SVG for enlargement; adjacent explanations and source credits stay together beneath the image. No image service, modal dependency, or external asset is added. Mobile table cards repeat column names visually while retaining the original table and header cells for assistive technology. Two-column tables retain a keyboard-focusable scrolling region and a visible scrolling hint.

地图默认完整适应文章栏，图片与图注均可打开经过验证的本地 SVG 大图；说明和来源署名集中在图下。不增加图片服务、弹窗依赖或外部素材。手机表格卡片重复显示字段名，同时保留原始表格及表头供辅助技术读取。两列表格保留可用键盘聚焦的横向滚动区域和可见的滑动提示。

The HTML policy adds only `figure` and `figcaption` with optional classes, `details open="open"`, a table-region `tabindex="0"`, and two fixed reader button actions (`expand` and `collapse`). It still rejects unknown actions, conflicting language/action buttons, inline handlers, arbitrary attributes, empty image alt text, and unverified assets. The CSP is unchanged. Only the language preference is stored; section state and reading position are not persisted.

HTML 策略只增加可带 class 的 `figure`、`figcaption`，`details open="open"`，表格区域的 `tabindex="0"`，以及固定的 `expand`、`collapse` 两种阅读按钮操作。仍拒绝未知操作、冲突的语言与阅读操作按钮、内联事件、任意属性、空图片替代文字及未经验证的素材。CSP 不变。只保存语言偏好，不保存小节展开状态或阅读位置。

## Content and Safety | 内容与安全

Original Markdown, body text, citations, filenames, and publication permissions are unchanged; only the repeated reading aids listed above are moved or dropped in the rendered page. Navigation can only target pages present in the verified allowlist. Major headings are preferred for long-page outlines; third-level headings are used when there are no major headings.

原有 Markdown、正文、引文、文件名及发布权限均不改变；渲染页面只移动或省略上文列出的重复阅读辅助。导航只能指向已验证白名单中存在的页面。长文目录优先显示二级标题；没有二级标题时使用三级标题。

The output still contains exactly one HTML file per approved Markdown page and one local stylesheet plus approved local maps and illustrations. Only the generated local reading script is allowed; inline and third-party scripts, tracking, forms, comments, remote assets, and source-repository links remain prohibited. The layout does not imply that untranslated source material is fully bilingual.

输出仍然严格对应为每份获准 Markdown 一个 HTML 文件，以及一份本地样式表及获准本地地图与插画。只允许生成的本地阅读脚本；继续禁止内联及第三方脚本、追踪、表单、评论、远程资源及源仓库链接。界面不会把尚未翻译的来源材料标成完整双语。

## Verification and Preview | 验证与预览

Run the full regression suite and repository audits before export:

导出前运行完整回归测试和仓库审计：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_markdown.py
python3 scripts/audit_publication.py
python3 scripts/audit_publication.py --history-content
git diff --check
```

Use the existing commands in the [build instructions](./README.md) and the [deployment checklist](./STATIC_MIRROR_DEPLOYMENT.md). Export from a reviewed committed ref, retain the content-set digest, and verify both the site and offline ZIP against that same snapshot.

使用现有[构建说明](./README.md)与[部署清单](./STATIC_MIRROR_DEPLOYMENT.md)中的命令。从复核后的已提交版本导出，另行保留内容集摘要，并对照同一快照验证站点和离线 ZIP。

A successful Publication Guard run attaches the verified offline ZIP as a short-lived reading preview. Download and extract the artifact, then extract the inner ZIP and open its index page. This is a review artifact, not an automatically deployed public website.

Publication Guard 成功运行后，会附上经过验证的离线 ZIP，作为短期保留的阅读预览。下载并解压构件后，再解压内部 ZIP，打开其首页即可。这是审核用构件，不是自动部署的公开网站。

## Browser Regression Checks | 浏览器回归检查

The publication workflow also runs Chromium against the unchanged verified site through actual file URLs and a temporary loopback HTTP server. Every page is checked at 320, 390, 768, 1024, and 1440 pixel widths for stylesheet loading, document overflow, and reader structure. Mobile menus are opened and closed by keyboard on every page that contains them.

发布验证流程还会使用 Chromium，通过真实文件网址和临时本机 HTTP 服务检查未经修改的已验证站点。每页均检查 320、390、768、1024 和 1440 像素宽度下的样式加载、页面溢出和阅读结构；每页存在的手机目录都会通过键盘展开与收起。

Representative interactions cover starting a reading route, previous/next round trips, heading links, back-to-top, keyboard skip links, system dark mode, reduced motion, and print navigation hiding. Screenshots and a JSON result are retained separately from the reading package. These checks are not an assertion that every external source is reachable or that a public host has been deployed and reviewed.

代表性交互检查包括开始阅读、前后篇往返、小节链接、返回页首、键盘跳到正文、系统深色模式、减少动态效果和打印时隐藏导航。截图与 JSON 结果独立于阅读包保存。这些检查不表示每个外部来源都可访问，也不表示已经部署并复核公开托管网站。

Playwright is pinned as a development-only dependency; it is not shipped in the generated site. The browser check leaves the site files and its strict content security policy unchanged and rejects unexpected remote requests. It serves only the generated output, not the maintenance repository.

Playwright 固定版本且仅作为开发验证依赖，不会随生成站点发布。浏览器检查不修改站点文件或严格内容安全策略，并拒绝意外的远程请求。临时服务只提供生成产物，不提供维护仓库。

[Back to project entry | 返回项目入口](./README.md)
