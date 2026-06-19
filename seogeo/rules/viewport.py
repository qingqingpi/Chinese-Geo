"""technical 类：移动端 viewport（影响移动搜索与 AI 收录）。"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "technical-viewport"
WEIGHT = 6


@register(id=RULE_ID, category="technical", weight=WEIGHT)
def check_viewport(ctx: AuditContext) -> CheckOutcome:
    vp = ctx.dom.metas.get("viewport") if ctx.dom else ""
    if vp:
        return outcome(RULE_ID, WEIGHT, "pass", "已设置移动端 viewport", evidence={"viewport": vp})
    return outcome(RULE_ID, WEIGHT, "warn",
                   "缺少 <meta viewport> —— 移动端体验差，影响移动搜索 / AI 收录",
                   recommendation='加 <meta name="viewport" content="width=device-width, initial-scale=1">',
                   evidence={"viewport": ""})
