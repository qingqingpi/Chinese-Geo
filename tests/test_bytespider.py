"""Bytespider 强制力检查：robots 挡了 ≠ 真挡住（它不守 robots，要服务端硬拦）。"""
from seogeo.rules.base import AuditContext
from seogeo.rules.bytespider import check_bytespider_enforce


def test_allowed_bytespider_passes():
    # robots 允许/未禁 Bytespider → 可抓（利于豆包），无强制问题
    ctx = AuditContext(url="x", robots_txt="User-agent: *\nAllow: /")
    assert check_bytespider_enforce(ctx).status == "pass"


def test_no_robots_passes():
    assert check_bytespider_enforce(AuditContext(url="x")).status == "pass"


def test_disallowed_and_server_blocked_passes():
    ctx = AuditContext(url="x", robots_txt="User-agent: Bytespider\nDisallow: /",
                       bytespider_blocked=True)
    assert check_bytespider_enforce(ctx).status == "pass"


def test_disallowed_but_not_blocked_fails():
    ctx = AuditContext(url="x", robots_txt="User-agent: Bytespider\nDisallow: /",
                       bytespider_blocked=False)
    out = check_bytespider_enforce(ctx)
    assert out.status == "fail"
    assert "硬拦" in out.recommendation or "WAF" in out.recommendation


def test_disallowed_unprobed_warns():
    ctx = AuditContext(url="x", robots_txt="User-agent: Bytespider\nDisallow: /")
    assert check_bytespider_enforce(ctx).status == "warn"


def test_id():
    assert check_bytespider_enforce(AuditContext(url="x")).id == "domestic-bytespider-enforce"
