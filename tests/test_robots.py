"""robots.txt 解析与按 UA 分类——国内 AI 爬虫准入检查的地基。

关键语义：Bytespider / 搜狗 对仅靠 `*` 覆盖的合规度有争议（站长报告、非官方，最早见
feitsui.com 2020），其余按 RFC 9309 遵守 `*`。所以 classify_bot 既要判 allowed/blocked，
也要分辨命中的是"显式 UA 块"还是"仅靠 * 通配"（via_wildcard）。
"""
from seogeo.robots import classify_bot


def test_no_applicable_rule_is_missing():
    # 只有 Googlebot 的规则，Baiduspider 无任何适用规则
    robots = "User-agent: Googlebot\nDisallow: /private\n"
    c = classify_bot("Baiduspider", robots)
    assert c.status == "missing"


def test_explicit_allow_is_allowed_not_wildcard():
    robots = "User-agent: Baiduspider\nDisallow:\n"
    c = classify_bot("Baiduspider", robots)
    assert c.status == "allowed"
    assert c.via_wildcard is False


def test_wildcard_allow_is_allowed_via_wildcard():
    robots = "User-agent: *\nDisallow:\n"
    c = classify_bot("Baiduspider", robots)
    assert c.status == "allowed"
    assert c.via_wildcard is True


def test_explicit_disallow_root_is_blocked():
    robots = "User-agent: Bytespider\nDisallow: /\n"
    c = classify_bot("Bytespider", robots)
    assert c.status == "blocked"
    assert c.via_wildcard is False


def test_wildcard_disallow_root_is_blocked_via_wildcard():
    robots = "User-agent: *\nDisallow: /\n"
    c = classify_bot("Baiduspider", robots)
    assert c.status == "blocked"
    assert c.via_wildcard is True


def test_exact_match_preferred_over_wildcard():
    # 通配段封禁全站，但 Baiduspider 有自己的放行块——精确匹配优先
    robots = (
        "User-agent: *\nDisallow: /\n\n"
        "User-agent: Baiduspider\nDisallow:\n"
    )
    c = classify_bot("Baiduspider", robots)
    assert c.status == "allowed"
    assert c.via_wildcard is False


def test_consecutive_user_agents_share_one_group():
    # 连续的 User-agent 行共享同一组规则
    robots = (
        "User-agent: Baiduspider\n"
        "User-agent: Sogou web spider\n"
        "Disallow: /\n"
    )
    assert classify_bot("Baiduspider", robots).status == "blocked"
    assert classify_bot("Sogou web spider", robots).status == "blocked"


def test_user_agent_match_is_case_insensitive():
    robots = "User-agent: baiduspider\nDisallow: /\n"
    assert classify_bot("Baiduspider", robots).status == "blocked"


def test_disallow_subpath_keeps_root_allowed():
    # 只封子路径，根路径仍可抓 → 视为 allowed（站点整体可被引用）
    robots = "User-agent: Baiduspider\nDisallow: /admin\n"
    c = classify_bot("Baiduspider", robots)
    assert c.status == "allowed"


def test_allow_overrides_disallow_on_tie():
    # 同长度 Allow 与 Disallow 同时命中 '/' → Allow 胜（最不受限）
    robots = "User-agent: Baiduspider\nDisallow: /\nAllow: /\n"
    c = classify_bot("Baiduspider", robots)
    assert c.status == "allowed"


def test_comments_and_blank_lines_ignored():
    robots = (
        "# 这是注释\n"
        "\n"
        "User-agent: Bytespider   # 行内注释\n"
        "Disallow: /\n"
    )
    assert classify_bot("Bytespider", robots).status == "blocked"
