"""
一键运行演示：真实执行「语料 -> 索引 -> 检索」全链路。

    python demo.py

输出同时写入 run.log（UTF-8），供 screenshots/ 下的运行截图使用。
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from gdm import DOMAIN_NAMES, build, search, write_outputs

ROOT = Path(__file__).resolve().parent

QUERIES = ["内存池", "帧同步", "热更新", "幂等", "DrawCall"]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    lines: list[str] = []

    def emit(line: str = "") -> None:
        print(line)
        lines.append(line)

    bar = "=" * 78
    emit(bar)
    emit("  gamedevmind-mini  |  技术图谱索引引擎 · 本机运行演示")
    emit("  原项目: https://github.com/gonglei007/GameDevMind   (MIT / Python)")
    emit("  复现链路: 语料 -> 倒排索引 -> INDEX.md / KEYWORDS.md / nav/content-data.js")
    emit(f"  环境: Python {sys.version.split()[0]} | {sys.platform} | {datetime.now():%Y-%m-%d %H:%M:%S}")
    emit(bar)

    catalog = build(ROOT / "corpus")
    s = catalog.stats

    emit("# [1/5] 扫描语料，按「编号.标题.md」推断能力域与层级")
    emit(f"  {s['doc_count']} 篇文档 / {len(s['domain_counts'])} 个能力域 / "
         f"{s['keyword_count']} 个关键词 / {s['link_count']} 条索引关联")
    emit("  " + " · ".join(f"{d}.{DOMAIN_NAMES[d]} {c}篇" for d, c in s["domain_counts"].items()))

    emit("# [2/5] 生成三个自动产物（对应原项目 INDEX.md / KEYWORDS.md / content-data.js）")
    outputs = write_outputs(catalog, ROOT)
    for name, path in outputs.items():
        emit(f"> {name:<24} {path.stat().st_size:>6} bytes")

    emit("# [3/5] 按术语定位：倒排索引检索")
    all_hits: dict[str, list] = {}
    for q in QUERIES:
        hits = search(catalog, q)
        all_hits[q] = hits
        emit(f"$ python -m gdm search {q}")
        for i, h in enumerate(hits[:2], 1):
            emit(f"  [{i}] {h.doc.title}  ({h.doc.domain}.{DOMAIN_NAMES[h.doc.domain]}, "
                 f"{h.score}分)  命中: {','.join(h.matched[:3])}")
        emit(f"  -> 共 {len(hits)} 篇匹配")

    emit("# [4/5] 按能力域筛选（运营能力内的热更新）")
    domain_hits = search(catalog, "热更新", domain=6)
    emit("$ python -m gdm search 热更新 --domain 6")
    emit("  " + " · ".join(h.doc.title for h in domain_hits))
    emit(f"  -> 共 {len(domain_hits)} 篇匹配")

    emit("# [5/5] 自检断言")
    checks = [
        ("语料扫描为 16 篇文档", s["doc_count"] == 16),
        ("层级与父文档推断生效（0/1/2 三级）",
         {d.level for d in catalog.docs} == {0, 1, 2}
         and any(d.parent for d in catalog.docs)),
        ("覆盖全部 6 个能力域", len(s["domain_counts"]) == 6),
        ("三个自动产物均已生成且非空", all(p.exists() and p.stat().st_size > 0 for p in outputs.values())),
        ("INDEX.md 含能力域分类与文档链接",
         "### 1. 基础能力" in (ROOT / "INDEX.md").read_text(encoding="utf-8")
         and "内存管理" in (ROOT / "INDEX.md").read_text(encoding="utf-8")),
        ("KEYWORDS.md 含术语分组", "### 内存池" in (ROOT / "KEYWORDS.md").read_text(encoding="utf-8")),
        ("content-data.js 含 DOCS/parent/KEYWORDS",
         all(k in (ROOT / "nav" / "content-data.js").read_text(encoding="utf-8")
             for k in ("const DOCS", "parent", "const KEYWORDS"))),
        ("术语「内存池」跨文档命中 >= 2 篇", len(all_hits["内存池"]) >= 2),
        ("术语「帧同步」跨文档命中 >= 2 篇", len(all_hits["帧同步"]) >= 2),
        ("术语「热更新」跨能力域命中 >= 3 篇", len(all_hits["热更新"]) >= 3),
        ("能力域筛选结果全部属于 6.运营能力", all(h.doc.domain == 6 for h in domain_hits) and bool(domain_hits)),
        ("模糊检索可容错拼写", len(search(catalog, "DrowCall")) >= 1),
    ]
    passed = 0
    for label, ok in checks:
        passed += bool(ok)
        emit(f". {label}  {'PASS' if ok else 'FAIL'}")

    emit("-" * 78)
    emit(f"# 结果: {passed}/{len(checks)} 断言通过 | {s['doc_count']} 篇文档 | "
         f"3 个自动产物 | 0 外部依赖")
    emit("# 交互式导航: 浏览器打开 nav/index.html，支持搜索 + 能力域筛选")
    emit("# 单元测试: python -m unittest discover -s tests -v")
    emit(bar)

    (ROOT / "run.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
