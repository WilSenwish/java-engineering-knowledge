#!/usr/bin/env python3
"""Build a static HTML site from docs/ markdown."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
ASSETS_SRC = ROOT / "site-src"

GROUPS = [
    ("01-java-core", "域1 · Java 核心"),
    ("02-backend-components", "域2 · 后端组件"),
    ("03-distributed", "域3 · 分布式"),
    ("04-delivery-cloudnative", "域4 · 交付与云原生"),
    ("05-ops-observability", "域5 · 运维与可观测"),
    ("06-performance-ai", "域6 · 性能与 AI"),
    ("07-business-cases", "域7 · 实战案例"),
]


def svg(inner: str) -> str:
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{inner}</svg>'


ICONS = {
    "toc": svg('<path d="M8 6h12M8 12h12M8 18h12"/><path d="M4 6h.01M4 12h.01M4 18h.01"/>'),
    "home": svg('<path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1z"/>'),
    "file": svg('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>'),
    "module": svg('<path d="M9 4 7 20M17 4l-2 16M4 9h16M3 15h16"/>'),
    "01-java-core": svg('<path d="m8 8-4 4 4 4M16 8l4 4-4 4"/>'),
    "02-backend-components": svg('<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>'),
    "03-distributed": svg('<circle cx="6" cy="12" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><path d="M8 12h8M16.2 7.6 8 11M16.2 16.4 8 13"/>'),
    "04-delivery-cloudnative": svg('<path d="M7 18h10a4 4 0 0 0 .4-8A6 6 0 0 0 6 9.2 3.5 3.5 0 0 0 7 18z"/>'),
    "05-ops-observability": svg('<path d="M3 12h4l2-5 4 10 2-5h6"/>'),
    "06-performance-ai": svg('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>'),
    "07-business-cases": svg('<path d="M3 8h18v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>'),
    "principle": svg('<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2" fill="currentColor" stroke="none"/>'),
    "practice": svg('<circle cx="12" cy="12" r="8"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>'),
    "pitfall": svg('<path d="M12 4 3 19h18z"/><path d="M12 10v4M12 17h.01"/>'),
    "advance": svg('<path d="M4 16l6-6 4 4 6-7"/><path d="M14 7h6v6"/>'),
    "compare": svg('<path d="M4 5h7v14H4zM13 5h7v14h-7z"/>'),
    "section": svg('<circle cx="12" cy="12" r="4"/>'),
}

SECTIONS = (
    ("核心原理", "principle"),
    ("生产落地", "practice"),
    ("踩坑规避", "pitfall"),
    ("优化进阶", "advance"),
    ("选型对比", "compare"),
)


def ico(name: str) -> str:
    return f'<span class="nav-ico">{ICONS[name]}</span>'

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
    extension_configs={"toc": {"permalink": False, "toc_depth": 3}},
)


def reset_md() -> None:
    MD.reset()


def title_of(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.M)
    return match.group(1).strip() if match else fallback


def headings_of(text: str) -> list[str]:
    found = re.findall(r"^#{2,3}\s+(.+)$", text, re.M)
    return [re.sub(r"[*`]", "", item).strip() for item in found]


def rewrite_links(body: str) -> str:
    def repl(match: re.Match[str]) -> str:
        url = match.group(1)
        if url.startswith(("http://", "https://", "mailto:")):
            return match.group(0)
        path, _, anchor = url.partition("#")
        if path.endswith(".md"):
            path = path[:-3] + ".html"
            url = path + (("#" + anchor) if anchor else "")
        return f'href="{url}"'

    return re.sub(r'href="([^"]+)"', repl, body)


def pages() -> list[dict]:
    items = []
    for folder, label in GROUPS:
        directory = DOCS / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(DOCS).as_posix()
            items.append(
                {
                    "group": label,
                    "folder": folder,
                    "rel": rel,
                    "href": rel[:-3] + ".html",
                    "title": title_of(text, path.stem),
                    "headings": headings_of(text),
                    "text": text,
                }
            )
    return items


def h2_links(body: str) -> list[tuple[str, str]]:
    found = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', body, flags=re.S)
    links = []
    for anchor, inner in found:
        label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inner)).strip()
        if label:
            links.append((anchor, label))
    return links


def decorate_headings(body: str) -> str:
    def h2(match: re.Match[str]) -> str:
        return (
            f'<h2 id="{match.group(1)}" class="lv-module">'
            f'<span class="hd-ico">{ICONS["module"]}</span>{match.group(2)}</h2>'
        )

    def h3(match: re.Match[str]) -> str:
        text = re.sub(r"<[^>]+>", "", match.group(2))
        kind = "section"
        for key, name in SECTIONS:
            if key in text:
                kind = name
                break
        return (
            f'<h3 id="{match.group(1)}" class="lv-{kind}">'
            f'<span class="hd-ico">{ICONS[kind]}</span>{match.group(2)}</h3>'
        )

    body = re.sub(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', h2, body, flags=re.S)
    return re.sub(r'<h3 id="([^"]+)"[^>]*>(.*?)</h3>', h3, body, flags=re.S)


_SECTION_CARD = re.compile(
    r'<h3\b[^>]*class="[^"]*\blv-(?:principle|practice|pitfall|advance|compare)\b'
)


def wrap_section_cards(module_html: str) -> str:
    pieces = re.split(r"(?=<h3\b)", module_html)
    if len(pieces) == 1:
        return module_html
    out = [pieces[0]]
    for piece in pieces[1:]:
        if _SECTION_CARD.match(piece):
            out.append(f'<div class="section-card">{piece}</div>')
        else:
            out.append(piece)
    return "".join(out)


def wrap_cards(body: str) -> str:
    parts = re.split(r"(?=<h2\b)", body)
    out = []
    for part in parts:
        if not part.startswith("<h2"):
            out.append(part)
            continue
        is_domain = 'class="lv-domain"' in part[:160]
        sectioned = wrap_section_cards(part)
        if is_domain or sectioned == part:
            out.append(f'<section class="module-card">{part}</section>')
        else:
            out.append(sectioned)
    return "".join(out)


def sidebar(items: list[dict], current: str | None, prefix: str) -> str:
    home_cls = "nav-home active" if current is None else "nav-home"
    chunks = [
        '<nav class="toc">',
        f"<h3>{ico('toc')}<span>目录</span></h3>",
        f'<a class="{home_cls}" href="{prefix}index.html">{ico("home")}<span class="nav-label">首页</span></a>',
    ]
    grouped: list[tuple[str, list[dict]]] = []
    for item in items:
        if not grouped or grouped[-1][0] != item["group"]:
            grouped.append((item["group"], []))
        grouped[-1][1].append(item)
    for label, group in grouped:
        folder = group[0]["folder"]
        opened = " open" if current and any(entry["href"] == current for entry in group) else ""
        links = []
        for entry in group:
            active = "nav-page active" if entry["href"] == current else "nav-page"
            links.append(
                f'<a class="{active}" href="{prefix}{entry["href"]}">'
                f'{ico("file")}<span class="nav-label">{html.escape(entry["title"])}</span></a>'
            )
            if entry["href"] == current:
                heads = "".join(
                    f'<a class="nav-head" href="#{html.escape(anchor)}">'
                    f'{ico("module")}<span class="nav-label">{html.escape(text)}</span></a>'
                    for anchor, text in entry.get("h2") or []
                )
                if heads:
                    links.append(f'<div class="subheads">{heads}</div>')
        chunks.append(
            f'<details class="nav-domain"{opened}>'
            f"<summary>{ico(folder)}<span class='nav-label'>{html.escape(label)}</span></summary>"
            f"<div class='group'>{''.join(links)}</div></details>"
        )
    chunks.append("</nav>")
    return "".join(chunks)


def page_html(title: str, article: str, items: list[dict], current: str | None, prefix: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{prefix}assets/style.css">
  <script>
    (function () {{
      var mode = "system";
      try {{
        var saved = localStorage.getItem("kb-theme");
        if (saved === "light" || saved === "dark" || saved === "system") mode = saved;
      }} catch (e) {{}}
      var dark = mode === "dark" || (mode === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
      document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
      document.documentElement.setAttribute("data-theme-mode", mode);
    }})();
  </script>
</head>
<body data-root="{prefix}">
  <div class="read-progress" aria-hidden="true"><span id="read-bar"></span></div>
  <div class="toolbar">
    <a class="brand" href="{prefix}index.html">Java 工程知识库</a>
    <span class="tools">
      <button class="btn" id="listenBtn" type="button">▶ 听</button>
      <input id="q" class="search" type="search" placeholder="搜索标题与正文" autocomplete="off">
      <button class="btn" id="themeBtn" type="button">◐ 系统</button>
      <button class="btn" id="topBtn" type="button">↑ 顶部</button>
      <button class="btn" id="botBtn" type="button">↓ 底部</button>
      <button class="btn menu-btn" id="menuBtn" type="button">目录</button>
    </span>
  </div>
  <div id="search-hits"></div>
  <div class="shell">
    {sidebar(items, current, prefix)}
    <main class="wrap">
      <article>{article}</article>
    </main>
  </div>
  <script src="{prefix}assets/search-index.js"></script>
  <script src="{prefix}assets/app.js"></script>
</body>
</html>
"""


def home_article(items: list[dict]) -> str:
    rows = []
    current = None
    for index, item in enumerate(items):
        if item["group"] != current:
            current = item["group"]
            rows.append(
                f'<h2 class="lv-domain"><span class="hd-ico">{ICONS[item["folder"]]}</span>'
                f"{html.escape(current)}</h2><ul class='domain-list'>"
            )
        rows.append(
            f'<li><a href="{item["href"]}">{ico("file")}'
            f"<span>{html.escape(item['title'])}</span></a></li>"
        )
        nxt = items[index + 1]["group"] if index + 1 < len(items) else None
        if nxt != current:
            rows.append("</ul>")
    return wrap_cards(
        "<h1>Java 后端开发与架构知识库</h1>"
        "<blockquote><p>二次加工层。每篇按核心原理、生产落地、踩坑规避、优化进阶、选型对比来写。</p></blockquote>"
        + "".join(rows)
    )


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    shutil.copytree(ASSETS_SRC, SITE / "assets")

    items = pages()
    search = []
    for item in items:
        reset_md()
        body = rewrite_links(MD.convert(item["text"]))
        item["h2"] = h2_links(body)
        body = wrap_cards(decorate_headings(body))
        prefix = "../" if "/" in item["href"] else ""
        plain = re.sub(r"\s+", " ", re.sub(r"[#>*`\[\]]", " ", item["text"])).strip()
        page = page_html(item["title"], body, items, item["href"], prefix)
        target = SITE / item["href"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
        search.append({"title": item["title"], "href": item["href"], "text": plain})

    index_plain = "Java 后端开发与架构知识库 总览"
    search.insert(0, {"title": "首页", "href": "index.html", "text": index_plain})
    payload = "window.SITE_INDEX = " + json.dumps(search, ensure_ascii=False) + ";\n"
    (SITE / "assets" / "search-index.js").write_text(payload, encoding="utf-8")
    (SITE / "index.html").write_text(
        page_html("Java 后端开发与架构知识库", home_article(items), items, None, ""),
        encoding="utf-8",
    )
    print(f"wrote {len(items)} pages to {SITE}")


if __name__ == "__main__":
    main()
