#!/usr/bin/env python3
"""Turn one built chapter of the manual into a single self-contained HTML page (for an Artifact preview).

    python3 -I tools/publish_chapter.py part3/electronic-throttle "Part III — Configuring the engine" out.html

Run `mkdocs build` first. Takes the chapter's article from documentation/site/<page>.html, embeds every
image as a data: URI, wraps tables for horizontal scrolling, adds a contents list from the h2 headings,
and applies the page stylesheet below (light and dark, phone width). The Markdown stays the source.
"""
import base64
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "documentation/site"
DOCS = ROOT / "documentation/docs"

page, part, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
built = (SITE / f"{page}.html").read_text()
article = re.search(r'<article class="md-content__inner md-typeset">(.*?)</article>', built, re.S).group(1)
article = re.sub(r'<a class="headerlink"[^>]*>.*?</a>', "", article)          # permalink pilcrows
title = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", article, re.S).group(1))).strip()
article = re.sub(r"<h1[^>]*>.*?</h1>", "", article, count=1, flags=re.S)


def embed(m):
    src = m.group(1)
    path = (DOCS / page).parent / src
    mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
    return f'src="data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"'


article = re.sub(r'src="(\.\./img/[^"]+)"', embed, article)
article = re.sub(r"<table>", '<div class="table-wrap"><table>', article)
article = article.replace("</table>", "</table></div>")
toc = "".join(f'<li><a href="#{i}">{html.escape(html.unescape(re.sub(r"<[^>]+>", "", t)))}</a></li>'
              for i, t in re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', article, re.S))

CSS = r"""
/* Layout: workshop-manual page — a narrow sticky contents rail beside one reading column; rail folds above the text on phones. */
:root {
  --paper: #f5f6f4; --ink: #171b21; --ink-soft: #4a515c; --rule: #d6dad6; --panel: #ffffff;
  --accent: #1d4ed8; --accent-soft: #e3eaf9; --code-bg: #eceeea;
  --danger: #b4231a; --danger-bg: #fbe9e7; --warn: #8a5a00; --warn-bg: #fdf3dc;
  --tip: #1f7a42; --tip-bg: #e6f4ea; --note: #1d4ed8; --note-bg: #e6edfb; --info: #5b4b9a; --info-bg: #eeebf8;
  --basic: #2e9d4f; --inter: #b98900; --adv: #c8412d;
  --display: "IBM Plex Sans Condensed", "Arial Narrow", Arial, sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", Roboto, Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #121519; --ink: #e6e8eb; --ink-soft: #a3aab4; --rule: #2a3038; --panel: #1a1f25;
  --accent: #7aa2f7; --accent-soft: #1d2a44; --code-bg: #20262e;
  --danger: #f28b82; --danger-bg: #3a1714; --warn: #f2c063; --warn-bg: #332611; --tip: #7fd19b; --tip-bg: #13291b;
  --note: #8ab0f8; --note-bg: #16233b; --info: #b9a9f0; --info-bg: #241f38; --basic: #5ccf7f; --inter: #e7c04a; --adv: #f08a78;
  color-scheme: dark; } }
:root[data-theme="dark"] {
  --paper: #121519; --ink: #e6e8eb; --ink-soft: #a3aab4; --rule: #2a3038; --panel: #1a1f25;
  --accent: #7aa2f7; --accent-soft: #1d2a44; --code-bg: #20262e;
  --danger: #f28b82; --danger-bg: #3a1714; --warn: #f2c063; --warn-bg: #332611; --tip: #7fd19b; --tip-bg: #13291b;
  --note: #8ab0f8; --note-bg: #16233b; --info: #b9a9f0; --info-bg: #241f38; --basic: #5ccf7f; --inter: #e7c04a; --adv: #f08a78;
  color-scheme: dark; }
body { background: var(--paper); color: var(--ink); font: 16px/1.62 var(--body); }
.wrap { max-width: 1180px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 64px;
  display: grid; grid-template-columns: 230px minmax(0, 1fr); gap: 48px; }
header.chapter { grid-column: 1 / -1; border-bottom: 2px solid var(--ink); padding-bottom: 18px; display: grid; gap: 6px; }
.eyebrow { font: 600 12px/1.3 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--ink-soft); }
h1 { font: 600 clamp(34px, 6vw, 54px)/1.05 var(--display); margin: 0; text-wrap: balance; letter-spacing: -.01em; }
.spec { font: 13px/1.4 var(--mono); color: var(--ink-soft); display: flex; flex-wrap: wrap; gap: 6px 18px; }
nav.rail { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 20px); align-self: start;
  font: 14px/1.4 var(--body); border-left: 2px solid var(--rule); padding-left: 14px; }
nav.rail h2 { font: 600 12px var(--mono); text-transform: uppercase; letter-spacing: .08em; color: var(--ink-soft); margin: 0 0 8px; }
nav.rail ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 7px; }
nav.rail a { color: var(--ink); text-decoration: none; }
nav.rail a:hover, nav.rail a:focus-visible { color: var(--accent); }
main { min-width: 0; max-width: 46rem; }
main h2 { font: 600 30px/1.15 var(--display); margin: 48px 0 6px; padding-top: 14px; border-top: 1px solid var(--rule); text-wrap: balance; }
main h3 { font: 600 21px/1.25 var(--display); margin: 32px 0 6px; }
main p, main li { max-width: 68ch; }
main a { color: var(--accent); }
code { font: .88em var(--mono); background: var(--code-bg); padding: .1em .35em; border-radius: 3px; }
blockquote { margin: 18px 0; padding: 12px 18px; border-left: 4px solid var(--accent); background: var(--accent-soft); }
.twemoji { display: inline-flex; vertical-align: -0.12em; }
.twemoji svg { width: 1em; height: 1em; fill: currentColor; }
.level-basic { color: var(--basic); } .level-intermediate { color: var(--inter); } .level-advanced { color: var(--adv); }
main > p:has(> .twemoji:first-child) { font: 600 13px var(--mono); letter-spacing: .03em; color: var(--ink-soft); margin-top: 0; }
.admonition { margin: 22px 0; padding: 12px 16px 4px; border-left: 4px solid var(--note); background: var(--note-bg); border-radius: 0 6px 6px 0; }
.admonition-title { font: 600 14px/1.3 var(--body); margin: 0 0 6px; color: var(--note); }
.admonition.danger { border-color: var(--danger); background: var(--danger-bg); } .admonition.danger .admonition-title { color: var(--danger); }
.admonition.warning { border-color: var(--warn); background: var(--warn-bg); } .admonition.warning .admonition-title { color: var(--warn); }
.admonition.tip { border-color: var(--tip); background: var(--tip-bg); } .admonition.tip .admonition-title { color: var(--tip); }
.admonition.info { border-color: var(--info); background: var(--info-bg); } .admonition.info .admonition-title { color: var(--info); }
figure { margin: 26px 0; display: grid; gap: 8px; justify-items: start; }
figure img { max-width: 100%; height: auto; border: 1px solid var(--rule); border-radius: 4px; background: var(--panel); }
figure > p { margin: 0; width: 100%; }
figure:has(img[src^="data:image/svg"]) { justify-items: stretch; }
figure img[src^="data:image/svg"] { border: 0; background: transparent; width: 100%; display: block; }
figcaption { font-size: 14px; color: var(--ink-soft); max-width: 62ch; }
.table-wrap { overflow-x: auto; margin: 18px 0; border: 1px solid var(--rule); border-radius: 6px; background: var(--panel); }
table { border-collapse: collapse; width: 100%; font-size: 14px; font-variant-numeric: tabular-nums; }
th, td { text-align: left; vertical-align: top; padding: 8px 12px; border-bottom: 1px solid var(--rule); }
th { font: 600 12px var(--mono); text-transform: uppercase; letter-spacing: .05em; color: var(--ink-soft); background: var(--code-bg); }
tr:last-child td { border-bottom: 0; }
td code { white-space: nowrap; }
@media (max-width: 820px) {
  .wrap { grid-template-columns: minmax(0, 1fr); gap: 20px; }
  nav.rail { position: static; border-left: 0; border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); padding: 12px 0; }
  nav.rail ol { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
}
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
"""

page_html = f"""<title>rusEFI Electronic Throttle</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <header class="chapter">
    <div class="eyebrow">The rusEFI Manual · {html.escape(part)} · draft</div>
    <h1>{html.escape(title)}</h1>
    <div class="spec"><span>Board: Proteus F7</span><span>Tools: TunerStudio 3.3.01</span><span>Firmware: rusEFI master, October 2026</span></div>
  </header>
  <nav class="rail" aria-label="Contents"><h2>In this chapter</h2><ol>{toc}</ol></nav>
  <main>{article}</main>
</div>
"""
out.write_text(page_html)
print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
