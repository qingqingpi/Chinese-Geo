---
name: seogeo-optimize
description: 当用户想"从头到尾完整做一遍"网站的 AI 可见性 / GEO / SEO 优化时使用——"全面提升 AI 可见性"、"把站从头到尾做一遍 GEO"、"完整 GEO 流程怎么走"、"AI 搜索优化全套"、"不知从哪下手带我走一遍"。这是总入口：按阶段编排，逐段委派给 audit / structure / content / offsite / monitor 专项 skill 与 seogeo CLI。不用于：只做单一环节（直接用对应专项 skill）。
---

# seogeo · GEO 全流程总编排（一条龙）

把零散手法编成一条可执行的闭环。**核心原则：先做能证明的确定性赢面（爬虫准入、结构），文案层保持谦虚（纯文案手法随竞争趋于零和），最后用监控量化证明有没有效果。**

## 总览：六阶段闭环

`1 体检 → 2 地基(确定性) → 3 结构 → 4 内容 → 5 站外+实体 → 6 监控验证 →` 回到 1 按月迭代。

越靠前越确定、越该先做；越靠后越需持续投入。**别跳过 1–2 直接堆文案。**

## 阶段拆解

### 阶段 1 · 体检定位（确定性）
跑 `seogeo audit <域名> --format json`，拿到 `score` / `band` / `recommendations`。委派 **`seogeo-audit`** 出中文行动清单。**先看有没有 Critical（尤其国内爬虫被挡）——有就先修，别的先放。**

### 阶段 2 · 地基修复（确定性赢面，最高优先）
seogeo 押注的"能证明的赢面"：
- 爬虫准入：`seogeo bots gen` 生成 robots（国内各家单独成块）；Bytespider 另在服务端 / WAF 硬拦；`seogeo bots verify <ip> <bot>` 校验真伪。
- 结构化：`seogeo schema gen <type>` 补 JSON-LD。
- 一键打包：`seogeo init` 直接出 robots + llms + schema + canonical 清单。

退出标准：重跑 audit，`domestic` / `structure` 项转绿。

### 阶段 3 · 结构（委派 `seogeo-structure`）
答案胶囊 40–75 字、问答式小标题、表格 / listicle、FAQ + schema 对齐。退出标准：`content` / `structure` 维度回升。

### 阶段 4 · 内容（委派 `seogeo-content`）
结论前置、加统计 / 引文 / 出处、TL;DR、新鲜度。**诚实提醒用户：纯文案手法边际收益随竞争下降，别过度承诺；这步是锦上添花，不是地基。**

### 阶段 5 · 站外 + 实体（委派 `seogeo-offsite`）
按目标引擎选平台（豆包←抖音 / 头条、元宝←公众号、文心←百度百科 / 百家号、DeepSeek / Kimi←知乎 / CSDN）；一题多发；百科 / sameAs / NAP 立实体。**AI 回答约 91% 来自第三方站——这步往往比站内更关键。**

### 阶段 6 · 监控验证（委派 `seogeo-monitor`）
`seogeo monitor prompts` 生成去品牌化问题 →（零 key 手动粘 / BYOK `monitor run` 自动）→ `monitor score` 算引用率 + SoV。基准 <10% 差 / 10–30% 良 / >30% 优。**按月重测**，回推前几阶段该补哪。

## 诚实边界（务必传达）
- "有效果"押在确定性赢面（阶段 2）+ 可量化监控（阶段 6）；文案层（阶段 4）保持谦虚。
- 体检反映的是爬虫 UA 抓到的 HTML；反爬站可能被低估。
- AI 联网结果会波动、可被操控 → GEO 是持续运营，不是一次性项目。

## 用法
逐阶段走，每段调对应专项 skill / CLI；做完一轮回到阶段 1 按月迭代。用户只想要某一环 → 直接转对应专项 skill。
