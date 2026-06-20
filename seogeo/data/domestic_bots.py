"""国内主流 AI 爬虫清单（seogeo 的差异化核心数据）。

这是需要持续维护的数据资产，而非散落常量——单独成文件，便于后续更新。
注：按 RFC 9309，`*` 是标准 catch-all，Baiduspider / PetalBot / 神马 等通常遵守（百度官方文档
明示 `*` 对 Baiduspider 生效）；仅 Bytespider / 搜狗 有"合并组被无视、单独成块才停"的站长报告
（见 BLOCK_FORMAT_SENSITIVE）。
"""

# UA token → 所属引擎/说明
DOMESTIC_BOTS = {
    "Baiduspider": "百度搜索 / 文心一言",
    "Bytespider": "字节 / 豆包（不完全遵守 robots，建议服务端硬拦）",
    "PetalBot": "华为 PetalSearch / 华为 AI",
    "Sogou web spider": "搜狗 / 腾讯元宝（微信搜一搜底层）",
    "YisouSpider": "神马搜索（阿里 / 夸克 / UC）",
}

# 反向 DNS 校验后缀（验证 access.log 里自称某爬虫的 IP 真伪；monitor/日志分析用）
DOMESTIC_BOT_RDNS = {
    "Baiduspider": ".crawl.baidu.com",
    "Bytespider": ".crawl.bytedance.com",
    "PetalBot": ".aspiegel.com",
    "Sogou web spider": ".crawl.sogou.com",
    "YisouSpider": ".crawl.sm.cn",
}

# 仅这两家有"被合并进 `*` / 多 UA 堆叠成一组时仍照爬、各自单独成块后才停"的站长报告（最早见
# feitsui.com 2020，n=1、社区经验、非官方；Bytespider 另有 HAProxy 等多方"整体不守 robots"的
# 观测）。本质是这两家对 robots 排除标准的合规度不完整，而非 `*` 通配本身被无视——按 RFC 9309，
# `*` 是标准 catch-all，Baiduspider / PetalBot / 神马 通常遵守。据此：仅这两家"只靠 `*` 放行"才提醒。
BLOCK_FORMAT_SENSITIVE = {"Bytespider", "Sogou web spider"}
