"""seogeo MCP server（L2 工具层，可选）。

把 CLI 能力暴露为 MCP 工具，让支持 MCP 的 agent（Claude / Codex / Cursor / opencode /
CodeBuddy / Qoder / Kimi 等）以结构化方式调用。需要 `pip install china-geo[mcp]`，运行 `seogeo-mcp`。
"""
from __future__ import annotations

import json

from seogeo.engines import available_engines, run_matrix
from seogeo.generate import generate_llms, generate_robots, generate_schema
from seogeo.monitor import generate_prompts, score_answers
from seogeo.report import render_markdown
from seogeo.service import audit_url

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:  # pragma: no cover
    raise SystemExit("需要 MCP 依赖：pip install china-geo[mcp]") from e

mcp = FastMCP("seogeo")


@mcp.tool()
def audit(url: str) -> str:
    """对网站做 AI 可见性体检（国内 + 海外 AI 引擎），返回中文报告（含打分与优先级修复清单）。"""
    return render_markdown(audit_url(url))


@mcp.tool()
def bots_gen(sitemap_url: str = "") -> str:
    """生成推荐 robots.txt——放行主流 AI 爬虫，国内爬虫各家单独成块。"""
    return generate_robots(sitemap_url=sitemap_url or None)


@mcp.tool()
def schema_gen(schema_type: str) -> str:
    """生成 JSON-LD 脚手架。schema_type ∈ organization / article / faqpage / breadcrumb。"""
    return generate_schema(schema_type)


@mcp.tool()
def llms_gen(title: str, summary: str = "") -> str:
    """生成 llms.txt 脚手架（主要面向海外 AI 引擎；国内引擎基本不读，靠 robots 准入 + 站外分发）。"""
    return generate_llms(title, summary or None)


@mcp.tool()
def monitor_prompts(industry: str) -> list:
    """按行业 / 品类生成去品牌化 prompt 矩阵（用户粘进各 AI 引擎收集回答）。"""
    return [p["text"] for p in generate_prompts(industry)]


@mcp.tool()
def monitor_score(answers_json: str, brand: str, aliases: str = "", competitors: str = "") -> dict:
    """从粘回的回答算引用率 + SoV。

    answers_json: `{"引擎":["回答",...]}` 的 JSON 字符串；aliases / competitors: 逗号分隔。
    """
    answers = json.loads(answers_json)
    alias_list = [a.strip() for a in aliases.split(",") if a.strip()]
    comp = {c.strip(): [] for c in competitors.split(",") if c.strip()}
    return score_answers(answers, brand, alias_list, comp)


@mcp.tool()
def monitor_run(industry: str, brand: str, engines: str = "",
                aliases: str = "", competitors: str = "") -> dict:
    """BYOK：用环境变量里已配置的 API key 自动跑各引擎，算引用率 + SoV。

    engines 留空＝跑所有已配置 key 的引擎；engines / aliases / competitors 逗号分隔。
    注：调的是各引擎 API 模型（默认不联网检索，Perplexity 除外）。
    """
    if not available_engines():
        return {"error": "没有可用引擎：请在环境变量配置至少一个 API key（如 DEEPSEEK_API_KEY）。"}
    only = [e.strip() for e in engines.split(",") if e.strip()] or None
    prompts = [p["text"] for p in generate_prompts(industry)]
    answers = run_matrix(prompts, engines=only)
    alias_list = [a.strip() for a in aliases.split(",") if a.strip()]
    comp = {c.strip(): [] for c in competitors.split(",") if c.strip()}
    return score_answers(answers, brand, alias_list, comp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
