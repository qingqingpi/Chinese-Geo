# 在 opencode 里用 chinese-geo

> chinese-geo（命令 `chinese-geo`）：让网站被国内（豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi）与
> 海外（ChatGPT / Claude / Perplexity / Google AI）AI 引擎抓取与引用。本卡＝在 opencode 里的装法 + 调法 + 真实输出。

## 1. 装 CLI（必装，运行时零依赖）
```bash
pip install Chinese-Geo            # 得到 chinese-geo 命令
pip install "Chinese-Geo[mcp]"     # 想用 MCP 再加（得到 chinese-geo-mcp）
```

## 2. 接入 opencode
```bash
chinese-geo init --agent opencode
```
写入（已存在则跳过，不覆盖）：
- `AGENTS.md` —— 指令文件，opencode 自动读到（回退 `CLAUDE.md`）
- `opencode.json` —— MCP 配置。**注意 opencode 用键 `mcp`（不是通用的 `mcpServers`），且每个 server 带 `type`：**
  ```json
  { "mcp": { "chinese-geo": { "type": "local", "command": ["chinese-geo-mcp"], "enabled": true } } }
  ```

## 3. 调法
- **CLI 直调**（永远可用）：让 opencode 跑 `chinese-geo audit <你的域名>`。
- **MCP 工具**：`opencode.json` 就位后，`chinese-geo` 的 8 个工具可调。
- **Skills**：opencode 复用 `.claude/skills/`、`~/.claude/skills/`。

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
