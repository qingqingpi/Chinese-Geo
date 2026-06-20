# 在 Claude Code 里用 chinese-geo

> chinese-geo（命令 `chinese-geo`）：让网站被国内（豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi）与
> 海外（ChatGPT / Claude / Perplexity / Google AI）AI 引擎抓取与引用。本卡＝在 Claude Code 里的装法 + 调法 + 真实输出。

## 1. 装 CLI（必装，运行时零依赖）
```bash
pip install Chinese-Geo            # 得到 chinese-geo 命令（纯标准库）
pip install "Chinese-Geo[mcp]"     # 想用 MCP 再加（得到 chinese-geo-mcp）
```

## 2. 接入 Claude Code
**最省事：一键插件**（含 6 个技能 + MCP）
```
/plugin marketplace add qingqingpi/Chinese-Geo
/plugin install chinese-geo
```
**或：一键写接入文件**
```bash
chinese-geo init --agent claude
```
写入（已存在则跳过，不覆盖）：
- `CLAUDE.md` —— 指令文件，Claude Code 自动读到，知道何时调 chinese-geo
- `.mcp.json` —— 注册 `chinese-geo` MCP 服务（需 `chinese-geo-mcp` 在 PATH）

## 3. 调法
- **斜杠命令**：`/chinese-geo:seogeo-optimize`（全流程总入口）、`seogeo-audit` / `-structure` / `-content` / `-offsite` / `-monitor`；以及 `/chinese-geo:audit`、`/chinese-geo:monitor`。
- **MCP 工具**：装了 `[mcp]` 后，`chinese-geo` 的 8 个工具（audit / bots_gen / schema_gen / llms_gen / monitor_* / offsite）可直接调。
- **CLI 直调**（永远可用）：让 Claude 跑 `chinese-geo audit <你的域名>`。

## 4. 真实 CLI 输出样例（`chinese-geo audit https://example.com`）
```
# chinese-geo 体检报告：https://example.com
**总分 63/100 · 等级：待打基础**

| 维度 | 得分 |
|---|---|
| ★国内 AI 爬虫准入 | 26/26 |
| 内容可引用性 | 4/24 |
| 结构化 | 3/22 |
...
### 🔴 必须修
- [+16分 · 内容可引用性] 补强：H2 小节切分、正文≥300字、列表/表格
- [+16分 · 结构化] 添加 Organization / Article / FAQPage 等 JSON-LD
```
完整三命令（audit / offsite / monitor）真实输出见 **[cli-output-samples.md](cli-output-samples.md)**。

## 5. 预期看到什么
- audit：7 维度打分 + 中文优先级修复清单（🔴必须修 / 🟠重要），退出码非 0 = 有必修项（可进 CI）。
- 抓取失败不会瞎打分：抓不到首页 / robots 时相关项显示"无法获取…无法判定"，提示先确认可访问。
- 国内差异化：robots 里国内各家单独成块、Bytespider 硬拦探测、`chinese-geo offsite` 的国内社媒矩阵——海外工具没有。
