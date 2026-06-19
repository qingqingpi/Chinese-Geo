"""爬虫真伪/拦截判定（纯逻辑，依赖注入，可离线测）。

- looks_blocked：用 browser-UA 与 Bytespider-UA 两次抓取，判断 Bytespider 是否被服务端拦。
- verify_bot_ip：反向 + 正向 DNS 双向校验某 IP 是否真为该爬虫（注入 resolver 离线测）。
"""
from seogeo.botverify import looks_blocked, verify_bot_ip


# ---- looks_blocked ----

def test_blocked_when_bot_gets_403():
    assert looks_blocked({"status": 200, "text": "x" * 1000}, {"status": 403, "text": "forbidden"}) is True


def test_blocked_when_challenge_page():
    assert looks_blocked({"status": 200, "text": "x" * 1000},
                         {"status": 200, "text": "Just a moment... checking your browser"}) is True


def test_blocked_when_bot_content_much_shorter():
    assert looks_blocked({"status": 200, "text": "x" * 1000}, {"status": 200, "text": "x" * 100}) is True


def test_not_blocked_when_similar():
    assert looks_blocked({"status": 200, "text": "x" * 1000}, {"status": 200, "text": "x" * 900}) is False


def test_none_when_probe_missing():
    assert looks_blocked(None, {"status": 200, "text": "x"}) is None
    assert looks_blocked({"status": 200, "text": "x"}, None) is None


# ---- verify_bot_ip（注入 reverse/forward）----

def test_genuine_baiduspider():
    assert verify_bot_ip("1.1.1.1", "Baiduspider",
                         reverse=lambda ip: "baidu.crawl.baidu.com",
                         forward=lambda h: ["1.1.1.1"]) is True


def test_fake_wrong_suffix():
    assert verify_bot_ip("1.2.3.4", "Baiduspider",
                         reverse=lambda ip: "evil.example.com",
                         forward=lambda h: ["1.2.3.4"]) is False


def test_fake_forward_mismatch():
    assert verify_bot_ip("1.2.3.4", "Baiduspider",
                         reverse=lambda ip: "x.crawl.baidu.com",
                         forward=lambda h: ["9.9.9.9"]) is False


def test_unknown_bot_is_false():
    assert verify_bot_ip("1.2.3.4", "UnknownBot",
                         reverse=lambda ip: "x", forward=lambda h: ["1.2.3.4"]) is False


def test_dns_failure_is_false():
    def boom(_):
        raise OSError("dns fail")
    assert verify_bot_ip("1.2.3.4", "Baiduspider", reverse=boom, forward=lambda h: []) is False
