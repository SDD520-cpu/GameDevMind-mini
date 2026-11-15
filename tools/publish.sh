#!/usr/bin/env bash
# 可选：把复现版推到自己的 GitHub（见 PUSH.md）
# 用法: bash tools/publish.sh <用户名> <邮箱> [仓库名，默认 GameDevMind-mini]
# 只使用用户名与邮箱，不索取、不保存密码或 Token。

set -e
cd "$(dirname "$0")/.."

GH_USER="${1:-}"
GH_EMAIL="${2:-}"
REPO="${3:-GameDevMind-mini}"
if [ -z "$GH_USER" ]; then read -r -p "GitHub username: " GH_USER; fi
if [ -z "$GH_EMAIL" ]; then read -r -p "GitHub email:    " GH_EMAIL; fi
if [ -z "$GH_USER" ] || [ -z "$GH_EMAIL" ]; then
  echo "用户名和邮箱不能为空，已取消。"; exit 1
fi

URL="https://github.com/$GH_USER/$REPO.git"

git init -b main >/dev/null 2>&1 || true
git config user.name "$GH_USER"
git config user.email "$GH_EMAIL"
# 本机 Windows 访问不到证书吊销列表，只关吊销检查，证书校验仍开启
git config --local http.sslBackend schannel
git config --local http.schannelCheckRevoke false

git add .
if git diff --cached --quiet; then
  echo "没有新的改动需要提交。"
else
  git commit -m "feat: reproduce GameDevMind index generation and retrieval"
fi
git branch -M main
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$URL"
else
  git remote add origin "$URL"
fi

echo "推送到: $URL"
echo "- 若弹出浏览器：登录 GitHub 点授权即可"
echo "- 若提示密码：填 Personal Access Token，不是账号密码"
git push -u origin main

python - "$GH_USER" "$REPO" <<'PY'
import sys
from pathlib import Path
user, repo = sys.argv[1], sys.argv[2]
src = Path("REPORT.md").read_text(encoding="utf-8")
parts = src.split("\n---\n", 1)
body = parts[1] if len(parts) > 1 else src
body = body.split("\n## 任务对照自检", 1)[0]
body = body.rstrip().rstrip("-").rstrip()
old_block = "**1｜仓库地址**\n\n`https://github.com/gonglei007/GameDevMind`"
new_block = (
    "**1｜仓库地址**\n\n"
    "原项目：`https://github.com/gonglei007/GameDevMind`\n"
    f"我的复现代码仓库：`https://github.com/{user}/{repo}`"
)
if old_block in body:
    body = body.replace(old_block, new_block, 1)
else:
    # REPORT.md 结构变化时退化为只追加一行，避免丢失地址
    body = body.replace(
        "**1｜仓库地址**",
        "**1｜仓库地址**\n" + f"我的复现代码仓库：`https://github.com/{user}/{repo}`",
        1,
    )
Path("MESSAGE_TO_SEND.md").write_text(
    "# 发给部长的汇报文案（可直接整段复制）\n\n"
    "配套图片：screenshots/run-demo.png · screenshots/nav-demo.png\n\n" + body + "\n",
    encoding="utf-8",
)
PY
echo "完成！仓库地址: https://github.com/$GH_USER/$REPO"
echo "已生成 MESSAGE_TO_SEND.md，整段复制连同两张截图发群即可。"
