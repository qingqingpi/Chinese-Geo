"""content 类：新鲜度信号（AI 联网偏好新内容，需要可判断的时效）。"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "content-freshness"
WEIGHT = 8
_DATE_META = ("article:published_time", "article:modified_time", "date")


@register(id=RULE_ID, category="content", weight=WEIGHT)
def check_freshness(ctx: AuditContext) -> CheckOutcome:
    d = ctx.dom
    metas = d.metas if d else {}
    jsonld = " ".join(d.jsonld_blocks) if d else ""
    has_date = (any(metas.get(k) for k in _DATE_META)
                or "datePublished" in jsonld or "dateModified" in jsonld)
    if has_date:
        return outcome(RULE_ID, WEIGHT, "pass", "含日期 / 新鲜度信号", evidence={"has_date": True})
    return outcome(RULE_ID, WEIGHT, "warn",
                   "未见日期 / 新鲜度信号 —— AI 联网偏好新内容，难判断时效",
                   recommendation="加可见更新日期 + JSON-LD datePublished/dateModified（或 article:published_time）",
                   evidence={"has_date": False})
