"""国内主流 AI 爬虫准入检查——seogeo 最差异化的一条规则。

判定：
- 任一国内爬虫被封禁 → fail（最高优先修复）。
- Bytespider / 搜狗 仅靠 `*` 通配放行 → warn（这两家有"合并组被无视、单独成块才停"的站长报告，n=1、非官方）。
- 其余国内爬虫（Baiduspider / PetalBot / 神马）仅靠 `*` 放行 → pass（按 RFC 9309 遵守 `*`，不扣分）。
- 显式放行、或 robots 对它无任何约束 → pass。
"""
from __future__ import annotations

from seogeo.data.domestic_bots import BLOCK_FORMAT_SENSITIVE, DOMESTIC_BOTS
from seogeo.robots import classify_bot
from seogeo.rules.base import AuditContext, CheckOutcome, outcome, register

RULE_ID = "domestic-bot-access"
WEIGHT = 20


@register(id=RULE_ID, category="domestic", weight=WEIGHT)
def check_domestic_bots(ctx: AuditContext) -> CheckOutcome:
    if ctx.robots_error:
        # 抓取失败/403 ≠ 无 robots。诚实报"无法判定"，不能假装放行。
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"无法获取 robots.txt（{ctx.robots_error}）—— 无法判定国内 AI 爬虫准入",
                       recommendation="确认 robots.txt 可公开访问；若站点对默认 UA 反爬，AI 爬虫可能同样受阻。可换 www 域名或人工核实",
                       evidence={"robots_error": ctx.robots_error})
    if not ctx.robots_txt:
        return outcome(RULE_ID, WEIGHT, "pass",
                       "未发现 robots.txt —— 国内 AI 爬虫默认可抓全站",
                       evidence={"robots": False})

    blocked, wildcard_risky, wildcard_ok, explicit_ok = [], [], [], []
    for bot in DOMESTIC_BOTS:
        c = classify_bot(bot, ctx.robots_txt)
        if c.status == "blocked":
            blocked.append(bot)
        elif c.status == "allowed" and c.via_wildcard:
            # 仅 Bytespider / 搜狗"只靠 * 放行"值得提醒；其余遵守 *，不扣分。
            (wildcard_risky if bot in BLOCK_FORMAT_SENSITIVE else wildcard_ok).append(bot)
        elif c.status == "allowed":
            explicit_ok.append(bot)
        # status == "missing"：robots 对它无约束 → 可抓，不计入问题

    evidence = {"blocked": blocked, "wildcard_risky": wildcard_risky,
                "wildcard_ok": wildcard_ok, "explicit_ok": explicit_ok}

    if blocked:
        # Bytespider 本身不完全守 robots：robots 放行也未必够，可能还要服务端 / WAF 层处理。
        bytespider_note = ("（Bytespider 不完全遵守 robots，必要时还需服务端 / WAF 硬拦）"
                           if "Bytespider" in blocked else "")
        return outcome(RULE_ID, WEIGHT, "fail",
                       f"robots.txt 挡住了国内 AI 爬虫：{', '.join(blocked)}",
                       recommendation=(f"为 {', '.join(blocked)} 各自单独写 User-agent 块并 "
                                       f"Allow: /{bytespider_note}"),
                       evidence=evidence)
    if wildcard_risky:
        return outcome(RULE_ID, WEIGHT, "warn",
                       f"{', '.join(wildcard_risky)} 仅靠通配 * 放行——这两家有合并组被无视的站长报告（社区经验、n=1）",
                       recommendation=("建议为 " + ", ".join(wildcard_risky)
                                       + " 各自单独成块并 Allow: /（非官方、属保险做法；其余国内爬虫遵守 * 通配，无需如此）"),
                       evidence=evidence)
    return outcome(RULE_ID, WEIGHT, "pass",
                   f"国内 AI 爬虫均可正常抓取（显式放行：{', '.join(explicit_ok) or '无显式块且无封禁'}）",
                   evidence=evidence)
