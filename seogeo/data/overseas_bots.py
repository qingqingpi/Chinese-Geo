"""海外主流 AI 爬虫清单（与国内清单并列；国内仍是差异化核心）。

注：海外爬虫普遍遵守 robots 的 `*` 通配，故无需"各家单独成块"。
"""

OVERSEAS_BOTS = {
    "GPTBot": "OpenAI（训练语料）",
    "OAI-SearchBot": "OpenAI（ChatGPT 搜索引用）",
    "ChatGPT-User": "OpenAI（ChatGPT 用户触发抓取）",
    "ClaudeBot": "Anthropic（训练语料）",
    "Claude-User": "Anthropic（Claude 用户触发抓取）",
    "anthropic-ai": "Anthropic",
    "PerplexityBot": "Perplexity（索引）",
    "Perplexity-User": "Perplexity（用户触发抓取）",
    "Google-Extended": "Google（Gemini / AI Overviews 训练令牌）",
    "CCBot": "Common Crawl（被多家 AI 训练采用）",
    "Bingbot": "Microsoft Bing / Copilot",
    "Applebot-Extended": "Apple（AI 训练）",
    "Meta-ExternalAgent": "Meta AI（训练）",
    "Amazonbot": "Amazon",
}
