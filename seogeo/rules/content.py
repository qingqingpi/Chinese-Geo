"""content 类：内容可引用性结构（唯一H1 / 可抽取分节(H2或FAQPage) / 正文足量 / 列表表格）。

正文足量按字符数判定（中文无空格，词数失真）。4 项信号 → pass / warn / fail。
分节信号：H2 小节**或** FAQPage 问答结构均算——FAQPage 提供的问答对本身就是可被 AI
整段抽取的"答案胶囊"，不应因缺 H2 散文而判一个用 FAQPage 做对了的页面内容不达标。
"""
from __future__ import annotations

import json

from seogeo.rules.base import AuditContext, CheckOutcome, html_unavailable, outcome, register

RULE_ID = "content-structure"
WEIGHT = 16
MIN_CHARS = 300


def _has_faqpage(blocks) -> bool:
    """页面是否含 FAQPage JSON-LD（问答结构＝可被 AI 整段抽取的内容，等价于 H2 分节）。"""
    for b in blocks or []:
        try:
            data = json.loads(b)
        except Exception:
            continue
        for item in (data if isinstance(data, list) else [data]):
            t = item.get("@type") if isinstance(item, dict) else None
            if t and "FAQPage" in (t if isinstance(t, list) else [t]):
                return True
    return False


@register(id=RULE_ID, category="content", weight=WEIGHT)
def check_content_structure(ctx: AuditContext) -> CheckOutcome:
    if ctx.html_error:
        return html_unavailable(RULE_ID, WEIGHT, "内容结构")
    if ctx.dom is None and not ctx.html_error:
        return html_unavailable(RULE_ID, WEIGHT, "内容结构")
    d = ctx.dom
    has_h2 = bool(d) and d.headings["h2"] > 0
    has_faq = bool(d) and _has_faqpage(d.jsonld_blocks)
    signals = {
        "single_h1": bool(d) and d.headings["h1"] == 1,
        "extractable_sections": has_h2 or has_faq,  # H2 小节 或 FAQPage 问答，都是可抽取分节
        "enough_text": bool(d) and d.text_length >= MIN_CHARS,
        "has_list_or_table": bool(d) and (d.has_list or d.has_table),
    }
    n = sum(signals.values())
    evidence = {**signals, "has_h2": has_h2, "has_faqpage": has_faq,
                "text_length": d.text_length if d else 0, "signals_met": n}

    if n >= 4:
        return outcome(RULE_ID, WEIGHT, "pass", f"内容结构良好（{n}/4 项可引用性信号）", evidence=evidence)

    missing = []
    if not signals["single_h1"]:
        missing.append("唯一 H1 主标题")
    if not signals["extractable_sections"]:
        missing.append("H2 小节切分或 FAQPage 问答结构（利于 AI 整段抽取）")
    if not signals["enough_text"]:
        missing.append(f"正文≥{MIN_CHARS}字")
    if not signals["has_list_or_table"]:
        missing.append("列表/表格（利于被 AI 抽取引用）")
    status = "warn" if n >= 2 else "fail"
    return outcome(RULE_ID, WEIGHT, status,
                   f"内容结构待改进（{n}/4 项信号）",
                   recommendation="补强：" + "、".join(missing),
                   evidence=evidence)
