# 在通义灵码 Lingma（阿里）里用 chinese-geo

> chinese-geo（命令 `chinese-geo`）：让网站被国内（豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi）与
> 海外（ChatGPT / Claude / Perplexity / Google AI）AI 引擎抓取与引用。本卡＝在通义灵码里的装法 + 调法 + 真实输出。

## 1. 装 CLI（必装，运行时零依赖）
```bash
pip install Chinese-Geo            # 得到 chinese-geo 命令
pip install "Chinese-Geo[mcp]"     # 想用 MCP 再加（得到 chinese-geo-mcp）
```

## 2. 接入通义灵码
```bash
chinese-geo init --agent lingma
```
写入（已存在则跳过，不覆盖）：
- `.lingma/rules/seogeo.md` —— 通义灵码的项目规则（指令）文件
- `MCP-SETUP-lingma.md` —— **手动一步**：灵码的 MCP 是 UI-only、跨工程共享，
  不替你写其私有路径；打开灵码的 MCP 设置，把文件里的 JSON 贴进去

> 置信：指令落点高；MCP 为 UI-only（以灵码设置面板为准）；Skills 目录官方未证实，可先用 CLI / MCP。

## 3. 调法
- **CLI 直调**（永远可用，且不依赖任何上层支持）：让灵码跑 `chinese-geo audit <你的域名>`。
- **MCP 工具**：按 `MCP-SETUP-lingma.md` 在设置里配好后，`chinese-geo` 的 8 个工具可调。

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
- audit：7 维度打分 + 中文优先级修复清单，退出码非 0 = 有必修项（可进 CI）。
- 抓取失败不会瞎打分：抓不到首页 / robots 时显示"无法获取…无法判定"。
- 国内差异化：国内爬虫各家单独成块、Bytespider 硬拦探测、`chinese-geo offsite` 国内社媒矩阵。
