"""
检索：复现「按术语定位 + 按领域筛选」这条查找路径。

原项目 README 把「查找具体问题」列为四大入口之一：
按领域浏览 INDEX.md / 按术语定位 KEYWORDS.md / 搜索与筛选交互式导航。
这里把三条路径合成一个可调用的检索函数，供 CLI 与 nav 页面共用。
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass

from .indexer import Catalog
from .corpus import Doc


@dataclass(frozen=True)
class Hit:
    doc: Doc
    score: int
    matched: tuple[str, ...]


def search(catalog: Catalog, query: str, domain: int | None = None, limit: int = 8) -> list[Hit]:
    q = query.strip().lower()
    if not q:
        return []

    hits: list[Hit] = []
    all_keywords = list(catalog.inverted.keys())

    for doc in catalog.docs:
        if domain is not None and doc.domain != domain:
            continue
        score = 0
        matched: list[str] = []

        for kw in doc.keywords:
            k = kw.strip().lower()
            if k == q:
                score += 5
                matched.append(kw)
            elif q in k:
                score += 3
                matched.append(kw)
            elif difflib.SequenceMatcher(None, q, k).ratio() >= 0.72:
                score += 2
                matched.append(kw + "~")

        if q in doc.title.lower():
            score += 4
            matched.append("标题")
        if q in doc.summary.lower() or q in doc.body.lower():
            score += 1
            matched.append("正文")

        # 容错：查询词本身不在任何关键词里时，找最相似的术语
        if score == 0 and all_keywords:
            near = difflib.get_close_matches(q, all_keywords, n=1, cutoff=0.65)
            if near and any(d.path == doc.path for d in catalog.inverted[near[0]]):
                score += 2
                matched.append("近似:" + near[0])

        if score:
            hits.append(Hit(doc, score, tuple(dict.fromkeys(matched))))

    hits.sort(key=lambda h: (-h.score, h.doc.domain, h.doc.title))
    return hits[:limit]
