"""优先级建议矩阵 + 报告渲染（JSON 给机器/skill、中文 Markdown 给人）。

优先级逻辑移植自 Auriti `audit.py:build_recommendations`：按桶分类 + 按可恢复分排序；
domestic 类 fail 直接 Critical（seogeo 的差异化最高优先）。
"""
import json

from seogeo.report import AuditResult, build_recommendations, render_json, render_markdown
from seogeo.rules.base import CheckOutcome


def _oc(rid, cat, status, score, mx, rec="改它"):
    return CheckOutcome(id=rid, status=status, message="msg", recommendation=rec,
                        score=score, max_score=mx, category=cat,
                        evidence={"x": 1})


# ---- build_recommendations ----

def test_pass_excluded():
    assert build_recommendations([_oc("a", "technical", "pass", 5, 5, rec="")]) == []


def test_domestic_fail_is_critical():
    recs = build_recommendations([_oc("domestic-bot-access", "domestic", "fail", 0, 20)])
    assert recs[0]["priority"] == "Critical"
    assert recs[0]["points"] == 20


def test_small_gap_is_quick_win():
    recs = build_recommendations([_oc("t", "technical", "warn", 4, 5)])  # gap 1
    assert recs[0]["priority"] == "Quick Win"


def test_sorted_critical_first_then_by_points():
    recs = build_recommendations([
        _oc("t", "technical", "warn", 4, 5),            # gap1 → Quick Win
        _oc("domestic-bot-access", "domestic", "fail", 0, 20),  # Critical, 20
        _oc("d", "discovery", "fail", 0, 8),            # gap8 → Critical
    ])
    assert recs[0]["priority"] == "Critical"
    assert recs[-1]["priority"] == "Quick Win"
    crit = [r for r in recs if r["priority"] == "Critical"]
    assert crit[0]["points"] >= crit[1]["points"]  # domestic(20) 排在 discovery(8) 前


# ---- 渲染 ----

def _result():
    outs = [
        _oc("domestic-bot-access", "domestic", "fail", 0, 20, rec="为 Bytespider 单独成块并 Allow: /"),
        _oc("discovery-sitemap", "discovery", "pass", 8, 8, rec=""),
    ]
    return AuditResult(url="https://example.com", score=29, band="critical",
                       breakdown={"domestic": {"earned": 0, "max": 20},
                                  "discovery": {"earned": 8, "max": 8}},
                       outcomes=outs, recommendations=build_recommendations(outs))


def test_render_json_has_core_keys():
    data = json.loads(render_json(_result()))
    assert data["url"] == "https://example.com"
    assert data["score"] == 29
    assert data["band"] == "critical"
    assert any(c["id"] == "domestic-bot-access" for c in data["checks"])
    assert data["recommendations"][0]["priority"] == "Critical"


def test_render_markdown_has_score_and_critical_section():
    md = render_markdown(_result())
    assert "29/100" in md
    assert "必须修" in md  # 🔴 Critical 分节
    assert "为 Bytespider 单独成块并 Allow: /" in md  # 行动建议文本出现


# ---- 影响引擎 + 验证闭环（让纯 CLI 用户也拿到策略上下文，不必依赖 skill/agent）----

def test_recommendation_carries_affected_engines():
    recs = build_recommendations([_oc("domestic-bot-access", "domestic", "fail", 0, 20)])
    assert recs[0]["engines"]  # 非空
    assert any(k in recs[0]["engines"] for k in ("文心", "豆包", "国内"))  # 点名国内引擎


def test_overseas_recommendation_names_overseas_engines():
    recs = build_recommendations([_oc("overseas-bot-access", "overseas", "fail", 0, 12)])
    assert any(k in recs[0]["engines"] for k in ("ChatGPT", "Perplexity", "海外"))


def test_markdown_shows_affected_engines_and_verify_note():
    md = render_markdown(_result())
    assert "影响引擎" in md
    assert "验证" in md and "monitor" in md  # 验证闭环引导到持续监控


# ---- Track A：每条建议带「怎么验证」（确定性维度→验证步骤映射，非编造）----

def test_recommendation_carries_verify_step():
    recs = build_recommendations([_oc("domestic-bot-access", "domestic", "fail", 0, 20)])
    assert recs[0]["verify"]                 # 非空
    assert "audit" in recs[0]["verify"]      # 引导重跑 audit 复检


def test_verify_is_category_specific():
    dom = build_recommendations([_oc("d", "domestic", "fail", 0, 20)])[0]["verify"]
    struct = build_recommendations([_oc("s", "structure", "fail", 0, 22)])[0]["verify"]
    assert dom != struct                     # 不同维度给不同验证步骤，非一句通用套话
    assert "bots verify" in dom              # domestic 专属：DNS 真伪校验


def test_markdown_shows_per_recommendation_verify():
    md = render_markdown(_result())          # _result() 含一条 domestic 建议
    assert "验证：" in md                     # 每条建议下出现逐条验证步骤
    assert "bots verify" in md               # domestic 项点名其专属校验命令（非全局脚注）


def test_verify_in_json_recommendations():
    data = json.loads(render_json(_result()))
    assert data["recommendations"][0]["verify"]  # JSON 也带 verify（喂 agent/CI）
