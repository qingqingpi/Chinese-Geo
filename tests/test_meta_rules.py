"""加厚的技术/元信息检查：HTTPS / viewport(移动端) / Open Graph / 新鲜度。"""
from seogeo.dom import scan
from seogeo.rules.base import AuditContext
from seogeo.rules.freshness import check_freshness
from seogeo.rules.https import check_https
from seogeo.rules.opengraph import check_og
from seogeo.rules.viewport import check_viewport


def _ctx(url="https://example.com", html=""):
    c = AuditContext(url=url, html=html)
    c.dom = scan(html)
    return c


# ---- HTTPS ----

def test_https_pass():
    assert check_https(_ctx(url="https://x.com")).status == "pass"


def test_http_fails():
    assert check_https(_ctx(url="http://x.com")).status == "fail"


# ---- viewport（移动端）----

def test_viewport_present_pass():
    assert check_viewport(_ctx(html='<meta name="viewport" content="width=device-width">')).status == "pass"


def test_viewport_absent_warns():
    assert check_viewport(_ctx(html="<p>x</p>")).status == "warn"


# ---- Open Graph ----

def test_og_title_and_desc_pass():
    html = '<meta property="og:title" content="T"><meta property="og:description" content="D">'
    assert check_og(_ctx(html=html)).status == "pass"


def test_og_absent_warns():
    assert check_og(_ctx(html="<p>x</p>")).status == "warn"


# ---- 新鲜度（日期信号）----

def test_freshness_via_article_meta_pass():
    assert check_freshness(_ctx(html='<meta property="article:published_time" content="2026-01-01">')).status == "pass"


def test_freshness_via_jsonld_pass():
    html = '<script type="application/ld+json">{"datePublished":"2026-01-01"}</script>'
    assert check_freshness(_ctx(html=html)).status == "pass"


def test_freshness_absent_warns():
    assert check_freshness(_ctx(html="<p>没有任何日期</p>")).status == "warn"
