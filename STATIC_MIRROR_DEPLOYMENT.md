# Static Mirror Deployment | 静态镜像部署

> This page is a provider-neutral release checklist for a GitHub-independent reading mirror. It does not mean that a public mirror has already been deployed.<br>
> 本页是一份与托管商无关的发布清单，用于建立可脱离 GitHub 阅读的静态镜像；它不表示公开镜像已经完成部署。

<a id="reading-route"></a>
## Reading Route | 阅读路线

- [Current status | 当前状态](#current-status)
- [Exact publication boundary | 精确发布边界](#exact-publication-boundary)
- [Host requirements | 托管要求](#host-requirements)
- [Recommended response headers | 建议响应头](#recommended-response-headers)
- [Release sequence | 发布顺序](#release-sequence)
- [Live acceptance checks | 线上验收](#live-acceptance-checks)
- [Mainland China access boundary | 中国境内访问边界](#mainland-china-access-boundary)
- [Update and rollback | 更新与回滚](#update-and-rollback)
- [Completion rule | 完成判定](#completion-rule)

<a id="current-status"></a>
## Current Status | 当前状态

Project Covenant can produce a deterministic static site and a byte-verifiable offline ZIP from the reviewed publication snapshot. The offline ZIP can be read after extraction without GitHub or a web server. No external hosting provider, domain, account, or live mirror is configured by this repository.<br>
Project Covenant 已能从经过复核的发布快照生成可重现的静态站点和可逐字节验证的离线 ZIP。离线包解压后无需 GitHub 或网页服务器即可阅读。本仓库目前没有配置外部托管商、域名、托管账号或在线镜像。

<a id="exact-publication-boundary"></a>
## Exact Publication Boundary | 精确发布边界

Publish only the files produced by `scripts/build_static_site.py` from the same verified snapshot and retained content-set digest. Never upload the repository, `.git`, a recursively copied working tree, a separately edited site directory, or files outside the exact allowlist recorded in `publication/site-content.txt`.<br>
只能发布由 `scripts/build_static_site.py` 使用同一份已验证快照及另行保存的内容集摘要生成的文件。不得上传整个仓库、`.git`、递归复制的工作区、另行编辑过的站点目录，或 `publication/site-content.txt` 精确白名单以外的文件。

The first mirror must remain static and script-free. It must not add analytics, comments, forms, cookies, remote fonts, remote images, source maps, injected advertising, or links that expose an identifying maintenance account.<br>
初版镜像必须保持纯静态且不含脚本，不得加入分析追踪、评论、表单、Cookie、远程字体、远程图片、source map、注入式广告，或暴露可识别维护账号的链接。

<a id="host-requirements"></a>
## Host Requirements | 托管要求

Use a host that serves the extracted site over HTTPS, preserves every generated path exactly, supports custom response headers, does not inject JavaScript or advertisements, and permits a complete export or deletion of the deployment. Review the provider account name, billing contact exposure, domain registration, access logs, and public project metadata separately from the site files.<br>
应选择能够通过 HTTPS 提供解压后站点、完整保留生成路径、支持自定义响应头、不注入 JavaScript 或广告，并允许完整导出或删除部署的托管服务。托管账号名称、账单联系信息暴露、域名注册、访问日志和公开项目元数据必须与站点文件分开复核。

<a id="recommended-response-headers"></a>
## Recommended Response Headers | 建议响应头

The generated pages need only same-origin CSS. A compatible baseline policy is shown below. Header syntax and support must be tested on the selected live host; placing `frame-ancestors` in an HTML meta tag is not equivalent to sending it as an HTTP response header.<br>
生成页面只需要加载同源 CSS。下面给出一组兼容的基线策略；选定托管服务后，必须在实际线上响应中测试语法和支持情况。把 `frame-ancestors` 写入 HTML meta 标签，不等同于通过 HTTP 响应头发送它。

```text
Content-Security-Policy: default-src 'none'; style-src 'self'; img-src 'none'; font-src 'none'; script-src 'none'; connect-src 'none'; object-src 'none'; frame-src 'none'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Enable `Strict-Transport-Security` only after HTTPS works correctly for the intended domain and every affected subdomain. Do not copy an `includeSubDomains` policy onto a domain whose other subdomains have not been reviewed.<br>
只有在目标域名及所有受影响子域名都已正确使用 HTTPS 后，才启用 `Strict-Transport-Security`。如果其他子域名尚未复核，不要直接在该域名上套用带有 `includeSubDomains` 的策略。

<a id="release-sequence"></a>
## Release Sequence | 发布顺序

1. Commit the intended public changes and start from a fresh, reviewed, clean checkout. / 提交预定公开修改，并从全新、经过复核且干净的 checkout 开始。
2. Run the tests and publication audits listed in [`PUBLICATION_POLICY.md`](./PUBLICATION_POLICY.md), including the Git-history content audit. / 运行 [`PUBLICATION_POLICY.md`](./PUBLICATION_POLICY.md) 列出的测试与发布审计，包括 Git 历史内容审计。
3. Export and independently verify the publication snapshot; retain its content-set SHA-256 through a trusted channel. / 导出并独立验证发布快照，通过可信渠道另行保存其内容集 SHA-256。
4. Build and verify the static site from that exact snapshot and digest. / 从这份完全相同的快照和摘要构建并验证静态站点。
5. Upload only the just-built site files in the same trusted release job, without post-build rewriting or provider injection. / 在同一可信发布任务中只上传刚刚生成的站点文件，不得在构建后改写，也不得接受托管商注入内容。
6. Test the live pages, headers, links, privacy boundary, and representative rendered pages before announcing the mirror. / 宣布镜像之前，检查线上页面、响应头、链接、隐私边界及代表性页面的实际渲染。

<a id="live-acceptance-checks"></a>
## Live Acceptance Checks | 线上验收

Check the homepage, at least one deep timeline page, the book-study hub, and the licensing page. Confirm that internal links still work at their final paths, that no request goes to an unapproved external asset, and that the browser receives no script, form, analytics beacon, tracking cookie, or identifying repository link.<br>
至少检查首页、一份深层时间线页面、书籍研读导航和授权说明页。确认内部链接在最终路径下仍可使用，没有请求访问未经批准的外部资源，并且浏览器没有收到脚本、表单、分析信标、追踪 Cookie 或指向可识别源仓库的链接。

```bash
curl --fail --silent --show-error --location --output /dev/null https://MIRROR.example/
curl --fail --silent --show-error --dump-header - --output /dev/null https://MIRROR.example/
curl --fail --silent --show-error --location --output /dev/null https://MIRROR.example/Book_Studies/
```

Record the tested URL, UTC time, deployed content-set digest or offline-package SHA-256, response headers, and reviewer. A successful build or upload is not evidence that the live mirror passed these checks.<br>
记录被测网址、UTC 时间、已部署的内容集摘要或离线包 SHA-256、响应头及复核人。构建或上传成功，并不能证明线上镜像已经通过这些检查。

<a id="mainland-china-access-boundary"></a>
## Mainland China Access Boundary | 中国境内访问边界

Do not describe a mirror as “accessible in mainland China” merely because it works elsewhere. Accessibility can vary by network, region, DNS, domain, hosting provider, and time. Test the final HTTPS domain from multiple ordinary mainland networks and repeat the checks over time; record failures and partial loading as failures, not as successful access.<br>
不要因为镜像在其他地区可以打开，就把它写成“在中国境内可访问”。可访问性会随网络、地区、DNS、域名、托管商和时间而变化。应从多个普通中国境内网络实测最终 HTTPS 域名，并持续复测；打不开或只加载一部分都应记录为失败，而不是成功访问。

Hosting, domain, content-service, filing, and other regulatory duties depend on the selected jurisdiction and provider. This repository does not determine legal eligibility or replace provider and legal review. Do not collect reader identities, prayer requests, testimonies, or contact details until a separate privacy, security, and legal review has approved that feature.<br>
托管、域名、内容服务、备案及其他监管义务取决于所选司法辖区与服务商。本仓库不能判断法律资格，也不能替代服务商与法律复核。在单独的隐私、安全和法律审查批准之前，不得收集读者身份、代祷事项、见证或联系方式。

<a id="update-and-rollback"></a>
## Update and Rollback | 更新与回滚

Treat every update as a new immutable release: rebuild from a reviewed commit, rerun all checks, retain the new digest, and keep the prior verified artifact available for rollback. Roll back by redeploying a previously verified complete artifact, never by mixing files from two releases.<br>
每次更新都应视为一个新的不可变发布：从经过复核的提交重新构建，重新运行全部检查，保存新的摘要，并保留上一份已验证产物以供回滚。回滚时应重新部署一份以前完整验证过的产物，不能混用两个版本的文件。

<a id="completion-rule"></a>
## Completion Rule | 完成判定

The offline package is complete when its exact bytes verify against the reviewed snapshot. A hosted mirror is complete only after the selected provider, account and domain have been reviewed, the exact artifact has been deployed, representative pages have been inspected, and live response headers and access have been recorded. Until then, describe the mirror as deployment-ready, not deployed.<br>
离线包只有在其全部字节与经过复核的快照验证一致后才算完成。在线镜像只有在选定托管商、账号和域名经过复核，精确产物已经部署，代表性页面已经查看，线上响应头和访问结果已经记录后才算完成。在此之前，只能称为“已具备部署条件”，不能称为“已经部署”。

[Back to Project Home | 返回项目首页](./README.md)
