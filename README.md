# china-geo

> 中文 / 国内生态优先的开源 **SEO + GEO（生成式引擎优化）** 工具包。
> 让你的网站被**豆包 / DeepSeek / 文心一言 / 通义千问 / 腾讯元宝 / Kimi** 等国内 AI 引擎**抓得到、看得懂、愿意引用**。
> **国内生态是差异化核心，海外主流（ChatGPT / Claude / Perplexity / Google AI）一并覆盖——两个生态，一个工具。**

现有 SEO/GEO 工具几乎全是英文 / 海外生态视角（只盯 ChatGPT / Perplexity，只认 Wikipedia / llms.txt）。**china-geo 把国内这一套补全，同时不丢海外主流**：国内爬虫准入、百度系结构化、知乎 / CSDN / 公众号站外矩阵、国产引擎引用监控——这是海外工具的空白。

> 命令行工具名为 `seogeo`（仓库名 `china-geo`）。

## ✨ 现在能做什么（v0）

一条命令，给你的站做 **AI 可见性体检**：7 个维度打分 + 中文优先级修复清单。

- **★ 国内 AI 爬虫准入** —— robots.txt 是否放行 Baiduspider / Bytespider / PetalBot / Sogou / YisouSpider，并按"**各家须单独成块、合并进 `*` 通配会被忽略**"的真实规则判定。还会探测 **Bytespider 是否真被服务端硬拦**（它不守 robots，robots 挡了≠真挡住），并支持**反向 DNS 校验爬虫 IP 真伪**。**别的工具没有这些。**
- **海外 AI 爬虫准入** —— GPTBot / ClaudeBot / PerplexityBot / Google-Extended 等是否被挡（海外爬虫遵守 `*` 通配，判定规则与国内不同）。
- **AI 可发现性** —— sitemap.xml（百度 / 搜狗提交友好）。
- **结构化数据** —— JSON-LD 存在性与合法性 + Open Graph 标签。
- **内容可引用性** —— 唯一 H1、H2 切分、正文足量（按**中文字符数**，不被"中文没空格"坑到）、列表 / 表格、新鲜度（日期信号）。
- **JS 渲染可见性** —— 检测前端渲染空壳，AI 爬虫是否只看到空白页。
- **技术基线** —— `<html lang>`、HTTPS、移动端 viewport。

确定性引擎，**运行时零依赖**（纯 Python 标准库），可进 CI、可复现。

## 🚀 快速开始

需要 Python 3.9+，无需任何第三方包。

```bash
git clone https://github.com/qingqingpi/china-geo
cd china-geo
pip install -e .

seogeo audit example.com                  # 体检：中文报告
seogeo audit example.com --format json    # 体检：JSON（给 agent / CI）
seogeo bots gen --sitemap https://example.com/sitemap.xml   # 生成推荐 robots.txt（国内各家单独成块）
seogeo bots verify 116.179.32.160 Baiduspider               # 反向 DNS 校验爬虫 IP 真伪
seogeo schema gen faqpage                 # 生成 JSON-LD 脚手架
seogeo llms gen --title "示例科技"          # 生成 llms.txt 脚手架（主要面向海外引擎）
seogeo init --site "示例科技"               # 一键打包 robots+llms+schema+canonical 清单 → seogeo-output/
seogeo monitor prompts --industry "智能客服"     # 生成去品牌化问题（粘进各 AI 引擎收集回答）
```

免安装直接跑：`python -m seogeo.cli audit example.com`

Claude Code 一键装成插件（含 5 个技能 + MCP），以及 Codex / Cursor 等其它 agent 的集成方式，见 **[INSTALL.md](INSTALL.md)**。

### 示例输出

```
# seogeo 体检报告：https://www.example.com
**总分 20/100 · 等级：亟需整改**

## 优先级修复清单
### 🔴 必须修
- [+20分 · ★国内 AI 爬虫准入] 为 Bytespider, PetalBot 各自单独写 User-agent 块并 Allow: /（合并进 * 通配段会被忽略）
- [+16分 · 内容可引用性] 补强：唯一 H1 主标题、H2 小节切分、正文≥300字、列表/表格
- [+16分 · 结构化] 添加 Organization / Article / FAQPage 等 JSON-LD
```

## 🧭 为什么国内要单独一套

每家国内 AI 主要"吃自己生态"：豆包 ← 抖音 / 今日头条，元宝 ← 微信公众号，文心 ← 百度百科 / 百家号，通义 ← 门户自媒体，DeepSeek / Kimi ← 知乎 / CSDN 等公网 UGC。爬虫准入、站外分发、引用监控都与海外完全不同；llms.txt 在国内基本无效，GEO 主战场是"联网检索"而非训练语料。

## 🗺️ 路线图

- [x] CLI `audit`：AI 可见性体检（7 类 12 项检查，确定性引擎）
- [x] CLI 生成半边：`bots gen`（推荐 robots.txt，国内各家单独成块）+ `schema gen`（JSON-LD 脚手架）
- [x] Bytespider 服务端硬拦探测（robots 挡了≠真挡住）+ 反向 DNS 真伪校验（`bots verify`）
- [x] CLI `init` + `llms gen`：一键生成 robots + llms.txt + schema 脚手架 + canonical 自查清单
- [ ] 行动清单：预期效果（量化）+ 影响哪些引擎 + 怎么验证
- [x] 6 个 Agent Skill（vendor-neutral，跑在 Claude Code / Codex / CodeBuddy / Qoder / Kimi 等）：**optimize 全流程总入口** / audit 体检 / structure 结构 / content 文案 / offsite 站外+实体 / monitor 引用率·SoV
- [x] 跨 Agent 指令层（`AGENTS.md` + `CLAUDE.md`，覆盖 Codex / opencode / Cursor / Trae / Kimi 等 30+ agent）
- [x] MCP server（7 工具：audit / bots_gen / schema_gen / llms_gen / monitor_prompts / monitor_run / monitor_score；可选 `pip install china-geo[mcp]`，跑 `seogeo-mcp`）
- [x] Claude 插件一键装（`.claude-plugin/` plugin.json + marketplace + 根 `.mcp.json`）→ 见 [INSTALL.md](INSTALL.md)
- [x] 跨 agent 一键接入：`seogeo init --agent <claude|codex|gemini|cursor|generic>`（写指令文件 + `.mcp.json`，不覆盖已有）
- [x] Claude 斜杠命令（`/seogeo:audit` `/seogeo:monitor`，直接跑 CLI 注入结果）
- [x] CI（GitHub Actions 跑 Python 3.9–3.12 测试）+ 打 GitHub Release 自动发 PyPI
- [x] 引用率 / SoV 监控（零 key 手动抽样，中文友好，真 SoV）：`seogeo monitor` + seogeo-monitor Skill
- [x] 站外矩阵 + 实体权威层（知乎 / CSDN / 公众号 / 小红书…）→ `seogeo-offsite` skill
- [x] BYOK 监控自动跑引擎（自带 key 一条命令跑完各引擎）：`seogeo monitor run`

> ⚠️ 早期阶段（v0）。欢迎 issue / PR。

## 开发

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT © 2026 qingqingpi
