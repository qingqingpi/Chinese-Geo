---
name: seogeo-structure
description: 当用户想优化页面"结构/骨架"让 AI 更易抽取引用时使用——"内容 AI 抓了但不引用"、"怎么排版 AI 才爱用"、"答案胶囊/FAQ/表格怎么做"、"标题层级/分块"、"schema 和正文对不上"。先跑 seogeo audit/schema 看结构项，再给重排建议。不用于：纯文案改写（用 seogeo-content）、站外分发（用 seogeo-offsite）。
---

# seogeo · 结构优化（让 AI 抽得动、愿意引）

AI 引用的是"块"，不是整页。把页面拆成自包含、可直接抽取的单元，被引概率显著上升——带表格页被引率约为纯文字的 4.2×，listicle 占 top 引用约一半。

## 流程

1. 先体检结构项（确定性、零 key）：
   ```bash
   seogeo audit <域名> --format json
   ```
   未安装命令时用 `python -m seogeo.cli audit <域名> --format json`。重点看 `structure`(JSON-LD) 与 `content`(可引用性) 两项的 `checks` / `recommendation`。
2. 需要结构化脚手架时：
   ```bash
   seogeo schema gen <organization|article|faqpage|breadcrumb>
   ```
3. 按下面清单逐项重排，再重跑 audit 看对应项转绿。

## 结构检查清单（判断层）

- **答案胶囊**：每个小节开头 40–75 字直接把结论说完（AI 抽取的基本单位），再展开论证。
- **问答式小标题**：H2/H3 用用户真实会问的问句（"X 怎么选？""X 和 Y 有何区别？"），AI 联网检索按问题匹配。
- **表格化对比**：参数 / 价格 / 方案对比一律上表格——被引率最高的形态之一。
- **listicle**：可枚举的内容用有序列表（"5 种方法…"），占 top 引用约 50%。
- **FAQ 块 + FAQPage schema**：页尾放 3–6 组 FAQ，并用 `schema gen faqpage` 让结构化与正文一一对应。
- **schema 与正文对齐**：JSON-LD 里写的（作者 / 日期 / FAQ）正文必须也有，否则被判不一致而失效。
- **唯一 H1 + 不跳级**：一页一个 H1，H2/H3 层级连续。

## 诚实边界

- 结构优化提升的是"可抽取性 / 就绪度"，不直接等于引用率；要配内容质量（seogeo-content）与站外权重（seogeo-offsite）。
- 反爬站可能返回简化页，audit 的结构判定可能偏低（看 `rendering` 的"可见文本很少"提示）。

## Next Best Skill

结构搭好 → `seogeo-content` 把文案改成可引用形态；想站外被引 → `seogeo-offsite`；验证效果 → `seogeo-monitor`。
