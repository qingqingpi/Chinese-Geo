"""content 类：内容可引用性结构（唯一H1 / H2切分 / 正文足量 / 列表表格）。

正文足量用字符数（中文友好）。
"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.content import check_content_structure


def _ctx(html):
    return AuditContext(url="https://x.com", html=html, dom=scan(html))


_RICH = "<h1>标题</h1><h2>小节</h2><p>" + "内容" * 200 + "</p><ul><li>项</li></ul>"


def test_rich_content_passes():
    assert check_content_structure(_ctx(_RICH)).status == "pass"


def test_thin_content_fails():
    out = check_content_structure(_ctx("<p>太少</p>"))
    assert out.status == "fail"
    assert out.recommendation  # 给出补强建议


def test_partial_warns():
    # 有 H1 + 足量正文，但缺 H2 与列表 → 2/4 信号 → warn
    html = "<h1>标题</h1><p>" + "内容" * 200 + "</p>"
    assert check_content_structure(_ctx(html)).status == "warn"


def test_id():
    assert check_content_structure(_ctx("")).id == "content-structure"


# ── Group D 修复：dom=None 且 html_error 未设时应 warn，不应 fail ──

def test_dom_none_no_html_error_warns_not_fails():
    """dom=None 且 html_error=None → html_unavailable warn（非 fail）。"""
    ctx = AuditContext(url="https://x.com", dom=None, html_error=None)
    out = check_content_structure(ctx)
    assert out.status == "warn", f"期望 warn，实际 {out.status}"


# ── FAQPage 算"可抽取分节"内容信号（H2 或 FAQPage 都满足分节） ──

_FAQ_LD = (
    '<script type="application/ld+json">'
    '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":'
    '[{"@type":"Question","name":"孙鑫是谁?","acceptedAnswer":{"@type":"Answer","text":"AI Agent 产品经理。"}}]}'
    '</script>'
)


def test_faqpage_counts_as_sections_signal_can_pass():
    # H1 + FAQPage(无 H2) + 足量正文 + 列表 → 4/4（FAQ 顶替 H2 的"分节"信号）→ pass
    html = "<h1>标题</h1>" + _FAQ_LD + "<p>" + "内容" * 200 + "</p><ul><li>项</li></ul>"
    assert check_content_structure(_ctx(html)).status == "pass"


def test_faqpage_hero_not_nagged_to_add_h2():
    # 典型 hero：H1 + FAQPage + 列表，正文偏短、无 H2 → warn，但有 FAQPage 就不该再硬要 H2
    html = "<h1>孙鑫</h1>" + _FAQ_LD + "<ul><li>Agent</li></ul><p>一句话简介</p>"
    out = check_content_structure(_ctx(html))
    assert "H2" not in out.recommendation


def test_no_faq_no_h2_still_flags_sections():
    # 回归：既无 H2 又无 FAQPage → 仍提示补"分节"（H2 或 FAQPage）
    html = "<h1>标题</h1><p>" + "内容" * 200 + "</p><ul><li>项</li></ul>"
    out = check_content_structure(_ctx(html))
    assert out.status == "warn"
    assert "H2" in out.recommendation or "FAQ" in out.recommendation
