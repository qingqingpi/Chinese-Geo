"""生成器：把诊断变成可复制的修复产物（确定性、零依赖）。

- generate_robots：推荐 robots.txt——国内爬虫"各家单独成块"（对 Bytespider/搜狗 是保险做法；合并组被无视仅这两家有站长报告），
  海外爬虫遵守通配可合并成一块。
- generate_schema：JSON-LD 脚手架（schema.org），带占位符，复制进 <head> 改改即用。
"""
from __future__ import annotations

import json
import os

from seogeo.data.domestic_bots import DOMESTIC_BOTS
from seogeo.data.overseas_bots import OVERSEAS_BOTS


def generate_robots(allow_domestic: bool = True, allow_overseas: bool = True,
                    sitemap_url: str | None = None) -> str:
    lines = [
        "# 由 chinese-geo 生成：放行主流 AI 爬虫",
        "# 注意：Bytespider 不完全遵守 robots；如需限流请在服务端 / WAF 按 UA 硬拦",
        "",
    ]
    if allow_domestic:
        lines.append("# 国内 AI 爬虫——各家单独成块（对 Bytespider/搜狗 是保险做法）")
        for bot in DOMESTIC_BOTS:
            lines += [f"User-agent: {bot}", "Allow: /", ""]
    if allow_overseas:
        lines.append("# 海外 AI 爬虫（遵守通配，可合并成一块）")
        for bot in OVERSEAS_BOTS:
            lines.append(f"User-agent: {bot}")
        lines += ["Allow: /", ""]
    lines += ["User-agent: *", "Allow: /", ""]
    if sitemap_url:
        lines.append(f"Sitemap: {sitemap_url}")
    return "\n".join(lines).rstrip() + "\n"


_SCHEMA_TEMPLATES = {
    "organization": {
        "@context": "https://schema.org", "@type": "Organization",
        "name": "<公司名>", "url": "https://<域名>", "logo": "https://<域名>/logo.png",
        "sameAs": ["<百度百科主页>", "<知乎/微博/官方主页>"],
    },
    "article": {
        "@context": "https://schema.org", "@type": "Article",
        "headline": "<文章标题>",
        "author": {"@type": "Person", "name": "<作者>"},
        "datePublished": "<YYYY-MM-DD>", "dateModified": "<YYYY-MM-DD>",
        "image": "<封面图 URL>",
    },
    "faqpage": {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question", "name": "<问题>",
            "acceptedAnswer": {"@type": "Answer", "text": "<答案，简明直接作答>"},
        }],
    },
    "breadcrumb": {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "<一级栏目>", "item": "https://<域名>/cat"},
            {"@type": "ListItem", "position": 2, "name": "<当前页>"},
        ],
    },
}


def generate_schema(schema_type: str) -> str:
    key = schema_type.lower()
    if key not in _SCHEMA_TEMPLATES:
        raise ValueError(f"未知 schema 类型：{schema_type}（支持：{', '.join(_SCHEMA_TEMPLATES)}）")
    body = json.dumps(_SCHEMA_TEMPLATES[key], ensure_ascii=False, indent=2)
    return f'<script type="application/ld+json">\n{body}\n</script>'


def generate_llms(title: str, summary: str | None = None,
                  links: list | None = None) -> str:
    """生成 llms.txt 脚手架（遵循 llmstxt.org 规范，带占位符）。

    诚实提醒写进文件：llms.txt 国内基本无效，主要面向海外 AI 引擎（ChatGPT /
    Claude / Perplexity）；国内 GEO 主战场是联网检索，靠 robots 准入 + 站外分发。
    """
    summary = summary or "<一句话介绍：你是谁、为谁解决什么问题>"
    rows = links or [("<核心页面标题>", "https://<域名>/<路径>", "<这页讲什么，便于 AI 取用>")]
    out = [
        f"# {title}",
        "",
        f"> {summary}",
        "",
        "<!-- 说明（发布前可删）：llms.txt 主要面向海外 AI 引擎（ChatGPT / Claude / "
        "Perplexity）；国内引擎基本不读，国内 GEO 靠 robots 准入 + 站外分发。 -->",
        "",
        "## 核心页面",
        "",
    ]
    for row in rows:
        text, url = row[0], row[1]
        desc = row[2] if len(row) > 2 else ""
        out.append(f"- [{text}]({url})" + (f": {desc}" if desc else ""))
    out += [
        "",
        "## 可选",
        "",
        "- [关于我们](https://<域名>/about): 团队 / 资质 / 背书（E-E-A-T 信号）",
    ]
    return "\n".join(out).rstrip() + "\n"


_CANONICAL_CHECKLIST = """\
# canonical / meta 逐页自查清单（chinese-geo 生成）

每页都过一遍——这些是 AI 爬虫"看懂并更易引用"的技术底线。

## 每页必备
- [ ] `<html lang="zh-CN">`：声明语言，避免被当成乱码或误判地区
- [ ] `<link rel="canonical" href="https://域名/本页规范地址">`：指向唯一规范 URL，避免重复内容稀释权重
- [ ] `<title>`：每页唯一、含核心关键词，≤ 30 字
- [ ] `<meta name="description">`：60–120 字，结论前置、像在直接回答问题
- [ ] 唯一 `<h1>`：与 title 呼应，全页仅一个
- [ ] 正文 ≥ 300 字，用 h2/h3 切分；关键结论配列表或表格（被引用率更高）

## 社交 / 抓取增强
- [ ] Open Graph：`og:title` / `og:description` / `og:image` / `og:url`
- [ ] 结构化数据：见同目录 schema-*.html，按页面类型选 Article / FAQPage / Organization
- [ ] 图片 `alt`：描述性文字，便于多模态抓取

## 站点级
- [ ] robots.txt（见同目录）：国内爬虫各家单独成块；Bytespider 另在服务端 / WAF 硬拦
- [ ] sitemap.xml：列全可索引页，提交到百度 / 搜狗资源平台
- [ ] HTTPS、移动端自适应、首屏不靠纯前端渲染（AI 爬虫常拿不到 JS 结果）
"""


def build_init_bundle(site_title: str = "<站点名>", sitemap_url: str | None = None,
                      summary: str | None = None) -> dict:
    """一键入门产物包：robots.txt / llms.txt / schema 脚手架 / canonical 清单。"""
    return {
        "robots.txt": generate_robots(sitemap_url=sitemap_url),
        "llms.txt": generate_llms(site_title, summary),
        "schema-organization.html": generate_schema("organization"),
        "canonical-meta-checklist.md": _CANONICAL_CHECKLIST,
    }


_AGENT_MCP_JSON = json.dumps(
    {"mcpServers": {"chinese-geo": {"command": "chinese-geo-mcp", "args": []}}},
    ensure_ascii=False, indent=2,
) + "\n"

# opencode 用键 `mcp`、每个 server 带 `type`（不是通用的 mcpServers）
_OPENCODE_MCP_JSON = json.dumps(
    {"$schema": "https://opencode.ai/config.json",
     "mcp": {"chinese-geo": {"type": "local", "command": ["chinese-geo-mcp"], "enabled": True}}},
    ensure_ascii=False, indent=2,
) + "\n"

# Kimi 的 MCP 是全局 ~/.kimi/mcp.json——不碰用户 home，给可手动粘贴的指引
_KIMI_MCP_SETUP = """\
# Kimi CLI 接入 chinese-geo MCP（手动一步）

Kimi 的 MCP 配置是**全局**的（`~/.kimi/mcp.json`），不在项目内，所以这里不自动写你的 home 目录。
把下面这段并入 `~/.kimi/mcp.json`（已有就合并 `mcpServers`），或用 `kimi --mcp-config-file <此文件>`：

```json
{
  "mcpServers": {
    "chinese-geo": { "command": "chinese-geo-mcp", "args": [] }
  }
}
```

需先 `pip install "Chinese-Geo[mcp]"`，让 `chinese-geo-mcp` 在 PATH 上；指令文件 `AGENTS.md` 已就位，Kimi 自动读到。
"""

# Qoder / 通义灵码 等的 MCP 是 UI-only（设置面板里配、无稳定项目级文件）——不碰其 app 私有路径，给手动指引
_UI_MCP_LABELS = {"qoder": "Qoder", "lingma": "通义灵码 Lingma"}


def _ui_mcp_setup(agent_key: str) -> str:
    label = _UI_MCP_LABELS.get(agent_key, agent_key)
    return (
        f"# {label} 接入 chinese-geo MCP（手动一步）\n\n"
        f"{label} 的 MCP 在**设置面板**里配置（UI-only，无稳定的项目级配置文件），"
        f"所以这里不替你写它的私有路径。\n"
        f"打开 {label} 的 MCP / 工具设置，新增一个 server，把下面这段贴进去：\n\n"
        f"```json\n{_AGENT_MCP_JSON.rstrip()}\n```\n\n"
        f"需先 `pip install \"Chinese-Geo[mcp]\"`，让 `chinese-geo-mcp` 在 PATH 上；"
        f"指令文件已就位，{label} 会自动读到。\n"
    )

_AGENT_BLURB = """\
# chinese-geo —— AI 可见性 / GEO 优化工具（本项目已接入）

让网站被国内（豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi）与海外（ChatGPT / Claude /
Perplexity / Google AI）AI 引擎抓取与引用。做 AI 可见性 / GEO / SEO 时用下面的命令与技能。

## CLI（确定性、零依赖；未装命令时用 `python -m seogeo.cli ...`）
- `chinese-geo audit <url> [--format md|json]` —— 7 维度 AI 可见性体检。
- `chinese-geo bots gen` / `bots verify <ip> <bot>` —— robots（国内各家单独成块）/ 反向 DNS 校验。
- `chinese-geo schema gen <type>` ｜ `llms gen` ｜ `init` —— JSON-LD / llms.txt / 一键打包产物。
- `chinese-geo monitor prompts｜run｜score` —— 引用率 / SoV（零 key 手动 + BYOK 自动）。

## 关键 know-how
- 国内爬虫各家单独成块（对 Bytespider/搜狗 是保险做法）；Bytespider 不完全守 robots，要服务端硬拦。
- 每家 AI 主要"吃自己生态"：豆包←抖音/头条、元宝←公众号、文心←百度百科/百家号、DeepSeek/Kimi←知乎/CSDN。
- llms.txt 国内基本无效；GEO 主战场是联网检索。

## 技能（装了 Claude 插件或克隆了仓库时可用）
optimize（全流程总入口）/ audit / structure / content / offsite / monitor。
"""


# 各 agent 接入落点（指令文件 + MCP 策略）。已核 2025–2026 各家官方约定。
#  standard   → 项目级 MCP 文件（mcpServers），默认 `.mcp.json`；可用 mcp_path 改落点（如 Trae 的 .trae/mcp.json）。
#  opencode   → opencode.json（键 mcp、server 带 type）。
#  kimi       → MCP 是全局 ~/.kimi/mcp.json，不碰 home，给手动指引文件。
#  guidance   → MCP 是 UI-only（设置面板配、无稳定项目文件），不硬写，给 `MCP-SETUP-<agent>.md` 贴 JSON 指引。
_AGENTS = {
    "claude":    {"instruction": "CLAUDE.md", "mcp": "standard"},
    "codex":     {"instruction": "AGENTS.md", "mcp": "standard"},
    "gemini":    {"instruction": "GEMINI.md", "mcp": "standard"},
    "cursor":    {"instruction": ".cursor/rules/seogeo.mdc", "mcp": "standard"},
    "generic":   {"instruction": "AGENTS.md", "mcp": "standard"},
    "codebuddy": {"instruction": "CODEBUDDY.md", "mcp": "standard"},  # CODEBUDDY.md 胜过 AGENTS.md
    "opencode":  {"instruction": "AGENTS.md", "mcp": "opencode"},
    "kimi":      {"instruction": "AGENTS.md", "mcp": "kimi"},
    # A1b：rules-dir 指令 + MCP 多为 UI-only。Qoder 原生读根 AGENTS.md（写它省一套）；
    # Trae 有稳定项目级 .trae/mcp.json；Lingma 的 MCP 跨工程共享、UI-only。
    "qoder":     {"instruction": "AGENTS.md", "mcp": "guidance"},
    "trae":      {"instruction": ".trae/rules/project_rules.md", "mcp": "standard",
                  "mcp_path": ".trae/mcp.json"},
    "lingma":    {"instruction": ".lingma/rules/seogeo.md", "mcp": "guidance"},
}


def build_agent_bundle(agent: str) -> dict:
    """生成某 agent 的接入文件包：指令文件 + MCP 配置（写进用户项目，让该 agent 认得 chinese-geo）。

    MCP 四类：standard 写项目级 MCP 文件（mcpServers，默认 `.mcp.json`，可经 `mcp_path` 改落点，
    如 Trae 的 `.trae/mcp.json`）；opencode 写 `opencode.json`（键 `mcp`、server 带 `type`）；
    kimi 的 MCP 是全局 `~/.kimi/mcp.json`——不碰 home，给手动指引 `MCP-SETUP-kimi.md`；
    guidance 是 UI-only（设置面板配），不硬写其私有路径，给 `MCP-SETUP-<agent>.md` 贴 JSON 指引。
    """
    key = agent.lower()
    if key not in _AGENTS:
        raise ValueError(f"未知 agent：{agent}（支持：{', '.join(_AGENTS)}）")
    spec = _AGENTS[key]
    bundle = {spec["instruction"]: _AGENT_BLURB}
    mcp = spec["mcp"]
    if mcp == "standard":
        bundle[spec.get("mcp_path", ".mcp.json")] = _AGENT_MCP_JSON
    elif mcp == "opencode":
        bundle["opencode.json"] = _OPENCODE_MCP_JSON
    elif mcp == "kimi":
        bundle["MCP-SETUP-kimi.md"] = _KIMI_MCP_SETUP
    elif mcp == "guidance":
        bundle[f"MCP-SETUP-{key}.md"] = _ui_mcp_setup(key)
    return bundle


def write_bundle(bundle: dict, output_dir: str) -> list:
    """把产物包写到 output_dir（含嵌套路径，按需逐层建目录），返回写入的文件路径列表。"""
    written = []
    for name, content in bundle.items():
        path = os.path.join(output_dir, name)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
    return written
