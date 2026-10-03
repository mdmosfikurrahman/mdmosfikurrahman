#!/usr/bin/env python3
"""Builds assets/tech.svg: the 2x2 tech grid, one borderless image.

    python assets/tech.py

GitHub draws a border on every table, so the grid is a single SVG instead. Icons are
fetched once and inlined (no external references, which camo would not load), drawn in
one grey that reads on both light and dark pages.
"""

import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GREY = "#8b949e"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")


def dp(name):
    return f"https://api.iconify.design/devicon-plain/{name}.svg?color=%238b949e"


def si(name):
    return f"https://cdn.simpleicons.org/{name}/8b949e"


GROUPS = [
    ("LANGUAGES", [("C#", dp("csharp")), ("Java", dp("java")), ("TypeScript", dp("typescript")), ("Python", dp("python"))]),
    ("FRAMEWORKS AND APIS", [(".NET", dp("dotnetcore")), ("Spring", dp("spring")), ("GraphQL", dp("graphql")),
                             ("gRPC", dp("grpc")), ("React", si("react")), ("Next.js", dp("nextjs"))]),
    ("DATA", [("SQL Server", dp("microsoftsqlserver")), ("PostgreSQL", dp("postgresql")), ("Redis", dp("redis")),
              ("Elasticsearch", dp("elasticsearch"))]),
    ("CLOUD AND DEVOPS", [("Docker", dp("docker")), ("Kubernetes", dp("kubernetes")), ("Azure", dp("azure")),
                          ("AWS", dp("amazonwebservices"))]),
]

W, COL_W = 760, 380
ICON, GAP = 30, 26
ROW_Y = [18, 128]


def inner(svg):
    viewbox = re.search(r'viewBox="([^"]+)"', svg).group(1)
    body = re.sub(r"^.*?<svg[^>]*>", "", svg, count=1, flags=re.S)
    body = re.sub(r"</svg>\s*$", "", body)
    return viewbox, body


def cell(col, row, label, items):
    cx = col * COL_W + COL_W / 2
    y = ROW_Y[row]
    total = len(items) * ICON + (len(items) - 1) * GAP
    x0 = cx - total / 2
    out = [f'<text x="{cx}" y="{y + 12}" text-anchor="middle" font-size="12" letter-spacing="2" '
           f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" fill="{GREY}">{label}</text>']
    for i, (title, url) in enumerate(items):
        viewbox, body = inner(fetch(url))
        x = x0 + i * (ICON + GAP)
        out.append(f'<svg x="{x}" y="{y + 32}" width="{ICON}" height="{ICON}" viewBox="{viewbox}" fill="{GREY}">'
                   f'<title>{title}</title>{body}</svg>')
    return "\n".join(out)


def main():
    cells = [cell(i % 2, i // 2, label, items) for i, (label, items) in enumerate(GROUPS)]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 200" width="{W}" height="200" role="img" '
           f'aria-label="Tech stack: languages, frameworks and APIs, data, cloud and DevOps">\n'
           + "\n".join(cells) + "\n</svg>\n")
    with open(os.path.join(HERE, "tech.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote tech.svg", len(svg), "bytes")


if __name__ == "__main__":
    main()
