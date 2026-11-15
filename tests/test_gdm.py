"""索引引擎自测：python -m unittest discover -s tests -v"""

from __future__ import annotations

import unittest
from pathlib import Path

from gdm import (
    DOMAIN_NAMES,
    build,
    load_corpus,
    render_content_data_js,
    render_index_md,
    render_keywords_md,
    search,
)

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"


class TestCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = load_corpus(CORPUS)

    def test_doc_count(self):
        self.assertEqual(len(self.docs), 16)

    def test_all_six_domains(self):
        self.assertEqual({d.domain for d in self.docs}, set(range(1, 7)))

    def test_number_and_level(self):
        doc = next(d for d in self.docs if d.title == "内存管理")
        self.assertEqual(doc.number, "1.1.6")
        self.assertEqual(doc.level, 2)
        self.assertEqual(doc.domain, 1)

    def test_front_matter_keywords(self):
        doc = next(d for d in self.docs if d.title == "内存管理")
        self.assertIn("内存池", doc.keywords)
        self.assertIn("循环引用", doc.keywords)
        self.assertTrue(doc.summary)

    def test_levels_present(self):
        self.assertEqual({d.level for d in self.docs}, {0, 1, 2})

    def test_parent_inferred(self):
        child = next(d for d in self.docs if d.number == "1.1.6")
        self.assertTrue(child.parent.endswith("1.1.编程语言.md"))
        middle = next(d for d in self.docs if d.number == "1.1")
        self.assertTrue(middle.parent.endswith("1.基础能力.md"))
        root = next(d for d in self.docs if d.number == "1")
        self.assertEqual(root.parent, "")

    def test_roles(self):
        doc = next(d for d in self.docs if d.title == "图形与渲染")
        self.assertEqual(doc.roles, "客户端")


class TestIndexer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build(CORPUS)

    def test_stats(self):
        s = self.catalog.stats
        self.assertEqual(s["doc_count"], 16)
        self.assertEqual(len(s["domain_counts"]), 6)
        self.assertGreater(s["keyword_count"], 30)

    def test_inverted_index_cross_docs(self):
        self.assertGreaterEqual(len(self.catalog.inverted["热更新"]), 3)
        self.assertGreaterEqual(len(self.catalog.inverted["幂等"]), 2)

    def test_render_index(self):
        text = render_index_md(self.catalog)
        self.assertIn("## 按能力域分类", text)
        self.assertIn("### 6. 运营能力", text)
        self.assertIn("corpus/1.基础能力/1.1.6.内存管理.md", text)

    def test_render_keywords(self):
        text = render_keywords_md(self.catalog)
        self.assertIn("### 内存池", text)
        self.assertIn(" · ", text)

    def test_render_nav_data(self):
        text = render_content_data_js(self.catalog)
        for key in ("const DOCS", '"t"', '"p"', '"c"', '"l"', '"r"', '"parent"', "const KEYWORDS"):
            self.assertIn(key, text)


class TestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build(CORPUS)

    def test_exact_keyword(self):
        hits = search(self.catalog, "内存池")
        self.assertIn("内存管理", [h.doc.title for h in hits])
        self.assertGreaterEqual(len(hits), 2)

    def test_cross_domain(self):
        hits = search(self.catalog, "热更新")
        self.assertGreaterEqual(len({h.doc.domain for h in hits}), 3)

    def test_domain_filter(self):
        hits = search(self.catalog, "热更新", domain=6)
        self.assertTrue(hits)
        self.assertTrue(all(h.doc.domain == 6 for h in hits))

    def test_fuzzy(self):
        self.assertTrue(search(self.catalog, "DrowCall"))

    def test_no_match(self):
        self.assertEqual(search(self.catalog, "不存在的术语zzz"), [])

    def test_limit(self):
        self.assertLessEqual(len(search(self.catalog, "热更新", limit=2)), 2)

    def test_domain_names(self):
        self.assertEqual(DOMAIN_NAMES[6], "运营能力")


if __name__ == "__main__":
    unittest.main(verbosity=2)
