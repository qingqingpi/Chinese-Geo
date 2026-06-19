"""爬虫真伪 / 拦截判定。

- looks_blocked：纯逻辑，判断 Bytespider 是否被服务端拦（用 browser-UA vs Bytespider-UA 对比）。
- verify_bot_ip：反向 + 正向 DNS 双向校验某 IP 是否真为该爬虫（reverse/forward 可注入，便于测试）。
- probe_bytespider_blocked：薄网络层，实际跑两次抓取喂给 looks_blocked。
"""
from __future__ import annotations

import socket

from seogeo.data.domestic_bots import DOMESTIC_BOT_RDNS
from seogeo.fetch import fetch

_CHALLENGE = ["just a moment", "checking your browser", "access denied", "captcha", "forbidden", "blocked"]
_BLOCK_STATUS = {403, 429, 451, 503}

_BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/120 Safari/537.36")
_BYTESPIDER_UA = "Mozilla/5.0 (compatible; Bytespider; https://zhanzhang.toutiao.com/)"


def looks_blocked(browser, bot):
    """返回 True/False；任一抓取缺失返回 None。"""
    if not browser or not bot:
        return None
    if bot["status"] in _BLOCK_STATUS:
        return True
    if any(k in (bot.get("text") or "")[:5000].lower() for k in _CHALLENGE):
        return True
    blen, botlen = len(browser.get("text") or ""), len(bot.get("text") or "")
    if browser["status"] == 200 and bot["status"] == 200 and blen > 0 and botlen < 0.3 * blen:
        return True
    return False


def verify_bot_ip(ip: str, bot: str, reverse=None, forward=None) -> bool:
    """反向 + 正向 DNS 双向校验（百度/谷歌官方推荐法）。仅支持有 rDNS 落点的爬虫。"""
    suffix = DOMESTIC_BOT_RDNS.get(bot)
    if not suffix:
        return False
    reverse = reverse or (lambda i: socket.gethostbyaddr(i)[0])
    forward = forward or (lambda h: socket.gethostbyname_ex(h)[2])
    try:
        host = reverse(ip)
        if not host.endswith(suffix):
            return False
        return ip in forward(host)
    except OSError:
        return False


def probe_bytespider_blocked(url: str):
    """实际抓两次（浏览器 UA + Bytespider UA）判断是否被服务端拦。返回 True/False/None。"""
    browser, _ = fetch(url, ua=_BROWSER_UA)
    bot, _ = fetch(url, ua=_BYTESPIDER_UA)
    return looks_blocked(browser, bot)
