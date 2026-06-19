"""审计管线：跑全部已注册规则 → 打分 → 建议 → AuditResult。

注：管线用全局 REGISTRY，断言保持对"行为/等级/关键检查结果"稳健，
不硬编码依赖具体检查条数的总分（加检查时总分会变，那是预期的）。
"""
from seogeo.pipeline import run_audit
from seogeo.rules.base import AuditContext

_ALL_ALLOW = "\n\n".join(
    f"User-agent: {b}\nDisallow:"
    for b in ["Baiduspider", "Bytespider", "PetalBot", "Sogou web spider", "YisouSpider"]
)

# 一个"全好"的站：robots 全放行 + sitemap + 含 JSON-LD/标题/足量正文/列表/lang 的 HTML
_GOOD_HTML = (
    '<html lang="zh-CN"><head><title>测试</title>'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<meta property="og:title" content="测试">'
    '<meta property="og:description" content="测试描述">'
    '<meta property="og:image" content="https://example.com/og.png">'
    '<meta property="article:published_time" content="2026-01-01">'
    '<script type="application/ld+json">{"@type":"Organization","name":"测试公司"}</script>'
    "</head><body><h1>主标题</h1><h2>小节</h2>"
    "<p>" + "这是一段实质内容。" * 60 + "</p>"
    "<ul><li>一</li><li>二</li></ul></body></html>"
)


def test_runs_all_registered_rules():
    ctx = AuditContext(url="https://example.com",
                       robots_txt="User-agent: Bytespider\nDisallow: /",
                       sitemap_xml="<urlset></urlset>")
    ids = {o.id for o in run_audit(ctx).outcomes}
    assert {"domestic-bot-access", "discovery-sitemap", "structure-jsonld",
            "content-structure", "technical-lang", "rendering-js-visibility"} <= ids


def test_blocked_domestic_bot_keeps_band_unhealthy():
    # 内容空壳 + 国内爬虫被挡：整体不可能落进健康档（band 阈值随检查增减，断言保持稳健）
    ctx = AuditContext(url="https://example.com",
                       robots_txt="User-agent: Bytespider\nDisallow: /",
                       sitemap_xml="<urlset></urlset>")
    result = run_audit(ctx)
    assert result.band not in ("excellent", "good")
    domestic = next(o for o in result.outcomes if o.id == "domestic-bot-access")
    assert domestic.status == "fail"


def test_builds_critical_recommendation_for_blocked_domestic_bot():
    ctx = AuditContext(url="https://example.com",
                       robots_txt="User-agent: Bytespider\nDisallow: /")
    result = run_audit(ctx)
    assert any(r["priority"] == "Critical" for r in result.recommendations)


def test_fully_good_site_scores_100_excellent():
    ctx = AuditContext(url="https://example.com", robots_txt=_ALL_ALLOW,
                       sitemap_xml="<urlset></urlset>", html=_GOOD_HTML)
    result = run_audit(ctx)
    assert result.score == 100
    assert result.band == "excellent"
    assert result.recommendations == []  # 全 pass → 无修复项


def test_outcomes_carry_category_from_registry():
    ctx = AuditContext(url="https://example.com", robots_txt=_ALL_ALLOW)
    cats = {o.id: o.category for o in run_audit(ctx).outcomes}
    assert cats["domestic-bot-access"] == "domestic"
    assert cats["structure-jsonld"] == "structure"
    assert cats["rendering-js-visibility"] == "rendering"
