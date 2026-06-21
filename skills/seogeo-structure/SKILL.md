---
name: seogeo-structure
description: 当用户想优化页面"结构/骨架"让 AI 更易抽取引用时使用——"内容 AI 抓了但不引用"、"怎么排版 AI 才爱用"、"答案胶囊/FAQ/表格怎么做"、"标题层级/分块"、"schema 和正文对不上"。先跑 chinese-geo audit/schema 看结构项，再给重排建议。不用于：纯文案改写（用 seogeo-content）、站外分发（用 seogeo-offsite）。
---

# chinese-geo · 结构优化（让 AI 抽得动、愿意引）

AI 引用的是"块"，不是整页。把页面拆成自包含、可直接抽取的单元，被引概率上升——结构化形态（表格、列表）更易被整段抽取（业界普遍观察；具体倍数随研究口径差异很大，无统一权威数字）。

## 流程

1. 先体检结构项（确定性、零 key）：
   ```bash
   chinese-geo audit <域名> --format json
   ```
   未安装命令时用 `python -m seogeo.cli audit <域名> --format json`。重点看 `structure`(JSON-LD) 与 `content`(可引用性) 两项的 `checks` / `recommendation`。
2. 拿确定性结构信号（**非评分** advisory，省人肉数）：
   ```bash
   chinese-geo structure <域名或URL> --format json
   ```
   未安装时 `python -m seogeo.cli structure <URL>`。它把下面清单里能机器判定的部分量出来——段落字数分布（答案胶囊）、FAQ 信号（FAQPage / 问句式小标题）、表格 / 列表存在、H1/H2 计数；据此对照清单判断，省得人肉数。注：答案胶囊字数是经验范围、非硬标准，仅供参考、不计分。
3. 需要结构化脚手架时：
   ```bash
   chinese-geo schema gen <organization|article|faqpage|breadcrumb>
   ```
4. 按下面清单逐项重排，再重跑 audit 看对应项转绿。

## 结构检查清单（判断层）

- **答案胶囊**：每个小节开头用一两句话（约几十字）直接把结论说完，再展开论证——便于 AI 整段抽取。（"答案胶囊"是业界经验做法，最佳字数各家说法不一、无定论，别拘泥具体数字。）
- **问答式小标题**：H2/H3 用用户真实会问的问句（"X 怎么选？""X 和 Y 有何区别？"），AI 联网检索按问题匹配。
- **表格化对比**：参数 / 价格 / 方案对比一律上表格——被引率最高的形态之一。
- **listicle**：可枚举的内容用有序列表（"5 种方法…"）——在 AI 最常引用的头部 URL 里 listicle 占比偏高（Evertune 2026 观察），是高被引形态之一。
- **FAQ 块 + FAQPage schema**：页尾放 3–6 组 FAQ，并用 `schema gen faqpage` 让结构化与正文一一对应。
- **schema 与正文对齐**：JSON-LD 里写的（作者 / 日期 / FAQ）正文必须也有，否则被判不一致而失效。
- **唯一 H1 + 不跳级**：一页一个 H1，H2/H3 层级连续。

## 诚实边界

- 结构优化提升的是"可抽取性 / 就绪度"，不直接等于引用率；要配内容质量（seogeo-content）与站外权重（seogeo-offsite）。
- 反爬站可能返回简化页，audit 的结构判定可能偏低（看 `rendering` 的"可见文本很少"提示）。

## Next Best Skill

结构搭好 → `seogeo-content` 把文案改成可引用形态；想站外被引 → `seogeo-offsite`；验证效果 → `seogeo-monitor`。
