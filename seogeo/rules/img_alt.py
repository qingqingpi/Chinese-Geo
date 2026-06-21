"""technical 类：图片 alt 缺失检查。

alt 文本是 AI 与无障碍理解图片的主要途径，缺失则图片对 AI 不可读。
按无障碍约定：`alt=""`（空）是装饰性图片的合法标注，不算缺失，避免误伤。
"""
from __future__ import annotations

from seogeo.rules.base import AuditContext, CheckOutcome, html_unavailable, outcome, register

RULE_ID = "technical-img-alt"
WEIGHT = 6


@register(id=RULE_ID, category="technical", weight=WEIGHT)
def check_img_alt(ctx: AuditContext) -> CheckOutcome:
    if ctx.html_error:
        return html_unavailable(RULE_ID, WEIGHT, "图片 alt")
    images = ctx.dom.images if ctx.dom else 0
    missing = ctx.dom.images_missing_alt if ctx.dom else 0
    evidence = {"images": images, "images_missing_alt": missing}
    if images == 0:
        return outcome(RULE_ID, WEIGHT, "pass", "未发现图片", evidence=evidence)
    if missing == 0:
        return outcome(RULE_ID, WEIGHT, "pass", f"{images} 张图片均有 alt 文本", evidence=evidence)
    return outcome(RULE_ID, WEIGHT, "warn",
                   f"{missing}/{images} 张图片缺 alt 文本 —— AI 无法理解这些图片",
                   recommendation='给图片补 alt 描述（装饰性图片可用 alt="" 显式标注）',
                   evidence=evidence)
