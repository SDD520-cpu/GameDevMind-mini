"""
把真实运行结果渲染成两张交付截图：

    python tools/make_screenshot.py

1) run-demo.png  —— demo.py 的真实 stdout（run.log）渲染成终端窗口
2) nav-demo.png  —— 本机 Edge 打开 nav/index.html?q=热更新 的真实页面截图

两次截图的文字/数据都来自本机真实运行，不是手写示意图。
"""

from __future__ import annotations

import html
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "screenshots"
LOG = ROOT / "run.log"

BROWSERS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]

TERM_CSS = """
* { box-sizing: border-box; }
body { margin:0; padding:26px; background:#eef1f5;
  font-family:'Cascadia Code','Consolas','Microsoft YaHei Mono',monospace; }
.window { border-radius:10px; overflow:hidden; background:#12161f;
  box-shadow:0 12px 36px rgba(20,30,50,.22); }
.titlebar { height:38px; background:#232a38; display:flex; align-items:center; padding:0 16px; gap:8px; }
.dot { width:11px; height:11px; border-radius:50%; }
.r{background:#ff5f57}.y{background:#febc2e}.g{background:#28c840}
.title { color:#9aa7bd; font-size:12.5px; margin-left:12px; }
pre { margin:0; padding:18px 22px 22px; color:#d6deeb; font-size:13px; line-height:19px;
  white-space:pre; overflow:hidden;
  font-family:'Cascadia Code','Consolas','Microsoft YaHei Mono',monospace; }
.s-head{color:#82b1ff}.s-cmd{color:#e8edf6}.s-fix{color:#ffd166}.s-ok{color:#7ee2a8;font-weight:bold}
.s-err{color:#ff8a80}.s-sep{color:#4a5670}.s-banner{color:#8ea0bd}.s-pass{color:#7ee2a8}.s-fail{color:#ff8a80}
"""


def colorize(line: str) -> str:
    if "FAIL" in line:
        cls = "s-fail"
    elif line.startswith(". "):
        cls = "s-pass"
    elif line.startswith("# "):
        cls = "s-head"
    elif line.startswith("$ "):
        cls = "s-fix"
    elif line.startswith("> "):
        cls = "s-ok"
    elif line.startswith(("=", "-")):
        cls = "s-sep"
    elif line.startswith("  [") or line.startswith("  ->"):
        cls = "s-cmd"
    elif line.startswith("  gamedev") or line.startswith("  原项目") or line.startswith("  复现") or line.startswith("  环境"):
        cls = "s-banner"
    else:
        cls = "s-banner"
    return f'<span class="{cls}">{html.escape(line)}</span>'


def browser() -> Path | None:
    return next((p for p in BROWSERS if p.exists()), None)


def shot(url: str, png: Path, width: int, height: int, extra: list[str] | None = None) -> bool:
    exe = browser()
    if exe is None:
        print("未找到 Edge/Chrome")
        return False
    cmd = [
        str(exe), "--headless", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--hide-scrollbars",
        "--allow-file-access-from-files", "--virtual-time-budget=2500",
        f"--window-size={width},{height}", f"--screenshot={png}", url,
    ]
    if extra:
        cmd[3:3] = extra
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if png.exists():
        print(f"  {png.name}: {png.stat().st_size} bytes  ({width}x{height})")
        return True
    print(f"  {png.name} 失败: {result.stderr[-500:]}")
    return False


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ok = True

    if not LOG.exists():
        print("缺少 run.log，请先运行 python demo.py")
        return 1

    raw = LOG.read_text(encoding="utf-8").rstrip("\n").splitlines()
    body = "\n".join(colorize(line) for line in raw)
    longest = max((len(line) for line in raw), default=80)
    width = min(1300, max(1000, int(longest * 8.0) + 70))
    height = min(2000, len(raw) * 19 + 120)
    term_html = OUT / "terminal.html"
    term_html.write_text(
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        f"<style>{TERM_CSS}</style></head><body><div class='window'>"
        "<div class='titlebar'><span class='dot r'></span><span class='dot y'></span>"
        "<span class='dot g'></span><span class='title'>bash - python demo.py  |  "
        "gamedevmind-mini 运行演示</span></div>"
        f"<pre>{body}</pre></div></body></html>",
        encoding="utf-8",
    )

    print("生成运行截图：")
    ok &= shot(term_html.as_uri(), OUT / "run-demo.png", width, height)

    nav_url = (ROOT / "nav" / "index.html").as_uri() + "?q=" + quote("热更新")
    print("生成交互式导航截图：")
    ok &= shot(nav_url, OUT / "nav-demo.png", 1100, 980)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
