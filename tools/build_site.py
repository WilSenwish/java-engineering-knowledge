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


def sidebar(items: list[dict], current: str | None, prefix: str) -> str:
    home_cls = "active" if current is None else ""
    chunks = [
        '<nav class="toc">',
        "<h3>目录</h3>",
        f'<a class="{home_cls}" href="{prefix}index.html">首页</a>',
    ]
    grouped: list[tuple[str, list[dict]]] = []
    for item in items:
        if not grouped or grouped[-1][0] != item["group"]:
            grouped.append((item["group"], []))
        grouped[-1][1].append(item)
    for label, group in grouped:
        opened = " open" if current and any(entry["href"] == current for entry in group) else ""
        links = []
        for entry in group:
            active = "active" if entry["href"] == current else ""
            links.append(
                f'<a class="{active}" href="{prefix}{entry["href"]}">{html.escape(entry["title"])}</a>'
            )
        chunks.append(
            f"<details{opened}><summary>{html.escape(label)}</summary><div class='group'>{''.join(links)}</div></details>"
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
    for item in items:
        if item["group"] != current:
            current = item["group"]
            rows.append(f"<h2>{html.escape(current)}</h2><ul>")
        rows.append(f'<li><a href="{item["href"]}">{html.escape(item["title"])}</a></li>')
        nxt = items[items.index(item) + 1]["group"] if items.index(item) + 1 < len(items) else None
        if nxt != current:
            rows.append("</ul>")
    return (
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
