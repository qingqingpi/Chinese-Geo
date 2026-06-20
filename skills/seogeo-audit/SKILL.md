---
name: seogeo-audit
description: 当用户想检查或优化自己网站在 AI 引擎里的可见性时使用——"我的站在豆包/DeepSeek 上能不能被引用"、"AI 搜索优化"、"GEO/SEO 体检"、"AI 引不引用我"、"被 AI 抓取吗"、"怎么让 ChatGPT/文心提到我"。会运行 seogeo CLI 做确定性体检，再给出中文优先级行动清单。不用于：通用写作、与本站无关的泛泛 SEO 咨询。
---

# seogeo · AI 可见性体检与优化

把"确定性体检（CLI）"和"判断型策略（你来做）"结合：CLI 给可验证的发现与打分，你把它翻译成用户能照着做的**中文行动清单**。

## Quick Start

用户给出域名后：

1. 运行体检（确定性、零 key、零依赖）：
   ```bash
   seogeo audit <域名> --format json
   ```
   未安装命令时用：`python -m seogeo.cli audit <域名> --format json`
2. 读取返回的 JSON：`score` / `band` / `breakdown` / `checks[]` / `recommendations[]`。
3. 按下面「输出」一节，给用户一份中文行动清单——每条绑住体检发现，并补上"预期效果 + 影响哪些引擎 + 怎么验证"。

## 输出：把体检结果变成行动清单

先给一句话总览：`总分 X/100（等级）`，再逐条展开 `recommendations[]`（已按 Critical → High → Quick Win 排好）。每条输出：

- **问题**：来自该 check 的 `message`（引具体数据 / 被挡的爬虫）。
- **怎么改**：来自 `recommendation`（含可复制的 robots / schema / 文案片段）。
- **预期效果**：查下方《手法 → 提升》表，给量化区间（如"加统计数字 → 约 +33% 可见度"）。
- **影响哪些引擎**：直接用 JSON 的 `recommendations[].engines`（CLI 已按类给出）；要细化站外分发再查下方《引擎 → 生态》表。
- **怎么验证**：重跑 `seogeo audit` 看该项转绿；隔几周看引用率是否回升（强调持续监控，不是一次性）。

按引擎差异化给站外建议：B2B / 科技 → 公众号 + 知乎 + CSDN（喂 DeepSeek / 文心 / 元宝）；消费 / 生活 → 小红书 + 抖音 + B站（喂 豆包 / 通义）。

## 参考数据

### 引擎 → 生态（每家 AI 主要"吃自己生态"）
| 引擎 | 主要引用生态 |
|---|---|
| 豆包 | 抖音 / 今日头条 / 抖音百科 |
| 腾讯元宝 | 微信公众号 / 视频号 |
| 文心 / 百度AI搜索 | 百度百科 / 百家号 |
| 通义 / 夸克 | 门户自媒体（网易 / 企鹅 / 搜狐号） |
| DeepSeek / Kimi | 公网媒体 + 知乎 / CSDN |
| ChatGPT / Perplexity / Claude / Google AI | Wikipedia / Reddit / 权威媒体 |

### 手法 → AI 可见度提升（Princeton 等 GEO 论文的**模拟引擎**实验，非真实 AI 搜索；方向可信、数值仅参考）
加引用来源 +27~115% ｜ 加统计数字 +33~37% ｜ 加专家引文 +28~41% ｜ 提升流畅度 +15~30% ｜ 权威语气 +16~25% ｜ 结论前置 +25% ｜ 关键词堆砌 −10%（有害，别做）。

## 诚实边界（务必如实告知用户）
- 体检反映的是"我们的爬虫 UA 抓到的 HTML"；反爬站可能返回简化页，`content` / `structure` 可能被低估（`rendering` 的"可见文本很少"会提示这一点）。
- 当前只测"能不能被抓 / 具备被引用的就绪度"，**不是真实引用率**——真实引用率 / SoV 用 `seogeo-monitor`（零 key 抽样）。
- 数值类提升是研究估计，按区间表述，**别承诺确数**。

## Next Best Skill
按问题类型转交专项 skill：结构骨架 → `seogeo-structure`；文案改写 → `seogeo-content`；站外分发 + 实体权威 → `seogeo-offsite`；改完验证效果 → `seogeo-monitor`（引用率 / SoV）。
