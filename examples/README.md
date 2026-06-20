# examples/ —— 开发者级「clone → 一条命令 → 看到结果」

三样东西，零 key、可复现：

| 文件 | 是什么 |
|---|---|
| `bad-site.html` | 一个**故意做差**的 fixture 站（演示用反面教材） |
| `quickstart.sh` | 一条命令跑 `chinese-geo demo`，看差站被自动修好的前后分数对比 |
| `sample-report.md` | 真实样例 audit 报告（实跑 `chinese-geo audit https://example.com` 落盘，**非手写**） |

## 最快看到结果

```bash
bash examples/quickstart.sh
```

或直接：

```bash
chinese-geo demo                 # 内置差站：体检 → 修复 → 复检，前后分数对比（零网络）
chinese-geo audit example.com    # 体检你想看的站（联网）
```

## bad-site.html 差在哪（期望改进点）

这页是「GEO 体检会扣很多分」的反面教材。chinese-geo 的 audit 会**实测**报出下面这些
（`tests/test_examples.py` 钉住它真的低分、真有必修项——防有人把 fixture 悄悄改好却还当差站）：

| 期望改进点 | audit 维度 | 怎么改 |
|---|---|---|
| 无 `<html lang>` 语言声明 | 技术基线 | 加 `<html lang="zh-CN">` |
| 用 `<div>` 当标题、无 `<h1>` / `<h2>` | 内容可引用性 | 唯一 `<h1>` + `<h2>` 分节 |
| 正文稀薄（几十字） | 内容可引用性 | 正文 ≥ 300 字，结论前置 |
| 无列表 / 表格 | 内容可引用性 | 加 `<ul>` / `<table>`（利于被 AI 抽取引用） |
| 无 JSON-LD 结构化数据 | 结构化 | 加 Organization / Article schema（`chinese-geo schema gen`） |
| 无 Open Graph 标签 | 结构化 | 加 `og:title` / `og:description` / `og:image` |
| 无移动端 viewport | 技术基线 | 加 `<meta name="viewport" ...>` |
| 无日期信号 | 内容可引用性 | 加 `article:published_time` 等新鲜度信号 |

> `chinese-geo demo` 用工具**自己的生成器**把同类差站修成好站，实测分数从低分抬到满分——这就是最小自证。
> 想看真实公开站长什么样，见 `sample-report.md`（example.com 实跑，63/100）。
