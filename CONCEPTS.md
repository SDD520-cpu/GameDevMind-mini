# GitHub 概念速查 + 这次新学到的东西

> 对应部长任务第 1 步「了解 Repository、README、Star 等概念」。
> 账号注册你已完成（`SDD520-cpu`），这里保留清单供复看，重点记这次新碰到的概念。

## 一、基础概念（第一次任务已覆盖）

| 概念 | 一句话 |
| --- | --- |
| **Repository（仓库）** | 项目文件 + 全部修改历史，存在 `.git` 里 |
| **README.md** | 仓库首页默认渲染的说明文档，项目的门面 |
| **Star** | 收藏/点赞，不影响代码；本项目研究对象有 6,689 个 |
| **Fork** | 把别人的仓库完整复制到自己账号下，之后随便改 |
| **Clone** | 把远程仓库下载到本机（`git clone <地址>`） |
| **Commit / Push / Pull** | 一次带说明的存档 / 上传到远程 / 取回远程更新 |
| **Branch** | 独立开发线；老项目常见 `master`，新项目多为 `main` |
| **Issue / Pull Request** | 问题讨论帖 / 请求对方合并你的改动 |
| **License** | 规定别人怎么用你的代码；原项目是 MIT |
| **.gitignore** | 列出不纳入版本管理的文件（`__pycache__`、密钥等） |

## 二、这次新碰到的概念

| 概念 | 在这次任务里对应什么 |
| --- | --- |
| **生成物（generated files）** | `INDEX.md`、`KEYWORDS.md`、`nav/content-data.js` 头部都写着「由 xx.py 自动生成，请勿手动编辑」。改内容要改**输入**（语料），再跑生成器，而不是直接改输出。这是本次复现的核心洞察。 |
| **倒排索引（inverted index）** | 正常是「文档 → 关键词」，倒过来变成「关键词 → 哪些文档」。`KEYWORDS.md` 就是这个结构，所以搜「热更新」能立刻列出跨多个能力域的 5 篇文档。 |
| **front-matter** | Markdown 文件开头用 `---` 包住的元数据区（`关键词: ...`、`角色: ...`）。生成器读它，不用猜正文。 |
| **静态站点 / GitHub Pages** | 原项目 `nav/` 是纯 HTML + JS，部署在 `gonglei007.github.io/GameDevMind/nav/`，不需要后端服务器。 |
| **CI（持续集成）** | 仓库 `.github/` 与 `tools/check/` 里的脚本，在每次提交时自动检查链接、图片、重新生成索引与统计。README 里的「124 篇文档」就是这么保持不旧的。 |
| **Topic / Tag** | 仓库右侧那堆蓝色标签（`unity3d`、`game-server`、`roadmap` 等），用来分类检索。 |
| **Watch / Release** | Watch 数（69）表示关注动态的人数；Tags（7 个）常用于版本发布。 |

## 三、注册账号（已完成，保留备查）

1. https://github.com/signup → 填邮箱、密码、用户名（用户名会成为 `github.com/<用户名>`）；
2. 完成邮箱验证码与人机验证；
3. 计划选 Free；
4. 到邮箱点验证链接激活；建议再开两步验证；
5. 打开一个项目点 Star、往下看渲染后的 README、再点 Fork 感受区别。

> GitHub 早已不支持用账号密码推送代码，需要 Personal Access Token 或 SSH；
> 本机 Git Credential Manager 已缓存授权，所以本次推送没有再输密码。

## 四、读一个陌生项目 README 的方法

按这 4 个问题找答案，比从头读到尾快得多：

1. **解决什么问题？** → 开头一两句 + About 描述；
2. **主要功能？** → 「从这里开始」表、Features 列表；
3. **怎么装 / 怎么跑？** → Requirements / Installation / Usage；
4. **怎么工作的、怎么扩展？** → 目录结构、工具链、贡献指南。

这次的第 4 问有个小技巧：**别只看 README，去翻索引文件的头部注释**。
`INDEX.md` 第 3 行写着「由 `tools/check/generate_catalog.py` 自动生成」，
顺藤摸瓜看 `tools/README.md`，才找到这个项目真正的核心机制 —— 于是复现方向就从
「抄几篇文档」变成了「复现索引生成链路」。
