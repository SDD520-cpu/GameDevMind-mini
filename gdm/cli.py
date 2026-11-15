"""命令行入口：python -m gdm build / stats / search"""

from __future__ import annotations

import argparse
from pathlib import Path

from .corpus import DOMAIN_NAMES
from .indexer import build, write_outputs
from .search import search

ROOT = Path(__file__).resolve().parent.parent


def _catalog(corpus: str | None):
    return build(Path(corpus) if corpus else ROOT / "corpus")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gdm", description="技术图谱索引生成与检索")
    parser.add_argument("--corpus", help="语料目录（默认 corpus/，可指向原项目 mds/）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="生成 INDEX.md / KEYWORDS.md / nav/content-data.js")
    sub.add_parser("stats", help="打印内容统计")
    p_search = sub.add_parser("search", help="按术语检索文档")
    p_search.add_argument("query")
    p_search.add_argument("--domain", type=int, choices=range(1, 7))
    p_search.add_argument("--limit", type=int, default=8)

    args = parser.parse_args(argv)
    catalog = _catalog(args.corpus)

    if args.cmd == "build":
        outputs = write_outputs(catalog, ROOT)
        for name, path in outputs.items():
            print(f"  生成 {name}  ({path.stat().st_size} bytes)")
        print(f"  共 {len(catalog.docs)} 篇文档 / {len(catalog.inverted)} 个关键词")
        return 0

    if args.cmd == "stats":
        s = catalog.stats
        print(f"文档数: {s['doc_count']}  关键词: {s['keyword_count']}  索引关联: {s['link_count']}")
        for domain, count in s["domain_counts"].items():
            print(f"  {domain}. {DOMAIN_NAMES.get(domain, '?')}: {count} 篇")
        return 0

    hits = search(catalog, args.query, args.domain, args.limit)
    print(f"查询: {args.query}" + (f"  [能力域 {args.domain}]" if args.domain else ""))
    if not hits:
        print("  (无匹配)")
        return 1
    for i, h in enumerate(hits, 1):
        print(f"  [{i}] {h.doc.title}  ({h.doc.domain}.{DOMAIN_NAMES[h.doc.domain]}, {h.score} 分)")
        print(f"      {h.doc.path}  命中: {', '.join(h.matched)}")
    return 0
