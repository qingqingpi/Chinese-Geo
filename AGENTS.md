# AGENTS.md — Chinese-Geo

中文 / 国内生态优先的开源 SEO + GEO 工具（命令名 `chinese-geo`）。本文件给任何 AI 编程 Agent（Claude Code / Codex / opencode / CodeBuddy / Qoder / Kimi / Trae 等）读：知道这个项目是什么、怎么用、怎么开发。

## 这是什么
确定性引擎（CLI，纯 Python 标准库、运行时零依赖）+ 中文判断层（Skill）。目标：让网站被国内 AI 引擎（豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi）与海外主流（ChatGPT / Claude / Perplexity / Google AI）抓取与引用。

## CLI 命令
- `chinese-geo audit <url> [--format md|json]` —— 7 维度 AI 可见性体检 → 中文报告 / JSON。
- `chinese-geo bots gen [--sitemap <url>]` —— 生成推荐 robots.txt（国内爬虫各家单独成块）。
- `chinese-geo bots verify <ip> <bot>` —— 反向 DNS 校验爬虫 IP 真伪。
- `chinese-geo schema gen <type>` —— JSON-LD 脚手架（organization / article / faqpage / breadcrumb）。
- `chinese-geo llms gen [--title <X>] [--summary <Y>]` —— llms.txt 脚手架（主要面向海外引擎；国内基本不读）。
- `chinese-geo init [--site <X>] [--sitemap <url>]` —— 站点产物（robots + llms.txt + schema + canonical 清单）；`chinese-geo init --agent <claude|codex|gemini|cursor|generic|codebuddy|kimi|opencode|qoder|trae|lingma>` —— 把 chinese-geo 接入某 agent（写指令文件 + MCP 配置或手动指引，不覆盖已有）。
- `chinese-geo monitor prompts --industry <X>` ｜ `monitor score --answers <f.json> --brand <X>`（零 key 手动）｜ `monitor run --industry <X> --brand <X>`（BYOK 自带 key 自动跑各引擎）—— 引用率 / SoV。
- `chinese-geo offsite [--engine <豆包|元宝|文心|通义|DeepSeek|Kimi>] [--audience b2b|consumer]` —— 国内社媒/站外平台矩阵（按引擎×受众×开放/封闭 + 一题多发），差异化核心。
- `chinese-geo demo` —— 内置 fixture 站「体检→修复→复检」前后分数对比（零 key、零网络、可复现的最小自证）。

未安装命令时用 `python -m seogeo.cli ...`（设 `PYTHONPATH=.`）。

## Skills（判断层，跑在 Agent 里）
- `skills/seogeo-optimize/SKILL.md` —— **全流程总入口**：用户要"从头到尾完整做一遍 GEO / AI 可见性优化"时，按六阶段编排，逐段委派下面的专项 skill。
- `skills/seogeo-audit/SKILL.md` —— AI 可见性体检：调 `audit` → 出中文行动清单。
- `skills/seogeo-structure/SKILL.md` —— 页面结构 / 骨架（答案胶囊、FAQ、表格、schema 对齐）：调 `audit` / `schema`。
- `skills/seogeo-content/SKILL.md` —— 文案改写成可引用形态（结论前置、加数据 / 引文）：几乎纯判断。
- `skills/seogeo-offsite/SKILL.md` —— 站外平台矩阵 + 实体权威层（知乎 / CSDN / 公众号 / 百度百科、sameAs / NAP）。
- `skills/seogeo-monitor/SKILL.md` —— 测引用率 / SoV / GEO 有没有效果：生成问题 → 用户粘回各引擎回答 → 算指标。

SKILL.md 是纯 vendor-neutral Markdown，可移植到任何支持 Agent Skills 的 runtime；不支持的 agent，直接调上面的 CLI 也能拿到主要价值。

## 关键 know-how（落地用）
- 国内爬虫准入：按 RFC 9309，`*` 是标准 catch-all，Baiduspider / PetalBot / 神马 通常遵守；仅 Bytespider / 搜狗 有"合并组被无视、单独成块才停"的站长报告（n=1、非官方）。生成 robots 时各家单独成块属保险做法。
- Bytespider 不守 robots——robots 挡了 ≠ 真挡住，要服务端 / WAF 硬拦。
- 每家 AI 主要"吃自己生态"：豆包 ← 抖音 / 头条、元宝 ← 公众号、文心 ← 百度百科 / 百家号、通义 ← 门户自媒体、DeepSeek / Kimi ← 知乎 / CSDN。
- llms.txt 国内基本无效；GEO 主战场是联网检索。

## 开发约定
- 纯标准库，运行时零依赖（渲染 / MCP 等重能力走 optional-dependencies）。
- 测试：`PYTHONPATH=. python3 -m pytest`。全程 TDD（先写失败测试再写实现）。
- 新增一条体检规则 = 在 `seogeo/rules/` 写一个 `@register` 装饰的函数文件，并加进 `seogeo/rules/__init__.py`（import 即自注册进管线）。
