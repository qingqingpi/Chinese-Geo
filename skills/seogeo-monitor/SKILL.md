---
name: seogeo-monitor
description: 当用户想知道或追踪自己品牌在 AI 引擎（豆包/DeepSeek/文心/通义/元宝/Kimi/ChatGPT 等）里"被不被引用、引用率多少、和竞品比份额（SoV）如何、GEO 有没有效果"时使用——"AI 提不提我"、"豆包会推荐我吗"、"AI 引用率"、"和竞品比 AI 份额"。零 key：生成去品牌化问题让用户粘进各引擎、再把回答粘回来算指标。不用于：网站体检（用 seogeo-audit）。
---

# seogeo · AI 引用率与 SoV 监控（零 key）

衡量"GEO 到底有没有效果"。零 key 做法：让 AI 在**去品牌化问题**下自己推荐，再看引不引你、和竞品比份额多少。

## 流程

1. **问清三件事**：品牌名（+别名/简称）、所在行业/品类、2–4 个主要竞品（+别名）。
2. **生成问题**（确定性、零 key）：
   ```bash
   seogeo monitor prompts --industry "<行业/品类>"
   ```
   得到 12 个去品牌化问题（覆盖 informational / comparison / decision 三阶段）。
3. **让用户逐引擎收集回答**：把这些问题粘进豆包 / DeepSeek / 文心 / 通义 / 元宝 / Kimi（或 ChatGPT / Perplexity 等），每个引擎的回答收集起来。一次不必全跑，先挑 2–3 个主力引擎也行。
4. **整理成 JSON**（你来拼）：`{"豆包": ["回答1","回答2",...], "DeepSeek": [...]}`，每条对应一个问题的回答；存成文件。
5. **算指标**（确定性、零 key）：
   ```bash
   seogeo monitor score --answers <file.json> --brand "<品牌>" --aliases "别名1,别名2" --competitors "竞品A,竞品B"
   ```
6. **解读 + 反推**（你来做）：见下。

> **BYOK 自动档（可选，自带 key）**：配了引擎 API key（环境变量，如 `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `PERPLEXITY_API_KEY` / `DASHSCOPE_API_KEY` / `ARK_API_KEY` / `MOONSHOT_API_KEY`）后，一条命令替你跑完步骤 2–5：
> ```bash
> seogeo monitor run --industry "<行业>" --brand "<品牌>" [--engines deepseek,openai] [--competitors 竞品A,竞品B]
> ```
> 注意：API 模型默认不联网检索（Perplexity 除外），与消费版 App 的联网回答可能不同——要测真实联网引用，仍以手动粘贴（上面的零 key 档）为准。

## 怎么解读

- **引用率** = 被引问题数 ÷ 答题数（按引擎分别算）。基准：**<10% 差 / 10–30% 良 / >30% 优**。
- **SoV（份额）** = 本品牌提及 ÷ 同题全竞品提及。低 = 竞品在抢占这些问题。
- **哪个引擎差就补哪个生态**：豆包差 → 补抖音 / 今日头条；元宝差 → 补微信公众号；文心差 → 补百度百科 / 百家号；DeepSeek / Kimi 差 → 补知乎 / CSDN / 公网媒体。
- **引用率低先回头看体检**（`seogeo-audit`）——是不是爬虫被挡 / 内容不可引用，先把地基补上再谈份额。

## 诚实边界（务必告知用户）
- 这是**抽样近似**，不是引擎官方数据；AI 联网结果会波动、可被操控 → **强调持续追踪（按月重测），不是一次性**。
- 占比 / 基准是经验值，方向可信、数值仅参考。
- 样本越大越准：每个引擎至少 10 个问题。

## Next Best Skill
引用率低 → 回到 `seogeo-audit` 补地基；或按"引擎 → 生态"做站外分发后，过几周重测看是否回升。
