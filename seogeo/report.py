"""审计结果 + 优先级建议矩阵 + 报告渲染。

- build_recommendations：移植自 Auriti `audit.py`，按桶分类 + 按可恢复分排序；
  domestic 类 fail 直接 Critical（seogeo 差异化最高优先）。
- render_json：机器/skill 用。render_markdown：人话，含优先级矩阵（🔴必须修/🟠重要/🟢快速见效）。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class AuditResult:
    url: str
    score: int
    band: str
    breakdown: dict
    outcomes: list
    recommendations: list = field(default_factory=list)
    duration_ms: int = 0


_PRIO_ORDER = {"Critical": 0, "High": 1, "Quick Win": 2}

# 每类问题修好后利好哪些引擎——让纯 CLI 用户（无 skill/agent）也拿到策略上下文。
_CAT_ENGINES = {
    "domestic": "国内联网引擎：文心/百度AI(Baiduspider)、豆包(Bytespider)、元宝(Sogou)、夸克/通义(YisouSpider)、小艺(PetalBot)",
    "overseas": "海外引擎：ChatGPT、Perplexity、Claude、Google AI（各自爬虫）",
    "discovery": "利于百度/搜狗收录 → 文心、元宝等国内引擎更易检索到",
    "structure": "全引擎通用：结构化数据帮所有 AI 理解实体与问答",
    "content": "全引擎通用：可引用形态对国内外引擎都有效",
    "rendering": "全引擎通用：爬虫拿不到 JS 渲染结果就等于空页",
    "technical": "全引擎通用：语言 / 规范化是被正确收录的底线",
}

# 每类问题"怎么验证修好了"——确定性映射（按维度，引到真实 chinese-geo 命令，非编造）。
_CAT_VERIFY = {
    "domestic": "改完重跑 `chinese-geo audit` 看该项转绿；放行真伪用 `chinese-geo bots verify <ip> <bot>` 校验",
    "overseas": "改完重跑 `chinese-geo audit` 看『海外 AI 爬虫准入』转绿",
    "discovery": "重跑 `chinese-geo audit` 看『AI 可发现性』转绿；并在百度/搜狗资源平台确认 sitemap 已提交",
    "structure": "重跑 `chinese-geo audit` 看『结构化』加分；用 `chinese-geo schema gen <type>` 比对字段、schema.org 校验器验合法性",
    "content": "重跑 `chinese-geo audit` 看『内容可引用性』加分；`chinese-geo structure <url>` 看 H2 / 答案胶囊信号",
    "rendering": "重跑 `chinese-geo audit --render` 看『JS 渲染可见性』转绿；或禁用 JS 看首屏是否仍有正文",
    "technical": "重跑 `chinese-geo audit` 看『技术基线』转绿",
}


def build_recommendations(outcomes) -> list:
    recs = []
    for o in outcomes:
        if o.status == "pass" or not o.recommendation:
            continue
        gap = o.max_score - o.score  # 可恢复分
        if o.category == "domestic" and o.status == "fail":
            prio = "Critical"
        elif gap >= 8:
            prio = "Critical"
        elif gap >= 3:
            prio = "High"
        else:
            prio = "Quick Win"
        recs.append({"priority": prio, "category": o.category, "points": gap,
                     "text": o.recommendation, "rule_id": o.id,
                     "engines": _CAT_ENGINES.get(o.category, ""),
                     "verify": _CAT_VERIFY.get(o.category, "")})
    return sorted(recs, key=lambda r: (_PRIO_ORDER[r["priority"]], -r["points"]))


def render_json(result: AuditResult) -> str:
    return json.dumps({
        "url": result.url,
        "score": result.score,
        "band": result.band,
        "breakdown": result.breakdown,
        "checks": [
            {"id": o.id, "category": o.category, "status": o.status,
             "score": o.score, "max": o.max_score, "message": o.message,
             "recommendation": o.recommendation, "evidence": o.evidence}
            for o in result.outcomes
        ],
        "recommendations": result.recommendations,
        "duration_ms": result.duration_ms,
    }, ensure_ascii=False, indent=2)


_BAND_CN = {"excellent": "优秀", "good": "良好", "foundation": "待打基础", "critical": "亟需整改"}
_CAT_CN = {
    "domestic": "★国内 AI 爬虫准入", "overseas": "海外 AI 爬虫准入",
    "discovery": "AI 可发现性", "structure": "结构化",
    "content": "内容可引用性", "rendering": "JS 渲染可见性", "technical": "技术基线",
}
_PRIO_ICON = {"Critical": "🔴 必须修", "High": "🟠 重要", "Quick Win": "🟢 快速见效"}


def render_markdown(result: AuditResult) -> str:
    lines = [
        f"# chinese-geo 体检报告：{result.url}",
        "",
        f"**总分 {result.score}/100 · 等级：{_BAND_CN.get(result.band, result.band)}**"
        f"（耗时 {result.duration_ms}ms）",
        "",
        "## 分项得分",
        "| 维度 | 得分 |",
        "|---|---|",
    ]
    for cat, b in result.breakdown.items():
        lines.append(f"| {_CAT_CN.get(cat, cat)} | {b['earned']}/{b['max']} |")

    lines += ["", "## 优先级修复清单"]
    if not result.recommendations:
        lines.append("")
        lines.append("🎉 没有发现需要修复的问题。")
    else:
        cur = None
        for r in result.recommendations:
            if r["priority"] != cur:
                cur = r["priority"]
                lines.append(f"\n### {_PRIO_ICON.get(cur, cur)}")
            cat_cn = _CAT_CN.get(r["category"], r["category"])
            lines.append(f"- **[+{r['points']}分 · {cat_cn}]** {r['text']}")
            if r.get("engines"):
                lines.append(f"  - 影响引擎：{r['engines']}")
            if r.get("verify"):
                lines.append(f"  - 验证：{r['verify']}")
        lines += [
            "",
            "> 验证闭环：改完重跑 `chinese-geo audit` 看对应项转绿；上线几周后用 "
            "`chinese-geo monitor` 抽样看引用率 / SoV 是否回升（GEO 要持续监控，不是一次性）。",
        ]
    return "\n".join(lines)
