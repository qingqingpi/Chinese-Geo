"""国内社媒 / 站外平台矩阵——差异化核心数据（每家 AI 主要"吃自己生态"）。

多角度：每个平台标注「被哪个 websearch 索引 → 喂哪些国内 AI 引擎 × 受众(b2b/consumer) × 开放/封闭」。
因果链：平台 → 被某搜索索引 → 引擎的"联网后端"用那个搜索 → 引用。各引擎联网后端：
文心/百度AI←百度、元宝←微信搜一搜(底层搜狗)、豆包←头条+抖音搜索、通义/夸克←夸克、
DeepSeek/Kimi←后端不透明(公网抓取，常被指走 Bing)。

来源：项目深度调研（方向可信、占比为单行业样本，数值仅参考；知识截至 2026-01，搜索后端会变）。
海外工具完全没有这套。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    name: str
    engines: tuple      # 喂哪些国内 AI 引擎（豆包/元宝/文心/通义/DeepSeek/Kimi）
    audiences: tuple    # "b2b"（B2B/科技）/ "consumer"（消费/生活），可多
    open: bool          # True=公网可被外部搜索索引；False=封闭，需做平台内 SEO
    tip: str
    indexed_by: str = ""  # 被哪些 websearch 索引（决定能喂到哪个引擎的联网后端）


DOMESTIC_PLATFORMS = (
    Platform("微信公众号", ("元宝",), ("b2b", "consumer"), True,
             "元宝主力（约占其引用一半）", indexed_by="搜狗独家（微信搜一搜=搜狗；外部百度/Google 基本搜不到正文）"),
    Platform("知乎", ("DeepSeek", "Kimi", "文心"), ("b2b", "consumer"), True,
             "跨引擎高价值，重论证", indexed_by="百度 / Bing / Google / 搜狗（广泛）"),
    Platform("CSDN", ("DeepSeek", "Kimi", "文心"), ("b2b",), True,
             "开发者技术内容", indexed_by="百度 / Bing / Google（广泛，SEO 友好）"),
    Platform("掘金", ("DeepSeek", "Kimi"), ("b2b",), True,
             "前端 / 开发者", indexed_by="百度 / Bing / Google"),
    Platform("人人都是产品经理", ("DeepSeek",), ("b2b",), True,
             "产品 / B2B", indexed_by="百度 / Bing / Google"),
    Platform("百家号", ("文心",), ("b2b", "consumer"), True,
             "百度系，原创同步", indexed_by="百度独家优先（百度自家产品，结果页权重高）"),
    Platform("百度百科", ("文心",), ("b2b", "consumer"), True,
             "实体权威锚点（E-E-A-T）", indexed_by="百度优先；Bing / Google 次之"),
    Platform("门户自媒体（网易号/企鹅号/搜狐号）", ("通义",), ("b2b", "consumer"), True,
             "搜狐权重普遍高", indexed_by="百度 / 夸克 / 神马 / Bing（广泛）"),
    Platform("今日头条 / 头条号", ("豆包",), ("consumer", "b2b"), True,
             "字节系，喂豆包", indexed_by="头条搜索（字节自家）；百度索引不到（字节-百度互屏）"),
    Platform("抖音", ("豆包",), ("consumer",), False,
             "抖音内 AI 只引抖音 → 做平台内 SEO", indexed_by="抖音搜索（封闭）；外部基本不可索引"),
    Platform("小红书", ("豆包", "通义"), ("consumer",), False,
             '自家"点点"只引小红书 → 也要做平台内', indexed_by="站内 / 点点（近封闭）；外部收录极少（robots 严 + 登录墙）"),
    Platform("B站", ("豆包", "通义"), ("consumer", "b2b"), True,
             "视频 + 图文，科技区偏 b2b", indexed_by="百度 / Bing / Google（广泛）"),
    Platform("视频号", ("元宝",), ("consumer",), True,
             "腾讯系，喂元宝", indexed_by="微信搜一搜（搜狗系）；外部弱"),
)
