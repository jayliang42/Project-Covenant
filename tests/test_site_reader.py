from __future__ import annotations

import tempfile
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from scripts import build_static_site, site_reader


class ParsedPage(HTMLParser):
    def __init__(self, document: str):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.feed(document)
        self.close()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append((tag, values))
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and "href" in values:
            self.links.append(values["href"])


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            "README.md": "Home | 首页",
            "Bible_Timeline/README.md": "Storyline | 故事线",
            "Bible_Timeline/First_Steps_Bilingual.md": "First Steps | 第一步",
            "Bible_Timeline/Bible_Timeline_Bilingual.md": "Overview | 总览",
            "Bible_Timeline/研究 甲.md": "Research A | 研究甲",
            "Bible_Timeline/研究 乙.md": "Research B | 研究乙",
            "Book_Studies/README.md": "Book studies | 书籍研读",
            "Book_Studies/guide.md": "Guide | 指南",
            "LICENSE.md": "Licensing | 授权",
        }
        self.mapping = {
            source: str(PurePosixPath(source).with_name("index.html"))
            if source.endswith("README.md") else str(PurePosixPath(source).with_suffix(".html"))
            for source in self.sources
        }
        self.body = '<h1 id="guide">Guide | 指南</h1>\n<h2 id="start-开始">Start | 开始</h2><p>Body &amp; sources. | 正文与来源。</p>'

    def render(self, source="Bible_Timeline/First_Steps_Bilingual.md", body=None, mapping=None, titles=None):
        mapping = self.mapping if mapping is None else mapping
        titles = self.sources if titles is None else titles
        return site_reader.render_page(source, mapping[source], titles[source], self.body if body is None else body, mapping, titles, "assets/site.css").decode()

    def test_outline_uses_real_ids_and_nested_inline_text(self):
        headings = site_reader.outline('<h2 id="stable"><strong>One</strong> &amp; <em>Two</em><br>中文</h2>')
        self.assertEqual([site_reader.Heading("stable", "One & Two 中文", 2)], headings)

    def test_outline_supports_explicit_anchor_without_heading_id(self):
        headings = site_reader.outline('<a id="explicit"></a>\n<h2>Title | 标题</h2>')
        self.assertEqual("explicit", headings[0].identifier)

    def test_outline_prefers_heading_id_to_preceding_anchor(self):
        headings = site_reader.outline('<a id="alias"></a><h2 id="actual">Title</h2>')
        self.assertEqual("actual", headings[0].identifier)

    def test_outline_does_not_reuse_stale_anchor(self):
        self.assertEqual([], site_reader.outline('<a id="old"></a><p>Text</p><h2>No ID</h2>'))

    def test_outline_prefers_major_sections_without_truncation(self):
        body = ''.join(f'<h2 id="s{i}">Section {i}</h2><h3 id="x{i}">Subsection</h3>' for i in range(120))
        headings = site_reader.outline(body)
        self.assertEqual(120, len(headings))
        self.assertTrue(all(item.level == 2 for item in headings))

    def test_outline_falls_back_to_h3_and_ignores_code(self):
        self.assertEqual([site_reader.Heading("sub", "Subsection", 3)], site_reader.outline('<pre>&lt;h2 id="fake"&gt;Code&lt;/h2&gt;</pre><h3 id="sub">Subsection</h3>'))

    def test_toc_keeps_chinese_place_names_with_latin_names_visible(self):
        toc = site_reader._toc('<h2 id="jericho">5.1 Jericho / Tell es-Sultan | 5.1 耶利哥／Tell es-Sultan</h2>')
        self.assertIn('<span class="l-zh" lang="zh-Hans">5.1 耶利哥／Tell es-Sultan</span>', toc)
        self.assertIn('<span class="l-en" lang="en">5.1 Jericho / Tell es-Sultan</span>', toc)

    def test_no_toc_when_document_has_no_linkable_sections(self):
        page = self.render(body='<h1>Guide</h1><p>Text</p>')
        self.assertNotIn('class="reader-toc"', page)
        self.assertNotIn('class="mobile-toc"', page)

    def test_title_moves_into_reading_header_and_body_follows_untouched(self):
        page = self.render()
        self.assertIn('<header class="article-header">', page)
        self.assertIn('<h1 id="guide">Guide | 指南</h1>\n', page)
        self.assertLess(page.index('<h1 id="guide">'), page.index('</header>\n<details class="mobile-toc">'))
        self.assertIn('<h2 id="start-开始">Start | 开始</h2><p>Body &amp; sources. | 正文与来源。</p>\n</article>', page)

    def test_body_without_title_is_preserved_byte_for_byte(self):
        body = '<h2 id="start-开始">Start | 开始</h2><p>Body.</p>'
        page = self.render(body=body)
        self.assertIn('</header>\n<details class="mobile-toc">', page)
        self.assertIn('</details>\n' + body + '\n</article>', page)

    def test_status_route_caption_and_back_links_are_reshaped_but_ids_survive(self):
        body = (
            '<a id="top" class="anchor" aria-hidden="true"></a>\n'
            '<blockquote>\n<p><span class="l-en" lang="en">Status: Draft (AI draft; not human reviewed)</span>'
            '<span class="l-sep"> | </span><span class="l-zh" lang="zh-Hans">状态：Draft（AI 草稿，未人工审阅）</span></p>\n</blockquote>\n'
            '<h1 id="guide">Guide | 指南</h1>\n'
            '<a id="in-three-sentences" class="anchor" aria-hidden="true"></a>\n'
            '<blockquote>\n<p><span class="l-bi"><strong>In Three Sentences | 三句话读懂本篇</strong></span></p>\n<p>Summary. | 摘要。</p>\n</blockquote>\n'
            '<blockquote>\n<p>Language status | 语言状态: Fully bilingual, paragraph by paragraph.</p>\n<p>语言状态 | Language status：全文按段落提供中英双语。</p>\n</blockquote>\n'
            '<p><img class="study-art" src="../assets/art/x.svg" alt="Art | 插画"></p>\n'
            '<p><em>Original illustration for this library; not historical evidence. / 本资料库原创插画，不作为历史证据。</em> '
            '<a href="../CREDITS.html#original-illustrations">About the illustrations | 插画说明</a></p>\n'
            '<a id="route-guide" class="anchor" aria-hidden="true"></a>\n'
            '<h2 id="route-guide-路线导航">Route Guide | 路线导航</h2>\n'
            '<div class="table-scroll">\n<table><tbody><tr><td><a href="#start-开始">Start</a></td></tr></tbody></table>\n</div>\n'
            '<h2 id="start-开始">Start | 开始</h2>\n<p>Body.</p>\n'
            '<p><a href="../index.html">Back to Project Covenant | 返回项目首页</a> · <a href="index.html">Back to the hub | 返回导航</a></p>\n'
        )
        page = self.render(body=body)
        article = page[page.index('<article'):page.index('</article>')]
        self.assertIn('<span class="status-badge">Draft</span>', article)
        self.assertIn('AI draft; not human reviewed', article)
        self.assertNotIn('Status: Draft', article)
        self.assertIn('<div class="lede">', article)
        self.assertIn('<p class="lede-label">', article)
        self.assertNotIn('Fully bilingual', article)
        self.assertNotIn('Original illustration', article)
        self.assertNotIn('Route Guide', article)
        self.assertNotIn('Back to Project Covenant', article)
        self.assertIn('class="study-art"', article)
        for identifier in ('top', 'in-three-sentences', 'route-guide', 'route-guide-路线导航', 'start-开始'):
            self.assertIn(f'id="{identifier}"', article)

    def test_route_table_that_links_elsewhere_is_kept(self):
        body = ('<h1 id="guide">Guide | 指南</h1>\n<a id="route-guide" class="anchor" aria-hidden="true"></a>\n'
                '<h2 id="route-guide">Route Guide | 路线导航</h2>\n<div class="table-scroll">\n'
                '<table><tbody><tr><td><a href="../Glossary/index.html">Glossary</a></td></tr></tbody></table>\n</div>\n')
        self.assertIn('Route Guide | 路线导航', self.render(body=body))

    def test_partial_language_status_moves_to_end_note_without_losing_the_boundary(self):
        body = ('<h1 id="guide">Guide | 指南</h1>\n<blockquote>\n<p><strong>Language status | 语言状态：</strong> '
                'Paired research draft; translation is not a new source-verification result. / '
                '中英对照研究草稿；补译不等于重新核实来源。</p>\n</blockquote>\n<h2 id="a">A | 甲</h2>\n<p>Body.</p>\n')
        page = self.render(body=body)
        article = page[page.index('<article'):page.index('</article>')]
        header = article[:article.index('</header>')]
        self.assertNotIn('Language status', header)
        self.assertNotIn('语言状态', header)
        self.assertIn('<details class="editorial-note">', article)
        self.assertGreater(article.index('class="editorial-note"'), article.index('<p>Body.</p>'))
        self.assertIn('translation is not a new source-verification result', article)
        self.assertIn('补译不等于重新核实来源', article)

    def test_mixed_book_facts_keep_facts_in_body_and_language_note_at_end(self):
        body = ('<h1 id="guide">Guide | 指南</h1>\n'
                '<blockquote>\n<p>Summary. | 摘要。</p>\n</blockquote>\n'
                '<blockquote>\n<p>Edition: 2020. | 版本：2020。</p>\n'
                '<p>Language status | 语言状态: Paired draft. / 对照草稿。</p>\n</blockquote>\n'
                '<h2 id="a">A | 甲</h2>\n<p>Body.</p>\n')
        page = self.render(source="Book_Studies/guide.md", body=body)
        article = page[page.index('<article'):page.index('</article>')]
        self.assertIn('<div class="book-facts">\n<p>Edition: 2020. | 版本：2020。</p>', article)
        self.assertEqual(1, article.count('Edition: 2020.'))
        self.assertGreater(article.index('Language status'), article.index('<p>Body.</p>'))

    def test_long_research_sections_keep_headings_content_and_all_anchor_ids(self):
        body = ('<h1 id="guide">Guide | 指南</h1>\n<h2 id="research">Research | 研究</h2>\n'
                '<a id="evidence-a" class="anchor" aria-hidden="true"></a>\n'
                '<h3 id="entry-a">Entry A | 条目甲</h3>\n<p>' + 'alpha ' * 2000 + '</p>\n'
                '<h4 id="source-a">Source A | 来源甲</h4>\n<p>Source boundary. | 来源边界。</p>\n'
                '<a id="evidence-b" class="anchor" aria-hidden="true"></a>\n'
                '<h3 id="entry-b">Entry B | 条目乙</h3>\n<p>' + 'beta ' * 2000 + '</p>\n'
                '<h2 id="conclusion">Conclusion | 结论</h2>\n<p>Conclusion stays visible.</p>\n')
        page = self.render(body=body)
        article = page[page.index('<article'):page.index('</article>')]
        self.assertEqual(2, article.count('<details class="reading-section" open="open">'))
        self.assertEqual(ParsedPage(body).ids, ParsedPage(article).ids)
        self.assertEqual(6, len(re.findall(r'<h[1-6](?: |>)', article)))
        self.assertEqual(2000, article.count('alpha '))
        self.assertEqual(2000, article.count('beta '))
        self.assertIn('</details>\n<h2 id="conclusion">', article)
        self.assertIn('data-reader-action="expand"', article)
        self.assertIn('data-reader-action="collapse"', article)

    def test_short_article_subsections_are_not_folded(self):
        body = '<h1 id="guide">Guide | 指南</h1>\n<h3 id="short">Short | 简短</h3>\n<p>A brief explanation.</p>\n'
        self.assertNotIn('class="reading-section"', self.render(body=body))

    def test_map_figure_preserves_image_sources_and_limits_with_a_local_full_size_link(self):
        mapping = {**self.mapping, "assets/maps/example.svg": "assets/maps/example.svg", "CREDITS.md": "CREDITS.html"}
        body = build_static_site.render_markdown_body(
            "Bible_Timeline/First_Steps_Bilingual.md",
            '# Guide | 指南\n\n'
            '<a id="map-example"></a>\n\n## Map | 地图\n\n'
            '![Map with disputed locations / 地点有争议的地图](../assets/maps/example.svg)\n\n'
            'Locations are disputed.\n地点有争议。\n\n'
            '**Sources | 来源：** [Source / 来源](https://example.org/source) · '
            '[Credits | 署名](../CREDITS.md)\n\n'
            '[Open the full-size map | 打开完整大图](../assets/maps/example.svg)\n\n'
            '## After map | 地图之后\n', mapping,
        )
        page = self.render(body=body, mapping=mapping)
        figure = re.search(r'<figure class="map-figure">.*?</figure>', page, re.S).group(0)
        self.assertIn('<a class="map-viewport" href="../assets/maps/example.svg"><img ', figure)
        self.assertEqual(1, figure.count('<img '))
        self.assertIn('alt="Map with disputed locations / 地点有争议的地图"', figure)
        caption = figure[figure.index('<figcaption>'):]
        self.assertIn('Locations are disputed.', caption)
        self.assertIn('地点有争议。', caption)
        self.assertIn('href="https://example.org/source" rel="external noopener noreferrer" referrerpolicy="no-referrer"', caption)
        self.assertIn('href="../CREDITS.html"', caption)
        self.assertNotIn('Open the full-size map', caption)
        self.assertIn('View full-size map', caption)
        self.assertIn('查看大图', caption)
        self.assertIn('id="map-example"', page)

    def test_wide_table_cards_retain_bilingual_column_labels_and_cell_values(self):
        body = build_static_site.render_markdown_body(
            "README.md", '# Guide | 指南\n\n'
            '| Evidence / 证据 | Supports / 支持 | Limits / 限制 |\n| --- | --- | --- |\n'
            '| Tablet / 泥版 | Place / 地点 | No route / 不证明路线 |\n'
            '| Scroll / 书卷 | Text / 文本 | No event / 不证明事件 |\n', self.mapping,
        )
        page = self.render(body=body)
        article = page[page.index('<article'):page.index('</article>')]
        self.assertIn('class="table-scroll table-cards" role="region" tabindex="0"', article)
        self.assertEqual(1, article.count('<table>'))
        self.assertEqual(6, article.count('class="table-cell-label" aria-hidden="true"'))
        self.assertEqual(6, article.count('class="table-cell-value"'))
        labels = re.findall(r'<span class="table-cell-label" aria-hidden="true">(.*?)</span><span class="table-cell-value">', article, re.S)
        self.assertEqual(6, len(labels))
        self.assertIn('<span class="l-en" lang="en">Evidence</span>', labels[0])
        self.assertIn('<span class="l-zh" lang="zh-Hans">证据</span>', labels[0])
        self.assertEqual(labels[:3], labels[3:])
        self.assertEqual(1, article.count('No route'))
        self.assertEqual(1, article.count('不证明路线'))
        self.assertEqual(1, article.count('No event'))

    def test_visual_table_labels_do_not_duplicate_focusable_links(self):
        body = ('<div class="table-scroll">\n<table><thead><tr>'
                '<th><a href="#date">Date | 年代</a></th><th>B</th><th>C</th>'
                '</tr></thead><tbody><tr><td>One</td><td>Two</td><td>Three</td>'
                '</tr></tbody></table>\n</div>')
        shaped = site_reader._reading_tables(body)
        self.assertEqual(1, shaped.count('href="#date"'))
        self.assertIn('<span class="table-cell-label" aria-hidden="true">Date | 年代</span>', shaped)

    def test_two_column_tables_keep_the_scrollable_table_layout(self):
        body = build_static_site.render_markdown_body(
            "README.md", '# Guide | 指南\n\n| Term / 术语 | Meaning / 含义 |\n| --- | --- |\n| One / 一 | First / 第一 |\n', self.mapping,
        )
        page = self.render(body=body)
        self.assertIn('class="table-scroll" role="region" tabindex="0"', page)
        self.assertNotIn('class="table-cell-label"', page)

    def test_section_index_keeps_all_ids_and_only_drops_in_page_navigation(self):
        for identifier in ('section-index', 'route-table'):
            with self.subTest(identifier=identifier):
                body = ('<h1 id="guide">Guide | 指南</h1>\n'
                        f'<a id="{identifier}-alias" class="anchor" aria-hidden="true"></a>\n'
                        f'<h2 id="{identifier}">Index | 索引</h2>\n'
                        '<div class="table-scroll" role="region" tabindex="0" aria-label="Table">\n'
                        '<table><tbody><tr><td><a href="#a">A</a></td></tr></tbody></table>\n</div>\n'
                        '<h2 id="a">A | 甲</h2>\n')
                article = self.render(body=body)
                self.assertNotIn('<table>', article)
                self.assertTrue(ParsedPage(body).ids.issubset(ParsedPage(article).ids))
                external = body.replace('href="#a"', 'href="../Glossary/index.html"')
                self.assertIn('<table>', self.render(body=external))

    def test_reading_time_counts_one_language_and_omits_short_pages(self):
        self.assertEqual("", site_reader.reading_time("<p>A short page.</p>"))
        bilingual = "<p>" + "word " * 600 + "</p><p>" + "字" * 1050 + "</p>"
        estimate = site_reader.reading_time(bilingual)
        self.assertEqual("3 min read | 约 3 分钟", estimate)
        rendered = self.render(body=bilingual)
        self.assertIn('class="reading-time"', rendered)

    def test_short_studies_have_reading_time_while_short_navigation_does_not(self):
        for source in ("Bible_Timeline/First_Steps_Bilingual.md", "Book_Studies/guide.md"):
            with self.subTest(source=source):
                page = self.render(source=source)
                self.assertIn('class="reading-time"', page)
                self.assertIn("1 min read", page)
        for source in ("README.md", "Book_Studies/README.md"):
            with self.subTest(source=source):
                self.assertNotIn('class="reading-time"', self.render(source=source))

    def test_minimal_allowlist_never_invents_missing_collections(self):
        page = self.render(source="README.md", mapping={"README.md": "index.html"}, titles={"README.md": "Home"})
        parsed = ParsedPage(page)
        self.assertTrue(all(link in {"index.html", "#main-content", "#start-%E5%BC%80%E5%A7%8B"} for link in parsed.links))
        self.assertNotIn('class="start-reading"', page)
        self.assertNotIn('class="collection-card"', page)

    def test_collection_order_is_deterministic_and_curated(self):
        source = "Bible_Timeline/First_Steps_Bilingual.md"
        normal = site_reader.collection_order(source, self.mapping)
        reverse = site_reader.collection_order(source, dict(reversed(list(self.mapping.items()))))
        self.assertEqual(normal, reverse)
        self.assertEqual(list(site_reader.STORY_ROUTE[:3]), normal[:3])
        self.assertEqual(normal[-2:], ["Bible_Timeline/研究 乙.md", "Bible_Timeline/研究 甲.md"])

    def test_pagination_is_collection_local_and_not_a_reading_history(self):
        page = self.render()
        self.assertIn('02 / 05', page)
        self.assertIn('class="previous" href="index.html"', page)
        self.assertIn('class="next" href="Bible_Timeline_Bilingual.html"', page)
        self.assertNotIn('class="reading-pager"', self.render(source="LICENSE.md"))
        self.assertNotIn('class="reading-pager"', self.render(source="README.md"))

    def test_first_and_last_pages_do_not_wrap(self):
        order = site_reader.collection_order("Bible_Timeline/README.md", self.mapping)
        self.assertNotIn('class="previous"', self.render(source=order[0]))
        self.assertNotIn('class="next"', self.render(source=order[-1]))

    def test_home_has_only_existing_start_and_collection_links(self):
        page = self.render(source="README.md")
        self.assertIn('href="Bible_Timeline/First_Steps_Bilingual.html" class="start-reading"', page)
        self.assertEqual(0, page.count('class="collection-card"'))
        self.assertIn('href="Bible_Timeline/index.html"', page)
        self.assertIn('href="Book_Studies/index.html"', page)
        self.assertIn('to read in Chinese, in English, or in both', page)

    def test_markup_escapes_titles_and_encodes_unicode_paths(self):
        titles = dict(self.sources)
        titles["Bible_Timeline/研究 甲.md"] = '<script>unsafe</script> & "quotes"'
        page = self.render(titles=titles)
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;unsafe&lt;/script&gt;', page)
        self.assertIn('%E7%A0%94%E7%A9%B6%20%E7%94%B2.html', page)

    def test_active_page_mobile_navigation_and_keyboard_skip(self):
        page = self.render()
        self.assertIn('aria-current="page"', page)
        self.assertIn('<details><summary>', page)
        self.assertIn('<details class="mobile-toc">', page)
        self.assertIn('id="main-content" class="content" tabindex="-1"', page)

    def test_generated_local_links_and_fragments_resolve(self):
        rendered = {self.mapping[source]: ParsedPage(self.render(source=source)) for source in self.sources}
        for current, page in rendered.items():
            for link in page.links:
                with self.subTest(current=current, link=link):
                    parsed = urlsplit(link)
                    self.assertFalse(parsed.scheme or parsed.netloc or parsed.query)
                    parts = list(PurePosixPath(current).parent.parts)
                    for part in unquote(parsed.path).split('/') if parsed.path else []:
                        if part == '..':
                            parts.pop()
                        elif part and part != '.':
                            parts.append(part)
                    target = '/'.join(parts) if parsed.path else current
                    self.assertIn(target, rendered)
                    if parsed.fragment:
                        self.assertIn(unquote(parsed.fragment), rendered[target].ids)

    def test_static_privacy_and_accessibility_styles(self):
        page = self.render()
        tags = ParsedPage(page).tags
        self.assertFalse(any(tag in {'form', 'iframe', 'img', 'input'} for tag, _ in tags))
        scripts = [attrs for tag, attrs in tags if tag == 'script']
        self.assertEqual(1, len(scripts))
        self.assertTrue(dict(scripts[0])['src'].endswith('assets/lang.js'))
        self.assertEqual(['src'], list(dict(scripts[0])))
        self.assertFalse(any(name.startswith('on') for _, attrs in tags for name in attrs))
        self.assertIn("script-src 'self'", page)
        self.assertNotIn("script-src 'unsafe", page)
        script = site_reader.LANG_JS.lower()
        for token in [b'http', b'fetch', b'xmlhttprequest', b'import', b'eval', b'cookie', b'innerhtml']:
            self.assertNotIn(token, script)
        self.assertIn('name="referrer" content="no-referrer"', page)
        css = site_reader.SITE_CSS.lower()
        for token in [b'url(', b'@import', b'@font-face', b'http://', b'https://']:
            self.assertNotIn(token, css)
        for token in [b'prefers-reduced-motion', b'prefers-color-scheme', b'@media print', b':focus-visible']:
            self.assertIn(token, css)

    def test_rejects_inconsistent_page_map(self):
        with self.assertRaises(ValueError):
            site_reader.render_page('README.md', 'other.html', 'Home', '', self.mapping, self.sources, 'assets/site.css')


class LanguageMarkTests(unittest.TestCase):
    def test_pairs_lines_labels_and_mixed_headings(self):
        mark = site_reader.bilingual_html
        self.assertEqual('<span class="l-en" lang="en">Read slowly.</span>', mark('Read slowly.'))
        self.assertEqual('<span class="l-zh" lang="zh-Hans">慢慢读。</span>', mark('慢慢读。'))
        self.assertIn('<span class="l-sep"> | </span>', mark('In Three Sentences | 三句话读懂本篇'))
        mixed = mark('Week 1 | 第 1 周｜Creation | 创造')
        self.assertIn('<span class="l-en1" lang="en">Week 1 · Creation</span>', mixed)
        self.assertIn('<span class="l-zh1" lang="zh-Hans">第 1 周 · 创造</span>', mixed)
        label = mark('<strong>Language status | 语言状态:</strong> Fully bilingual.')
        self.assertTrue(label.startswith('<span class="l-en" lang="en">'))
        self.assertIn('<strong>语言状态：</strong>', label)
        # A short Chinese aside does not move an English sentence into Chinese.
        self.assertIn('l-en', mark('Many readers use the Chinese Union Version (和合本) for this.'))
        # Markup inside a link or emphasis is never split.
        self.assertNotIn('l-sep', mark('<a href="#x">Guide | 指南</a>'))

    def test_outline_and_reading_time_count_text_once(self):
        body = '<h2 id="a">' + site_reader.bilingual_html('Week 1 | 第 1 周｜Creation | 创造') + '</h2>'
        self.assertEqual(['Week 1 | 第 1 周｜Creation | 创造'], [item.title for item in site_reader.outline(body)])


class ReaderIntegrationTests(unittest.TestCase):
    def test_existing_builder_and_verifier_accept_reader_output(self):
        from scripts import build_static_site
        from test_build_static_site import create_snapshot
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / 'snapshot'
            snapshot.mkdir()
            digest = create_snapshot(snapshot)
            first = build_static_site.build_site(snapshot, digest, root / 'site')
            second = build_static_site.verify_site(snapshot, digest, root / 'site')
            self.assertEqual(first, second)
            self.assertIn('class="reading-body"', (root / 'site/docs/guide.html').read_text())
            self.assertEqual(first.page_count + 2, first.file_count)

    def test_new_native_tags_do_not_allow_event_handlers(self):
        from scripts import build_static_site
        for markup in ['<details ontoggle="alert(1)">', '<summary onclick="alert(1)">', '<aside style="color:red">', '<article onmouseover="alert(1)">']:
            with self.subTest(markup=markup), self.assertRaises(build_static_site.SiteBuildError):
                build_static_site._HTMLPolicyParser('index.html').feed(markup)


if __name__ == '__main__':
    unittest.main()
