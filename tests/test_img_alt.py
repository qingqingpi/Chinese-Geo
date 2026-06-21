"""technical 类（D1）：图片 alt 缺失检查——AI 与无障碍都靠 alt 理解图片。"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.img_alt import check_img_alt


def _ctx(html, **kw):
    return AuditContext(url="https://x.com", html=html, dom=scan(html), **kw)


def test_all_images_have_alt_passes():
    out = check_img_alt(_ctx('<img src="a.png" alt="一只猫"><img src="b.png" alt="狗">'))
    assert out.status == "pass"
    assert out.evidence["images"] == 2 and out.evidence["images_missing_alt"] == 0


def test_no_images_passes():
    assert check_img_alt(_ctx("<p>纯文字页面，无图</p>")).status == "pass"


def test_missing_alt_warns_with_counts():
    out = check_img_alt(_ctx('<img src="a.png" alt="有"><img src="b.png"><img src="c.png">'))
    assert out.status == "warn"
    assert out.evidence["images"] == 3
    assert out.evidence["images_missing_alt"] == 2
    assert "alt" in out.recommendation.lower()


def test_empty_alt_not_counted_missing():
    # alt="" 是装饰性图片的合法用法（无障碍约定），不算缺失，避免误伤
    out = check_img_alt(_ctx('<img src="deco.png" alt="">'))
    assert out.status == "pass"
    assert out.evidence["images_missing_alt"] == 0


def test_html_error_warns_unavailable():
    out = check_img_alt(_ctx("", html_error="timeout"))
    assert out.status == "warn"
    assert out.evidence.get("html_unavailable")


def test_registered_in_technical_category():
    from seogeo.rules.base import REGISTRY
    r = REGISTRY.get("technical-img-alt")
    assert r is not None and r.category == "technical"
