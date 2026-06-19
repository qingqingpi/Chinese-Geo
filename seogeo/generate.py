"""生成器：把诊断变成可复制的修复产物（确定性、零依赖）。

- generate_robots：推荐 robots.txt——国内爬虫"各家单独成块"（差异化核心；合并进 * 可能被忽略），
  海外爬虫遵守通配可合并成一块。
- generate_schema：JSON-LD 脚手架（schema.org），带占位符，复制进 <head> 改改即用。
"""
from __future__ import annotations

import json

from seogeo.data.domestic_bots import DOMESTIC_BOTS
from seogeo.data.overseas_bots import OVERSEAS_BOTS


def generate_robots(allow_domestic: bool = True, allow_overseas: bool = True,
                    sitemap_url: str | None = None) -> str:
    lines = [
        "# 由 seogeo 生成：放行主流 AI 爬虫",
        "# 注意：Bytespider 不完全遵守 robots；如需限流请在服务端 / WAF 按 UA 硬拦",
        "",
    ]
    if allow_domestic:
        lines.append("# 国内 AI 爬虫——各家单独成块（合并进 * 可能被忽略）")
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
            "acceptedAnswer": {"@type": "Answer", "text": "<答案，40–75 字直接作答>"},
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
