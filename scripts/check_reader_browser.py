#!/usr/bin/env python3
"""Browser regression checks for verified output; never a deployment command.

Playwright is a development-only dependency. The input site and its CSP are
never modified. Only approved static output is served, on loopback, temporarily.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from time import monotonic, sleep
from urllib.parse import quote, unquote, urljoin, urlsplit

WIDTHS = (320, 390, 768, 1024, 1440)
YEAR_PLAN = "Bible_Timeline/52周圣经故事线_查经与史料阅读计划.html"
RESEARCH_PAGE = "Bible_Timeline/摩西五经_历史背景与证据边界.html"


class BrowserCheckError(RuntimeError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise BrowserCheckError(code)


def wait_for_state(page, expression: str, code: str, argument=None) -> None:
    """Poll via protocol evaluation without Playwright's CSP-blocked eval poller."""
    deadline = monotonic() + 5
    while monotonic() < deadline:
        if page.evaluate(expression, argument):
            return
        sleep(0.05)
    raise BrowserCheckError(code)


class SiteHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def list_directory(self, path: str):
        self.send_error(404)
        return None


@contextmanager
def serve(root: Path):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(SiteHandler, directory=str(root))
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "BROWSER_SYMLINK_FORBIDDEN")
        if path.is_file():
            name = path.relative_to(root).as_posix()
            require(name.endswith(".html") or name in {"assets/site.css", "assets/lang.js"} or (name.startswith(("assets/maps/", "assets/art/")) and name.endswith(".svg")) or (name.startswith("assets/illustrations/") and name.endswith(".jpg")),
                    "BROWSER_UNEXPECTED_SITE_FILE")
            digest.update(name.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def layout(page) -> None:
    state = page.evaluate("""() => {
      let loaded = false;
      try { loaded = document.styleSheets.length === 1 &&
                       !!document.querySelector('link[rel="stylesheet"]').sheet; } catch (_) {}
      return {
        loaded,
        accent: getComputedStyle(document.body).getPropertyValue('--accent').trim(),
        overflow: document.documentElement.scrollWidth > innerWidth + 1,
        culprit: (() => {
          if (document.documentElement.scrollWidth <= innerWidth + 1) return '';
          let worst = '', right = innerWidth + 1;
          for (const el of document.querySelectorAll('body *')) {
            const box = el.getBoundingClientRect();
            if (box.right > right) { right = box.right; worst = el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '') + ' right=' + Math.round(box.right); }
          }
          return worst;
        })(),
        main: document.querySelectorAll('main').length,
        article: document.querySelectorAll('article.reading-body').length,
        images: [...document.images].every(img => img.complete && img.naturalWidth > 0 && img.alt.trim() && ['file:', location.protocol].includes(new URL(img.currentSrc).protocol)),
        active: document.querySelectorAll('iframe,form,input').length,
        scripts: [...document.scripts].map(script => script.getAttribute('src') || 'inline')
      };
    }""")
    require(state["loaded"] and bool(state["accent"]), "BROWSER_CSS_NOT_LOADED")
    if state["overflow"]:
        print(f"browser_overflow_element={state['culprit']}", flush=True)
    require(not state["overflow"], "BROWSER_HORIZONTAL_OVERFLOW")
    require(state["main"] == state["article"] == 1, "BROWSER_STRUCTURE_INVALID")
    require(state["active"] == 0, "BROWSER_ACTIVE_CONTENT")
    require(len(state["scripts"]) == 1 and state["scripts"][0].endswith("assets/lang.js"), "BROWSER_UNEXPECTED_SCRIPT")
    require(state["images"], "BROWSER_IMAGE_NOT_LOADED")
    policy = page.locator('meta[http-equiv="Content-Security-Policy"]').get_attribute("content")
    require("script-src 'self'" in (policy or "") and "unsafe" not in (policy or ""), "BROWSER_CSP_MISSING")


def toggle_by_keyboard(page, selector: str) -> None:
    control = page.locator(selector)
    summary = control.locator("summary").first
    summary.focus()
    summary.press("Enter")
    require(control.evaluate("el => el.open"), "BROWSER_MENU_DID_NOT_OPEN")
    layout(page)
    summary.press("Enter")
    require(not control.evaluate("el => el.open"), "BROWSER_MENU_DID_NOT_CLOSE")


def click_navigation(page, selector: str) -> None:
    print(f"browser_navigation={selector}", flush=True)
    link = page.locator(selector).first
    target = urljoin(page.url, link.get_attribute("href") or "")
    require(urlsplit(target).scheme in {"file", "http"}, "BROWSER_BAD_TEST_TARGET")
    link.click()
    page.wait_for_url(target)
    page.wait_for_load_state("load")
    require(unquote(page.url) == unquote(target), "BROWSER_NAVIGATION_FAILED")
    layout(page)


def interactions(page, home: str, output: Path, mode: str) -> None:
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(home, wait_until="load")
    page.screenshot(path=str(output / f"{mode}-home.png"))
    click_navigation(page, "a.start-reading")
    original = page.url
    page.screenshot(path=str(output / f"{mode}-reader.png"))
    click_navigation(page, ".reading-pager .next")
    click_navigation(page, ".reading-pager .previous")
    require(page.url == original, "BROWSER_PAGER_ROUNDTRIP_FAILED")

    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(original, wait_until="load")
    toggle_by_keyboard(page, ".mobile-navigation details")
    toggle_by_keyboard(page, "details.mobile-toc")
    page.locator("details.mobile-toc > summary").click()
    toc_link = page.locator("details.mobile-toc .reader-toc a").first
    fragment = toc_link.get_attribute("href") or ""
    print("browser_interaction=toc", flush=True)
    toc_link.click()
    page.wait_for_url(urljoin(original, fragment))
    require(page.evaluate("id => !!document.getElementById(id)", unquote(fragment[1:])),
            "BROWSER_TOC_TARGET_MISSING")
    click_navigation(page, ".reading-end a")
    deadline = monotonic() + 5
    while page.evaluate("scrollY") >= 300 and monotonic() < deadline:
        sleep(0.05)
    require(page.evaluate("scrollY") < 300, "BROWSER_BACK_TO_TOP_FAILED")
    page.goto(original, wait_until="load")
    page.screenshot(path=str(output / f"{mode}-mobile.png"))

    page.emulate_media(color_scheme="dark", reduced_motion="reduce")
    require(page.evaluate("getComputedStyle(document.body).backgroundColor") ==
            "rgb(21, 25, 22)", "BROWSER_DARK_MODE_FAILED")
    require(page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") ==
            "auto", "BROWSER_REDUCED_MOTION_FAILED")
    layout(page)
    page.screenshot(path=str(output / f"{mode}-dark.png"))
    page.emulate_media(media="print")
    require(not page.locator(".site-header").is_visible(), "BROWSER_PRINT_HEADER_VISIBLE")
    require(not page.locator(".mobile-navigation").is_visible(), "BROWSER_PRINT_MENU_VISIBLE")
    page.emulate_media(media="screen", color_scheme="light", reduced_motion="no-preference")

    page.goto(home, wait_until="load")
    page.keyboard.press("Tab")
    require(page.locator(".skip-link").evaluate("el => el === document.activeElement"),
            "BROWSER_SKIP_LINK_NOT_FIRST")
    page.keyboard.press("Enter")
    require(page.locator("main").evaluate("el => el === document.activeElement"),
            "BROWSER_SKIP_FOCUS_FAILED")


def reading_sections(page, home: str) -> None:
    """Exercise disclosure navigation once per protocol, including old anchors."""
    plan = urljoin(home, quote(YEAR_PLAN))
    page.emulate_media(color_scheme="light", reduced_motion="reduce")
    page.set_viewport_size({"width": 390, "height": 900})
    page.goto(plan, wait_until="load")
    sections = page.locator("details.reading-section")
    require(sections.count() == 52, "BROWSER_WEEK_SECTION_COUNT")
    require(page.locator("details.reading-section[open]").count() == 0,
            "BROWSER_SECTIONS_NOT_COLLAPSED")
    section = sections.filter(has=page.locator('[id="week-35"]'))
    require(section.count() == 1, "BROWSER_WEEK_ANCHOR_MISSING")
    heading_id = section.locator("summary h3").get_attribute("id")
    require(bool(heading_id), "BROWSER_WEEK_HEADING_ID_MISSING")

    for fragment in ("week-35", heading_id):
        page.goto(plan + "#" + quote(fragment), wait_until="load")
        wait_for_state(page, "id => document.getElementById(id).closest('details').open",
                       "BROWSER_DEEP_LINK_NOT_OPENED", fragment)
        require(section.locator(".section-content").is_visible(), "BROWSER_DEEP_LINK_HIDDEN")
        require(page.locator("details.reading-section[open]").count() == 1,
                "BROWSER_DEEP_LINK_OPENED_UNRELATED_SECTIONS")

    page.locator('[data-reader-action="expand"]').click()
    require(page.locator("details.reading-section[open]").count() == 52,
            "BROWSER_EXPAND_ALL_FAILED")
    layout(page)
    page.locator('[data-reader-action="collapse"]').click()
    require(page.locator("details.reading-section[open]").count() == 0,
            "BROWSER_COLLAPSE_ALL_FAILED")

    # The existing week-index link must reopen a closed section even when its
    # fragment is already current and the browser emits no hashchange event.
    week_link = page.locator('article a[href="#week-35"]').first
    week_link.click()
    page.wait_for_url(plan + "#week-35")
    require(section.evaluate("el => el.open"), "BROWSER_WEEK_LINK_DID_NOT_OPEN")
    section.locator("summary").click()
    require(not section.evaluate("el => el.open"), "BROWSER_SECTION_CLOSE_FAILED")
    week_link.click()
    require(section.evaluate("el => el.open"), "BROWSER_SAME_HASH_DID_NOT_OPEN")

    page.locator('article a[href="#week-36"]').first.click()
    page.wait_for_url(plan + "#week-36")
    section.locator("summary").click()
    require(not section.evaluate("el => el.open"), "BROWSER_HISTORY_SETUP_FAILED")
    page.go_back()
    page.wait_for_url(plan + "#week-35")
    wait_for_state(page, "() => document.getElementById('week-35').closest('details').open",
                   "BROWSER_HISTORY_SECTION_NOT_OPENED")
    require(section.locator(".section-content").is_visible(), "BROWSER_HISTORY_TARGET_HIDDEN")

    # Chromium's print media emulation does not emit these lifecycle events.
    # Dispatch both events while applying real print CSS, then check restoration.
    before_print = sections.evaluate_all("items => items.map(el => el.open)")
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    page.emulate_media(media="print")
    require(page.locator("details.reading-section[open]").count() == 52,
            "BROWSER_PRINT_SECTIONS_CLOSED")
    require(sections.locator(".section-content").evaluate_all(
        "items => items.length === 52 && items.every(el => el.getBoundingClientRect().height > 0)"),
        "BROWSER_PRINT_CONTENT_HIDDEN")
    require(not page.locator(".section-tools").is_visible(), "BROWSER_PRINT_CONTROLS_VISIBLE")
    page.emulate_media(media="screen")
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    require(sections.evaluate_all("items => items.map(el => el.open)") == before_print,
            "BROWSER_PRINT_STATE_NOT_RESTORED")
    print("browser_interaction=sections-deep-links-history-print", flush=True)


def reading_presentation(page, home: str, output: Path, mode: str) -> None:
    """Check the redesigned components in four representative display modes."""
    research = urljoin(home, quote(RESEARCH_PAGE))
    for width in (390, 1280):
        for theme in ("light", "dark"):
            page.set_viewport_size({"width": width, "height": 900})
            page.emulate_media(color_scheme=theme, reduced_motion="reduce")
            page.goto(research, wait_until="load")
            page.locator('[data-lang-choice="both"]').click()
            page.locator('[data-reader-action="expand"]').click()
            layout(page)
            maps = page.locator(".map-figure .map-viewport")
            require(maps.count() > 0, "BROWSER_MAP_FIGURES_MISSING")
            require(maps.evaluate_all("""items => items.every(el => {
              const image = el.querySelector('img');
              const target = new URL(el.href);
              return image && image.getBoundingClientRect().width <= el.clientWidth + 1 &&
                el.scrollWidth <= el.clientWidth + 1 && target.href === image.src &&
                target.pathname.endsWith('.svg') && target.protocol === location.protocol &&
                target.host === location.host;
            })"""), "BROWSER_MAP_CLIPPED_OR_REMOTE")
            cards = page.locator(".table-cards")
            require(cards.count() > 0, "BROWSER_TABLE_CARDS_MISSING")
            if width == 390:
                require(cards.evaluate_all("items => items.every(el => el.scrollWidth <= el.clientWidth + 1)"),
                        "BROWSER_TABLE_CARD_OVERFLOW")
                require(cards.locator(".table-cell-label").first.is_visible(),
                        "BROWSER_TABLE_CARD_LABEL_HIDDEN")
            else:
                require(not cards.locator(".table-cell-label").first.is_visible(),
                        "BROWSER_DESKTOP_CARD_LABEL_VISIBLE")
                for language, visible, hidden in (("both", "zh", "en"), ("en", "en", "zh")):
                    page.locator(f'[data-lang-choice="{language}"]').click()
                    toc = page.locator(".outline-sidebar .reader-toc")
                    require(toc.locator(f".l-{visible}").first.is_visible(),
                            "BROWSER_TOC_LANGUAGE_MISSING")
                    require(not toc.locator(f".l-{hidden}").first.is_visible(),
                            "BROWSER_TOC_DUPLICATE_LANGUAGE")
                page.locator('[data-lang-choice="both"]').click()
            page.evaluate("window.scrollTo(0, 1000)")
            wait_for_state(page, "() => document.documentElement.classList.contains('reader-scrolled')",
                           "BROWSER_READING_POSITION_NOT_UPDATED")
            require(abs(page.locator(".site-header").bounding_box()["y"]) <= 1,
                    "BROWSER_STICKY_HEADER_GAP")
            require(page.locator(".floating-top").is_visible(), "BROWSER_FLOATING_TOP_HIDDEN")
            page.screenshot(path=str(output / f"{mode}-{width}-{theme}-research.png"))
            page.locator(".floating-top").click()
            wait_for_state(page, "() => scrollY < 300", "BROWSER_FLOATING_TOP_FAILED")
            print(f"browser_presentation={mode}:{width}:{theme}", flush=True)

    # Follow the actual map link once, including file-mode offline navigation.
    map_link = page.locator(".map-figure .map-viewport").first
    target = urljoin(page.url, map_link.get_attribute("href") or "")
    map_link.click()
    page.wait_for_url(target)
    require(page.locator("svg").count() == 1, "BROWSER_FULL_MAP_NOT_OPENED")
    page.emulate_media(color_scheme="light", reduced_motion="no-preference")


def without_javascript(browser, home: str, route_request) -> None:
    """The complete year plan remains readable when enhancement is unavailable."""
    context = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 900})
    context.route("**/*", route_request)
    try:
        page = context.new_page()
        page.goto(urljoin(home, quote(YEAR_PLAN)) + "#week-35", wait_until="load")
        require(page.locator("details.reading-section[open]").count() == 52,
                "BROWSER_NO_JS_CONTENT_COLLAPSED")
        require(not page.locator(".section-tools").is_visible(), "BROWSER_NO_JS_CONTROLS_VISIBLE")
        require(page.locator("details.reading-section .section-content").evaluate_all(
            "items => items.length === 52 && items.every(el => el.getBoundingClientRect().height > 0)"),
            "BROWSER_NO_JS_CONTENT_HIDDEN")
        layout(page)
    finally:
        context.close()
    print("browser_interaction=no-javascript", flush=True)


def run(site: Path, output: Path) -> dict:
    from playwright.sync_api import sync_playwright

    require(site.is_dir() and not site.is_symlink(), "BROWSER_SITE_INVALID")
    site = site.resolve()
    require(not output.resolve().is_relative_to(site), "BROWSER_OUTPUT_INSIDE_SITE")
    before = fingerprint(site)
    pages = sorted(site.rglob("*.html"))
    require(bool(pages) and (site / "index.html").is_file(), "BROWSER_HOME_MISSING")
    output.mkdir(parents=True, exist_ok=False)
    result = {"pages": len(pages), "widths": list(WIDTHS), "layout_checks": 0,
              "protocols": ["file", "http"], "status": "FAIL"}
    errors: list[str] = []
    try:
        with serve(site) as base, sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            result["chromium_version"] = browser.version
            context = browser.new_context(color_scheme="light")
            context.set_default_timeout(15000)

            def route_request(route):
                url = route.request.url
                parsed = urlsplit(url)
                allowed = url.startswith(base)
                if parsed.scheme == "file":
                    allowed = Path(unquote(parsed.path)).resolve().is_relative_to(site)
                if allowed:
                    route.continue_()
                else:
                    errors.append("BROWSER_REMOTE_REQUEST")
                    route.abort()

            context.route("**/*", route_request)
            page = context.new_page()
            page.on("pageerror", lambda _: errors.append("BROWSER_PAGE_ERROR"))
            page.on("requestfailed", lambda _: errors.append("BROWSER_REQUEST_FAILED"))
            page.on("response", lambda r: errors.append("BROWSER_HTTP_ERROR") if r.status >= 400 else None)
            for mode in result["protocols"]:
                for index, path in enumerate(pages):
                    url = path.as_uri() if mode == "file" else base + quote(path.relative_to(site).as_posix())
                    result["last_page_index"] = index
                    result["last_protocol"] = mode
                    page.goto(url, wait_until="load")
                    for width in WIDTHS:
                        result["last_width"] = width
                        page.set_viewport_size({"width": width, "height": 900})
                        layout(page)
                        if width == 390:
                            toggle_by_keyboard(page, ".mobile-navigation details")
                            if page.locator("details.mobile-toc").count():
                                toggle_by_keyboard(page, "details.mobile-toc")
                        result["layout_checks"] += 1
                home = (site / "index.html").as_uri() if mode == "file" else base + "index.html"
                interactions(page, home, output, mode)
                reading_sections(page, home)
                reading_presentation(page, home, output, mode)
                without_javascript(browser, home, route_request)
                print(f"browser_{mode}_pages={len(pages)}", flush=True)
            context.close()
            browser.close()
        require(not errors, errors[0] if errors else "BROWSER_REQUEST_ERROR")
        require(before == fingerprint(site), "BROWSER_SITE_CHANGED")
        result["status"] = "PASS"
        result["request_errors"] = 0
        return result
    except Exception as error:
        result["error_type"] = type(error).__name__
        trace = error.__traceback__
        while trace is not None:
            if Path(trace.tb_frame.f_code.co_filename).name == Path(__file__).name:
                result["failed_script_line"] = trace.tb_lineno
            trace = trace.tb_next
        result["error_code"] = str(error) if isinstance(error, BrowserCheckError) else "BROWSER_RUNTIME_ERROR"
        print(f"browser_failed_at={result.get('last_protocol')}:{result.get('last_page_index')}:"
              f"{pages[result.get('last_page_index', 0)].relative_to(site).as_posix() if pages else ''}:"
              f"{result.get('last_width')}", flush=True)
        raise BrowserCheckError(result["error_code"]) from None
    finally:
        (output / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = run(args.site, args.output)
    except Exception as error:
        code = str(error) if isinstance(error, BrowserCheckError) else "BROWSER_RUNTIME_ERROR"
        print(f"error_code={code}\nbrowser_check=FAIL")
        return 1
    print(f"browser_pages={result['pages']}\nbrowser_layout_checks={result['layout_checks']}")
    print("browser_check=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
