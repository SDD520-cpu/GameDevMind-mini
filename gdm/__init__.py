"""gdm：对 GameDevMind「索引生成 + 术语检索」核心链路的零依赖复现。"""

from .corpus import DOMAIN_NAMES, Doc, load_corpus
from .indexer import Catalog, build, render_content_data_js, render_index_md, render_keywords_md, write_outputs
from .search import Hit, search

__all__ = [
    "DOMAIN_NAMES",
    "Doc",
    "load_corpus",
    "Catalog",
    "build",
    "render_index_md",
    "render_keywords_md",
    "render_content_data_js",
    "write_outputs",
    "Hit",
    "search",
]
