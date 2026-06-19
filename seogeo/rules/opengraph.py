"""structure 类：Open Graph（分享卡片 / 部分 AI 预览靠它拿标题与摘要）。"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "structure-opengraph"
WEIGHT = 6
_CORE = ("og:title", "og:description", "og:image")


@register(id=RULE_ID, category="structure", weight=WEIGHT)
def check_og(ctx: AuditContext) -> CheckOutcome:
    metas = ctx.dom.metas if ctx.dom else {}
    present = [k for k in _CORE if metas.get(k)]
    if {"og:title", "og:description"} <= set(present):
        return outcome(RULE_ID, WEIGHT, "pass",
                       f"已设置 Open Graph（{', '.join(present)}）", evidence={"og": present})
    if present:
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"Open Graph 不全（仅 {', '.join(present)}）",
                       recommendation="补齐 og:title / og:description / og:image", evidence={"og": present})
    return outcome(RULE_ID, WEIGHT, "warn",
                   "缺少 Open Graph 标签 —— 分享卡片 / 部分 AI 预览拿不到标题与摘要",
                   recommendation="加 og:title / og:description / og:image", evidence={"og": []})
