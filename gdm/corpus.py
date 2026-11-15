"""
语料解析：复现 GameDevMind `mds/` 的「编号.标题.md」命名约定。

原项目把 124 篇文档按 `1.基础能力/1.1.6.内存管理.md` 这样的层级编号组织，
`tools/check/generate_catalog.py` 再据此推断能力域(c)、层级(l)与父文档(parent)。
本模块用零依赖方式复刻这套推断，并从 front-matter 读取关键词与角色。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DOMAIN_NAMES = {
    1: "基础能力",
    2: "技术能力",
    3: "研发能力",
    4: "生产能力",
    5: "管理能力",
    6: "运营能力",
}

_NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)[.．](.+)\.md$")


@dataclass(frozen=True)
class Doc:
    path: str                 # 相对项目根的路径（POSIX 风格）
    title: str
    domain: int               # 1..6，对应六大能力域
    level: int                # 0=域首页，1=二级，2=三级
    number: str               # 如 "1.1.6"
    parent: str               # 父文档 path，无则 ""
    roles: str                # 如 "客户端,服务端"
    keywords: tuple[str, ...]
    summary: str
    body: str


def _split_list(value: str) -> tuple[str, ...]:
    parts = re.split(r"[,，、;；]", value)
    return tuple(p.strip() for p in parts if p.strip())


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """解析极简 YAML front-matter（只支持 key: value，不引入第三方库）。"""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            meta: dict[str, str] = {}
            for line in lines[1:i]:
                if ":" in line and not line.strip().startswith("#"):
                    key, _, value = line.partition(":")
                    meta[key.strip()] = value.strip()
            return meta, "\n".join(lines[i + 1 :]).strip()
    return {}, text


def _summary_from_body(body: str) -> str:
    for line in body.splitlines():
        s = line.strip().lstrip("#").strip()
        if s and not s.startswith(("---", "|", "```")):
            return s[:90]
    return ""


def _keywords_from_body(body: str, title: str) -> tuple[str, ...]:
    """没有 front-matter 时，退化为「标题 + 正文中加粗的术语」。"""
    found = [title, *re.findall(r"\*\*(.+?)\*\*", body)]
    result: list[str] = []
    for item in found:
        if item.strip() and item not in result:
            result.append(item.strip())
    return tuple(result)


def load_corpus(root: Path) -> list[Doc]:
    """扫描目录下所有 .md，按编号推断层级与父子关系。"""
    root = Path(root)
    raw: list[dict] = []
    for file in sorted(root.glob("**/*.md")):
        m = _NUMBERED.match(file.name)
        if not m:
            continue
        number, title = m.group(1), m.group(2).strip()
        text = file.read_text(encoding="utf-8")
        meta, body = _parse_front_matter(text)
        parts = number.split(".")
        domain = int(parts[0])
        keywords = _split_list(meta.get("关键词", "")) or _keywords_from_body(body, title)
        raw.append(
            {
                "path": "",  # 稍后按项目根统一计算，保证生成物里的链接可点开
                "abs": file,
                "title": meta.get("标题") or title,
                "domain": domain,
                "level": len(parts) - 1,
                "number": number,
                "roles": meta.get("角色", "客户端,服务端"),
                "keywords": keywords,
                "summary": meta.get("摘要") or _summary_from_body(body),
                "body": body,
            }
        )

    # 相对路径统一按项目根计算，保证 INDEX/KEYWORDS 里的链接可点开
    project_root = root.parent
    for item in raw:
        item["path"] = item["abs"].relative_to(project_root).as_posix()

    by_number = {d["number"]: d["path"] for d in raw}
    docs: list[Doc] = []
    for item in raw:
        parts = item["number"].split(".")
        parent = ""
        for cut in range(len(parts) - 1, 0, -1):
            candidate = ".".join(parts[:cut])
            if candidate in by_number and candidate != item["number"]:
                parent = by_number[candidate]
                break
        docs.append(
            Doc(
                path=item["path"],
                title=item["title"],
                domain=item["domain"],
                level=item["level"],
                number=item["number"],
                parent=parent,
                roles=item["roles"],
                keywords=tuple(item["keywords"]),
                summary=item["summary"],
                body=item["body"],
            )
        )
    return sorted(docs, key=lambda d: (d.domain, [int(x) for x in d.number.split(".")]))
