"""国内主流 AI 爬虫准入检查——seogeo 最差异化的一条规则。

语义：
- 封禁国内爬虫 → fail（最高优先修复）。
- Bytespider / 搜狗 仅靠 `*` 放行 → warn（这两家有"合并组被无视、单独成块才停"的站长报告，n=1、非官方）。
- 其余爬虫（Baiduspider / PetalBot / 神马）仅靠 `*` 放行 → pass（按 RFC 9309 遵守 `*`，不扣分）。
- 显式放行或无任何封禁 → pass。
"""
from seogeo.rules.base import AuditContext
from seogeo.rules.domestic_bots import check_domestic_bots


def _ctx(robots):
    return AuditContext(url="https://example.com", robots_txt=robots)


def test_no_robots_passes():
    out = check_domestic_bots(_ctx(None))
    assert out.status == "pass"


def test_blocked_domestic_bot_fails_and_lists_it():
    robots = "User-agent: Bytespider\nDisallow: /\n"
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "fail"
    assert "Bytespider" in out.evidence["blocked"]
    assert out.recommendation


def test_wildcard_only_warns_for_format_sensitive_bots_only():
    # 仅靠 * 放行：Bytespider/搜狗 触发提醒；Baiduspider 等遵守 * → 不扣分。
    robots = "User-agent: *\nDisallow:\n"
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "warn"
    assert "Bytespider" in out.evidence["wildcard_risky"]
    assert "Sogou web spider" in out.evidence["wildcard_risky"]
    assert "Baiduspider" not in out.evidence["wildcard_risky"]
    assert "Baiduspider" in out.evidence["wildcard_ok"]


def test_wildcard_ok_bots_alone_do_not_warn():
    # Bytespider/搜狗 显式放行后，其余仅靠 * → pass（它们遵守 *，不再扣分）。
    robots = ("User-agent: Bytespider\nDisallow:\n\n"
              "User-agent: Sogou web spider\nDisallow:\n\n"
              "User-agent: *\nDisallow:\n")
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "pass"
    assert "Baiduspider" in out.evidence["wildcard_ok"]


def test_all_explicitly_allowed_passes():
    robots = "\n\n".join(
        f"User-agent: {b}\nDisallow:"
        for b in ["Baiduspider", "Bytespider", "PetalBot", "Sogou web spider", "YisouSpider"]
    )
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "pass"


def test_blocked_takes_precedence_over_wildcard_warn():
    robots = "User-agent: *\nDisallow:\n\nUser-agent: Bytespider\nDisallow: /\n"
    out = check_domestic_bots(_ctx(robots))
    assert out.status == "fail"
    assert "Bytespider" in out.evidence["blocked"]


def test_outcome_carries_rule_id():
    assert check_domestic_bots(_ctx(None)).id == "domestic-bot-access"


def test_robots_fetch_error_warns_not_false_pass():
    ctx = AuditContext(url="https://example.com", robots_txt=None, robots_error="HTTP 403")
    out = check_domestic_bots(ctx)
    assert out.status == "warn"
    assert "403" in out.message
    assert out.evidence.get("robots_error") == "HTTP 403"
