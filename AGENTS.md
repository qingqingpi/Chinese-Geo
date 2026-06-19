# AGENTS.md — china-geo

中文 / 国内生态优先的开源 SEO + GEO 工具（命令名 `seogeo`）。本文件给任何 AI 编程 Agent（Claude Code / Codex / opencode / CodeBuddy / Qoder / Kimi / Trae 等）读：知道这个项目是什么、怎么用、怎么开发。

## 这是什么
确定性引擎（CLI，纯 Python 标准库、运行时零依赖）+ 中文判断层（Skill）。目标：让网站被国内 AI 引擎（豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi）与海外主流（ChatGPT / Claude / Perplexity / Google AI）抓取与引用。

## CLI 命令
- `seogeo audit <url> [--format md|json]` —— 7 维度 AI 可见性体检 → 中文报告 / JSON。
- `seogeo bots gen [--sitemap <url>]` —— 生成推荐 robots.txt（国内爬虫各家单独成块）。
- `seogeo bots verify <ip> <bot>` —— 反向 DNS 校验爬虫 IP 真伪。
- `seogeo schema gen <type>` —— JSON-LD 脚手架（organization / article / faqpage / breadcrumb）。
- `seogeo monitor prompts --industry <X>` ｜ `seogeo monitor score --answers <f.json> --brand <X>` —— 零 key 引用率 / SoV 抽样。

未安装命令时用 `python -m seogeo.cli ...`（设 `PYTHONPATH=.`）。

## Skills（判断层，跑在 Agent 里）
- `skills/seogeo-audit/SKILL.md` —— 用户要做 AI 可见性体检 / 优化时：调 `audit` → 出中文行动清单。
- `skills/seogeo-monitor/SKILL.md` —— 用户要测引用率 / SoV / GEO 有没有效果时：生成问题 → 用户粘回各引擎回答 → 算指标。

SKILL.md 是纯 vendor-neutral Markdown，可移植到任何支持 Agent Skills 的 runtime；不支持的 agent，直接调上面的 CLI 也能拿到主要价值。

## 关键 know-how（落地用）
- 国内爬虫（Baiduspider / Bytespider / PetalBot / Sogou / YisouSpider）倾向只读精确匹配自己 UA 的块——robots 里各家须单独成块，合并进 `*` 会被忽略。
- Bytespider 不守 robots——robots 挡了 ≠ 真挡住，要服务端 / WAF 硬拦。
- 每家 AI 主要"吃自己生态"：豆包 ← 抖音 / 头条、元宝 ← 公众号、文心 ← 百度百科 / 百家号、通义 ← 门户自媒体、DeepSeek / Kimi ← 知乎 / CSDN。
- llms.txt 国内基本无效；GEO 主战场是联网检索。

## 开发约定
- 纯标准库，运行时零依赖（渲染 / MCP 等重能力走 optional-dependencies）。
- 测试：`PYTHONPATH=. python3 -m pytest`。全程 TDD（先写失败测试再写实现）。
- 新增一条体检规则 = 在 `seogeo/rules/` 写一个 `@register` 装饰的函数文件，并加进 `seogeo/rules/__init__.py`（import 即自注册进管线）。
