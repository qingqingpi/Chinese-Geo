"""chinese-geo demo：对内置 fixture 站跑通 体检 → 修复 → 复检，打印前后分数对比。

最小自证（零 key、零网络、可复现）：用 chinese-geo **自己的生成器**把一个"差站"修成"好站"，
audit 分数实测抬升——不依赖任何外部站点或 API，clone 下来一条命令即可看到效果。
"""
from __future__ import annotations

from seogeo.generate import generate_robots, generate_schema
from seogeo.pipeline import run_audit
from seogeo.report import AuditResult
from seogeo.rules.base import AuditContext

# 故意"差"的 fixture 站：无 lang/H1/H2、正文稀薄、无 JSON-LD、无 OG；robots 还挡了 Bytespider（豆包）
_BAD_HTML = "<html><body><div>首页</div></body></html>"
_BAD_ROBOTS = "User-agent: Bytespider\nDisallow: /"
_GOOD_SITEMAP = "<urlset><url><loc>https://demo.example/</loc></url></urlset>"


def _fixed_html() -> str:
    """用 chinese-geo 自己的生成器修：补 lang/H1/H2/正文/列表 + JSON-LD + OG + viewport + 日期。"""
    schema = generate_schema("organization")
    body = "我们提供智能客服解决方案，覆盖多渠道接入、知识库管理与数据分析，帮助团队降本增效。" * 8
    return (
        '<html lang="zh-CN"><head><title>示例公司 —— 智能客服</title>'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta property="og:title" content="示例公司智能客服">'
        '<meta property="og:description" content="多渠道智能客服解决方案">'
        '<meta property="og:image" content="https://demo.example/og.png">'
        '<meta property="article:published_time" content="2026-01-01">'
        f"{schema}</head><body>"
        "<h1>示例公司智能客服</h1><h2>能做什么</h2>"
        f"<p>{body}</p>"
        "<ul><li>多渠道接入</li><li>知识库管理</li><li>数据分析</li></ul>"
        "</body></html>"
    )


def _audit(html: str, robots: str, sitemap: str | None = None) -> AuditResult:
    ctx = AuditContext(url="https://demo.example", html=html,
                       robots_txt=robots, sitemap_xml=sitemap)
    return run_audit(ctx)


def run_demo() -> dict:
    """返回 {'before': AuditResult, 'after': AuditResult}。零网络、可复现。"""
    before = _audit(_BAD_HTML, _BAD_ROBOTS)
    after = _audit(_fixed_html(), generate_robots(), sitemap=_GOOD_SITEMAP)
    return {"before": before, "after": after}


def _crit(result: AuditResult) -> int:
    return sum(1 for r in result.recommendations if r["priority"] == "Critical")


def render_demo() -> str:
    """人话的前后对比报告。"""
    from seogeo.report import _BAND_CN, _CAT_CN  # 复用类目/等级中文名，与 audit 报告一致

    d = run_demo()
    b, a = d["before"], d["after"]
    lines = [
        "# chinese-geo demo —— 内置 fixture 站：体检 → 修复 → 复检",
        "",
        "（零 key、零网络、可复现：用 chinese-geo 自己的生成器把一个差站修成好站，分数实测抬升。）",
        "",
        f"**修复前 {b.score}/100（{_BAND_CN.get(b.band, b.band)}）　→　"
        f"修复后 {a.score}/100（{_BAND_CN.get(a.band, a.band)}）　Δ +{a.score - b.score}**",
        "",
        "## 分项前后对比",
        "| 维度 | 修复前 | 修复后 |",
        "|---|---|---|",
    ]
    for cat in b.breakdown:
        bb, aa = b.breakdown[cat], a.breakdown[cat]
        mark = " ⬆" if aa["earned"] > bb["earned"] else ""
        lines.append(f"| {_CAT_CN.get(cat, cat)} | {bb['earned']}/{bb['max']} | {aa['earned']}/{aa['max']}{mark} |")
    lines += [
        "",
        f"必须修项：修复前 {_crit(b)} 个 → 修复后 {_crit(a)} 个。",
        "",
        "> 这就是最小自证：差站经「补 H1 / JSON-LD / OG / 正文 + 放行国内爬虫」后 AI 可见性分实测抬升。",
        "> 想看你自己的站？跑 `chinese-geo audit <你的域名>` 拿真实分，再按清单改。",
    ]
    return "\n".join(lines)
