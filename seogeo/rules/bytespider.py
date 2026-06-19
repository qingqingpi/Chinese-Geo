"""Bytespider 强制力检查——"robots 挡了 ≠ 真挡住"。

Bytespider 不遵守 robots：若 robots 想封它，必须服务端 / WAF 按 UA 硬拦才有效。
本检查把 robots 状态与实际探测（ctx.bytespider_blocked）结合判定——这是别家没有的差异化。
"""
from __future__ import annotations

from seogeo.robots import classify_bot
from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "domestic-bytespider-enforce"
WEIGHT = 6


@register(id=RULE_ID, category="domestic", weight=WEIGHT)
def check_bytespider_enforce(ctx: AuditContext) -> CheckOutcome:
    disallowed = bool(ctx.robots_txt) and classify_bot("Bytespider", ctx.robots_txt).status == "blocked"

    if not disallowed:
        return outcome(RULE_ID, WEIGHT, "pass",
                       "Bytespider 未被 robots 封禁——可抓取，利于豆包引用",
                       evidence={"robots_disallow": False})

    blocked = ctx.bytespider_blocked
    if blocked is True:
        return outcome(RULE_ID, WEIGHT, "pass",
                       "robots 封禁 Bytespider 且服务端已硬拦——封禁有效",
                       evidence={"robots_disallow": True, "server_blocked": True})
    if blocked is False:
        return outcome(RULE_ID, WEIGHT, "fail",
                       "robots 挡了 Bytespider，但它不遵守 robots、仍能抓全站",
                       recommendation="Bytespider 无视 robots——要真封禁，请在服务端 / WAF 按 UA=Bytespider 硬拦",
                       evidence={"robots_disallow": True, "server_blocked": False})
    return outcome(RULE_ID, WEIGHT, "warn",
                   "robots 挡了 Bytespider，但它不守 robots；无法确认是否真被拦",
                   recommendation="Bytespider 无视 robots，建议服务端 / WAF 按 UA 硬拦并核实",
                   evidence={"robots_disallow": True, "server_blocked": None})
