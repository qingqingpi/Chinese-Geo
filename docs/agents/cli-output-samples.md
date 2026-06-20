# chinese-geo 真实 CLI 输出样例

> 本文件是各 agent 用法卡共享的"真实输出"参考——全部由 `chinese-geo` 命令实跑落盘（非手写），
> 针对公开站 `https://example.com`、示例引擎/行业。你在自己的域名上跑会得到对应的真实结果。
> （命令未安装时用 `python -m seogeo.cli ...`——内部 Python 模块名仍是 `seogeo`，仅命令改名为 `chinese-geo`。）

## `chinese-geo audit https://example.com`

```
# chinese-geo 体检报告：https://example.com

**总分 63/100 · 等级：待打基础**

## 分项得分
| 维度 | 得分 |
|---|---|
| ★国内 AI 爬虫准入 | 26/26 |
| 内容可引用性 | 4/24 |
| AI 可发现性 | 0/8 |
| 技术基线 | 20/20 |
| 结构化 | 3/22 |
| 海外 AI 爬虫准入 | 12/12 |
| JS 渲染可见性 | 14/14 |

## 优先级修复清单

### 🔴 必须修
- **[+16分 · 内容可引用性]** 补强：H2 小节切分、正文≥300字、列表/表格（利于被 AI 抽取引用）
  - 影响引擎：全引擎通用：可引用形态对国内外引擎都有效
- **[+16分 · 结构化]** 添加 Organization / Article / FAQPage 等 JSON-LD（schema.org）
  - 影响引擎：全引擎通用：结构化数据帮所有 AI 理解实体与问答
- **[+8分 · AI 可发现性]** 生成 sitemap.xml，并在百度搜索资源平台 / 搜狗站长提交（注：llms.txt 国内基本无效，仅对部分海外引擎有用）

### 🟠 重要
- **[+4分 · 内容可引用性]** 加可见更新日期 + JSON-LD datePublished/dateModified（或 article:published_time）
- **[+3分 · 结构化]** 加 og:title / og:description / og:image

> 验证闭环：改完重跑 `chinese-geo audit` 看对应项转绿；上线几周后用 `chinese-geo monitor` 抽样看引用率 / SoV 是否回升。
```

> 抓取失败不瞎打分：若首页 / robots 抓不到（网络 / DNS / 状态码 / 屏蔽抓取），相关维度会显示
> "无法获取首页 HTML，无法判定"并提示先确认可访问，而不是误报"0 字 / 缺 H1 / 缺 schema"。

## `chinese-geo offsite --engine 豆包 --audience consumer`

```
# 国内社媒 / 站外平台矩阵（筛选：喂 豆包、消费/生活）

## 推荐平台（平台 → 喂哪些引擎 ｜ 受众 ｜ 开放/封闭；次行=被哪个搜索索引 + 打法）
- 今日头条 / 头条号 → 喂 豆包 ｜ 消费/B2B ｜ 开放
    被索引：头条搜索（字节自家）；百度索引不到（字节-百度互屏）　字节系，喂豆包
- 抖音 → 喂 豆包 ｜ 消费 ｜ 封闭(平台内SEO)
    被索引：抖音搜索（封闭）；外部基本不可索引　抖音内 AI 只引抖音 → 做平台内 SEO
- 小红书 → 喂 豆包/通义 ｜ 消费 ｜ 封闭(平台内SEO)
- B站 → 喂 豆包/通义 ｜ 消费/B2B ｜ 开放

## 一题多发（同文改写、多平台同步）
头条号 / 百家号 / 知乎 / 搜狐号 / CSDN —— 一次产出、多源覆盖

> 每家 AI 主要吃自己生态——按目标引擎 / 受众选平台分发；占比是单行业样本，方向可信、数值仅参考。
```

## `chinese-geo monitor prompts --industry 智能客服`

```
# 去品牌化 prompt 矩阵（智能客服）—— 逐条粘进各 AI 引擎，把回答收集起来

1. [informational] 智能客服是什么？有哪些主流的解决方案？
2. [informational] 做智能客服一般用什么工具/平台？
5. [comparison] 智能客服哪个好？请对比几个主流选择的优缺点。
6. [comparison] 推荐几款智能客服，并说明区别。
```

> 收集到各引擎回答后，用 `chinese-geo monitor score --answers <file.json> --brand <你的品牌>` 算引用率 / SoV
> （基准：<10% 差 / 10–30% 良 / >30% 优）；有 API key 可 `chinese-geo monitor run` 自动跑各引擎。
