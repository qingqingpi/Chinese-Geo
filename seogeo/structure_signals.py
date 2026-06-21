"""结构信号：确定性、**非评分** advisory，给 seogeo-structure 判断层回调。

把"答案胶囊字数 / FAQ / 表格存在"等结构信号下沉成确定性 CLI 能力（D3，含 D2 意图）。
特意不进 audit 评分：答案胶囊字数是经验范围、非硬标准（honesty calibration 0cd528b），
做成信号更诚实——既给判断层可用的数据，又不拿"无定论"的字数去扣分、污染总分。
"""
from __future__ import annotations

import json

from seogeo.dom import scan

# 答案胶囊字数：经验范围、非硬标准。适中区间宽松取 40–150（非空白字符，中文友好）。
_WELL_MIN, _WELL_MAX, _TOO_LONG = 40, 150, 300


def _faqpage_in_jsonld(blocks: list) -> bool:
    for b in blocks:
        try:
            data = json.loads(b)
        except (json.JSONDecodeError, TypeError):
            continue
        for item in (data if isinstance(data, list) else [data]):
            t = item.get("@type") if isinstance(item, dict) else None
            if "FAQPage" in (t if isinstance(t, list) else [t]):
                return True
    return False


def analyze_structure(html: str) -> dict:
    dom = scan(html)
    paras = dom.paragraph_lengths
    return {
        "headings": dict(dom.headings),
        "has_list": dom.has_list,
        "has_table": dom.has_table,
        "faq": {
            "jsonld_faqpage": _faqpage_in_jsonld(dom.jsonld_blocks),
            "question_headings": sum(1 for t in dom.heading_texts if t.endswith(("？", "?"))),
        },
        "capsule": {
            "paragraphs": len(paras),
            "well_sized": sum(1 for n in paras if _WELL_MIN <= n <= _WELL_MAX),
            "too_long": sum(1 for n in paras if n > _TOO_LONG),
            "note": (f"答案胶囊字数为经验范围（约 {_WELL_MIN}–{_WELL_MAX} 字）、非硬标准；"
                     "结论先行的短段更易被 AI 抽取引用。"),
        },
    }


def render_structure(signals: dict, fmt: str = "md") -> str:
    if fmt == "json":
        return json.dumps(signals, ensure_ascii=False, indent=2)
    h, cap, faq = signals["headings"], signals["capsule"], signals["faq"]
    return "\n".join([
        "# chinese-geo 结构信号（确定性、**非评分** — 供 structure 判断层参考）",
        "",
        "## 骨架",
        f"- 标题层级：H1×{h['h1']} · H2×{h['h2']} · H3×{h['h3']}（H1 宜唯一、H2 切分小节）",
        f"- 列表：{'有' if signals['has_list'] else '无'} ｜ 表格：{'有' if signals['has_table'] else '无'}"
        "（列表 / 表格利于被 AI 抽取）",
        f"- FAQ 信号：JSON-LD FAQPage {'有' if faq['jsonld_faqpage'] else '无'} ｜ "
        f"问句式小标题 {faq['question_headings']} 个",
        "",
        "## 答案胶囊（段落字数分布）",
        f"- 段落数 {cap['paragraphs']} ｜ 适中（{_WELL_MIN}–{_WELL_MAX}字）{cap['well_sized']} ｜ "
        f"过长（>{_TOO_LONG}字）{cap['too_long']}",
        f"- 提示：{cap['note']}",
    ])
