"""technical 类：HTTPS（AI / 搜索普遍降权 HTTP 站）。"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "technical-https"
WEIGHT = 6


@register(id=RULE_ID, category="technical", weight=WEIGHT)
def check_https(ctx: AuditContext) -> CheckOutcome:
    if ctx.url.lower().startswith("https://"):
        return outcome(RULE_ID, WEIGHT, "pass", "已启用 HTTPS", evidence={"url": ctx.url})
    return outcome(RULE_ID, WEIGHT, "fail",
                   "未启用 HTTPS —— 影响信任与收录，AI / 搜索普遍降权 HTTP 站",
                   recommendation="部署 HTTPS（TLS 证书），并把 HTTP 全量 301 到 HTTPS",
                   evidence={"url": ctx.url})
