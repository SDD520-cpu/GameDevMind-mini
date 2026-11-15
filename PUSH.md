# 可选：把复现版推到自己的 GitHub

> 部长任务第 5 步要的「仓库地址」指的是**所研究项目的地址**，即
> `https://github.com/gonglei007/GameDevMind`，`REPORT.md` 里已经写好了。
> 这一步只是加分项：想让部长也看到你自己的复现代码时再做。

## 第 1 步：网页建一个空仓库

1. 登录 `SDD520-cpu` → 右上角 `+` → **New repository**
2. 名字填 `GameDevMind-mini`，选 **Public**
3. **不要**勾选 `Add a README file` / `.gitignore` / `Choose a license`（本地都有了）
4. 点 **Create repository**

## 第 2 步：一条命令推送

开始菜单打开 **Git Bash**：

```bash
cd "C:/Users/周/WorkBuddy/2026-11-14-14-19-51/gamedevmind-mini"
bash tools/publish.sh SDD520-cpu 1119341273@qq.com GameDevMind-mini
```

脚本会完成：初始化仓库 → 配置提交身份 → `git add` → `git commit` → 设置 remote → `git push`。
本机 Git 凭据已缓存（第一次任务推送成功过），一般不会再要密码；
若提示认证，浏览器授权即可，或用 Personal Access Token（不要发给任何人、不要写进文件）。

脚本还会处理本机那个 `CRYPT_E_NO_REVOCATION_CHECK` 证书吊销检查问题：
写入**仅本仓库生效**的 `http.sslBackend=schannel` + `http.schannelCheckRevoke=false`，
只关闭吊销检查，证书校验仍然开启，不改全局配置。

## 第 3 步：拿到成品文案

推送成功后脚本会生成 `MESSAGE_TO_SEND.md`：只含汇报正文、自动补上你自己的仓库地址、
去掉所有内部备注，整段复制连同两张截图发群即可。该文件已在 `.gitignore` 中，不会入库。

完成后地址是：`https://github.com/SDD520-cpu/GameDevMind-mini`

## 常见问题

| 现象 | 处理 |
| --- | --- |
| `repository not found` | 网页仓库名不是 `GameDevMind-mini`，或用户名填错 |
| `Updates were rejected` | 建仓时误勾了 README，先 `git pull --rebase origin main` |
| `CRYPT_E_NO_REVOCATION_CHECK` | 脚本已自动配置；手动可执行 `git config --local http.sslBackend schannel` 与 `git config --local http.schannelCheckRevoke false` |
| `Author identity unknown` | 脚本第二、三个参数填用户名与邮箱 |
