"""生成器：把诊断变成可复制的修复产物。

- generate_robots：推荐 robots.txt——国内爬虫"各家单独成块"（差异化核心）、海外爬虫可合并。
- generate_schema：JSON-LD 脚手架（Organization/Article/FAQPage/Breadcrumb）。
"""
import pytest

from seogeo.generate import generate_robots, generate_schema


# ---- robots ----

def test_robots_separate_block_per_domestic_bot():
    out = generate_robots()
    # 每个国内爬虫各自单独成块（合并进 * 会被忽略）
    assert "User-agent: Baiduspider\nAllow: /" in out
    assert "User-agent: Bytespider\nAllow: /" in out
    assert "User-agent: Sogou web spider\nAllow: /" in out


def test_robots_allows_overseas_bots():
    out = generate_robots()
    assert "GPTBot" in out
    assert "PerplexityBot" in out


def test_robots_has_default_allow_all():
    assert "User-agent: *" in generate_robots()


def test_robots_includes_sitemap_when_given():
    out = generate_robots(sitemap_url="https://x.com/sitemap.xml")
    assert "Sitemap: https://x.com/sitemap.xml" in out


def test_robots_notes_bytespider_hardblock():
    # 提示 Bytespider 不守 robots、需服务端硬拦
    out = generate_robots()
    assert "Bytespider" in out
    assert "robots" in out and ("硬拦" in out or "WAF" in out)


def test_robots_can_skip_domestic():
    out = generate_robots(allow_domestic=False)
    assert "Baiduspider" not in out


# ---- schema ----

def test_schema_organization():
    out = generate_schema("organization")
    assert '"@type": "Organization"' in out
    assert "schema.org" in out


def test_schema_faqpage():
    out = generate_schema("faqpage")
    assert "FAQPage" in out
    assert "Question" in out


def test_schema_case_insensitive():
    assert "Article" in generate_schema("Article")


def test_schema_wrapped_in_script_tag():
    assert generate_schema("organization").startswith('<script type="application/ld+json">')


def test_schema_unknown_raises():
    with pytest.raises(ValueError):
        generate_schema("nonsense")
