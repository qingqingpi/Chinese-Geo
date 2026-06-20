# LOOP.md — Chinese-Geo 自动推进循环

> 给 AI 编程 Agent（Claude Code 等）用：一轮一轮把下面的 BACKLOG 做完。
> 配套读 `AGENTS.md`（项目是什么、CLI/Skill 清单、开发约定）。本文件只管"重心、怎么循环、做什么、不许做什么"。
> **命令名＝`chinese-geo`**（2026-06-20 改名，内部 Python 模块仍 `seogeo`，`python -m seogeo.cli ...` 不变）。

> ⏸️ **暂停待 review（必修 A/B/C 全完，2026-06-21）** —— Track A + B + C 已全部 `[x]`，必修闭环完成、333 测试全绿、本地提交未 push。**loop 在此停**：交回用户 review，不发版（发版＝人按一键按钮）。**别自动进 Track D**（选做 / 低优）。若有遗留计时器误触发本 loop：A/B/C 已无 `[ ]` → 直接停、输出 Track C 小结、等用户明确放行（如"续 Track D"）再动。

---

## 这个 loop 的重心（已与用户确认，2026-06-20）★
这是一个**给 AI 编程 Agent 用的插件**，它的命门不是"再加几条体检规则"，而是三件事：

1. **各家 agent 到底怎么用** —— Claude Code / Codex / 国内 CodeBuddy / Qoder / Kimi / opencode，每家的装法、调法、真实输出。
2. **用了有什么结果** —— 能拿出可证明的前后对比，而不是手写的假样例。
3. **够不够产品** —— clone 下来一条命令就能看到结果，开发者级的 examples / demo / quickstart。

**现实分工（必须遵守）**：一个跑在单会话里的 loop **能**做的——扩接入器、跑 `chinese-geo` 自己抓**真实**输出、建可复现 demo、搭案例研究模板与人工验证清单、产品化；**不能**做的——它没法自己去装并驱动 Codex/CodeBuddy/Kimi，也没法拿真 API key 打真引擎、改真站等结果。**凡是需要真 agent / 真 key / 真站的，loop 只搭"就绪的模板 + 给人执行的清单"，绝不编造结果。**

---

## 现状（已核实，2026-06-20）
- main 已合并改名 PR（命令 + 插件 `seogeo → chinese-geo`，内部模块 `seogeo` 不变），version `0.3.0`，**0.3.0 Release 待人发**。
- 本会话 loop 成果（audit 修复 + A1/A1b agent 接入 + A2 用法卡）已 **reconcile 到改名后基线**、统一 `chinese-geo` 命名。
- 测试基线 **256 passed / 2 skipped / 0 failed**，`git` 干净（本地领先 origin，未 push）。
- 备份分支 `loop-backup-prerename` 保留改名前的本地状态（可丢）。

---

## 每轮协议（THE LOOP，单次迭代）
一轮**只做 BACKLOG 最上面一个未完成项**，做完即提交，再进下一轮。

1. **读状态**：`cat AGENTS.md`；看本文件 BACKLOG 顶部第一个 `[ ]`；跑 `PYTHONPATH=. python3 -m pytest -q` 确认起点全绿。
2. **选一项**：取 BACKLOG 最上面一个 `[ ]`。
3. **TDD**：先在 `tests/` 写失败测试 → 跑红 → 写实现 → 跑绿。新增体检规则＝`seogeo/rules/` 加 `@register` 文件并 import 进 `rules/__init__.py`。
4. **自检**：全量 `pytest -q` 全绿；`PYTHONPATH=. python3 -m seogeo.cli audit https://example.com` 冒烟不崩；护栏测试（`tests/test_skills.py` vendor-neutral & 术语中性、`tests/test_packaging.py`）过。
5. **记账**：本文件 BACKLOG 勾 `[x]` + 一句完成说明；功能有变同步 `AGENTS.md`/`README.md`/`INSTALL.md`。
6. **提交**：`git add -A && git commit -m "<type>: <一句话>"`。**只本地 commit，不 push、不发版。**
7. **分轨复审闸**：勾完 `[x]` 后看 BACKLOG——
   - 若本项所在 Track（A / B / C / D）下**已无 `[ ]`**（本轮收尾了一整个 Track）→ **停，不调度下一轮**；输出本 Track 小结 + "请 review，确认 OK 再发 `/loop` 续下一 Track"，交回给人。
   - 否则回第 1 步继续下一项。
   - BACKLOG 全部 `[x]` → 停，输出总结 + "需要人来做"清单。
   > ⚠️ 本闸**优先于唤醒 prompt 里的简述**：到 Track 边界就停、交回给人，别一口气冲到 D。

---

## 铁律 / 护栏（违反即停）
- **不许编造结果（诚实硬停）**：所有"样例输出 / 报告 / 对比数字"必须是真跑 `chinese-geo` 抓来的真实输出。**三分法**：① 真跑工具拿真实输出 = 允许；② 纯空壳模板 = 允许，但**只能含 `⏳ 待人工填` 占位、零编造正文**（报告正文 / 数字 / transcript / 截图 / 引用率 / 对话 一律不许虚构）；③ **某项需要真实数据而当下拿不到**（网络不通 / 需真 key / 真 agent / 真站）→ **判 BLOCKED、写进 `NEXT.md`，绝不用"看着像真的样例"凑数**。宁可停，不可造假。
- **纯标准库、运行时零依赖**：重能力（渲染/MCP/网络引擎）走 optional extras，import 失败优雅降级。
- **术语中性**：产品目录内不出现"中国/西方"，统一"国内/海外"。
- **SKILL.md 保持 vendor-neutral**：不出现任何某 agent 专属语法。
- **绝不 push、绝不发 PyPI、绝不碰账号**：发版是人按一键按钮。
- **每轮必须留绿**：pytest 红了停下修；不准删测试 / 弱化断言凑绿。
- **诚实化**：不写无依据强断言（见 commit `0cd528b` 口径）；占比类数字标"单行业样本，仅供参考"。
- **卡住就停**：需要账号/真 agent/真 key/拿不准的决策 → 停，在仓库根写/更新 `NEXT.md` 讲清卡点与备选，交回给人。

---

## BACKLOG（按 A→B→C→D 顺序，一轮一项，做完 `[ ]`→`[x]`）

### Track A —— 跨 agent 真·可用（核心命门，最高优先）

**A0. 各 agent 接入 spec** 见 git 历史 / `seogeo/generate.py` 的 `_AGENTS`（11 agent + 4 类 MCP 策略：standard / opencode(`mcp`/`type`) / kimi(全局手动) / guidance(UI-only 贴 JSON)）。

- [x] A1. **扩 `init --agent`：CodeBuddy / Kimi / opencode**。✅ codebuddy→`CODEBUDDY.md`+`.mcp.json`、opencode→`AGENTS.md`+`opencode.json`(键 `mcp`/`type`)、kimi→`AGENTS.md`+`MCP-SETUP-kimi.md`。
- [x] A1b. **扩 `init --agent`：Qoder / Trae / Lingma**。✅ qoder→`AGENTS.md`+`MCP-SETUP-qoder.md`(UI-only)、trae→`.trae/rules/project_rules.md`+`.trae/mcp.json`、lingma→`.lingma/rules/seogeo.md`+`MCP-SETUP-lingma.md`；新增 `guidance` 策略 + `mcp_path` 覆写。
- [x] A2. **每个 agent 一份"用法卡"** `docs/agents/<name>.md`。✅ 8 张卡（claude/codex/codebuddy/kimi/opencode/qoder/trae/lingma）+ 共享 `cli-output-samples.md`（真跑落盘）；`test_agent_docs.py` 落点同步防漂移；命令统一 chinese-geo。
- [x] A3. **每个 agent 一份人工验证清单** `docs/verify/VERIFY-<name>.md`：在真 agent 里实跑、勾选、贴 transcript/截图的模板（loop 备好，⏳ 人来执行）。 ✅ 完成：8 份 `VERIFY-<name>.md`（claude/codex/codebuddy/kimi/opencode/qoder/trae/lingma）——环境 / 落点(与 build_agent_bundle 一致) / CLI 直调 / 原生调法 勾选清单 + ⏳ 待人工填实跑结果；`test_verify_docs.py` 32 项防漂移；288 测试。
- [x] A4. **跨 agent 接入冒烟测试**：临时目录里验证 `init --agent <X>` 产出正确指令文件 + 正确 MCP 键名/路径、不覆盖已有（零网络）。 ✅ 完成：`test_init_agent_smoke.py`——经 CLI `main` 在临时目录实跑 11 agent 的 `init --agent`，验落点齐全 + opencode `mcp`/`type` 特判 + 标准 `chinese-geo`/`chinese-geo-mcp` 键 + Trae 落 `.trae/mcp.json` + guidance 写 `MCP-SETUP-*.md` + 不覆盖已有 + 未知 agent 报错；零网络；305 测试。

### Track B —— 可证明的结果（真实站点案例 harness）
- [x] B1. **`chinese-geo demo` 命令**：对内置 fixture 站跑通"体检→生成修复→（对 fixture）应用→复检"，打印**前后分数对比**；零 key、可复现，作为最小自证。 ✅ 完成：`seogeo/demo.py`——用 chinese-geo 自己的生成器（generate_schema/robots）把差站修成好站，run_audit 前后对比实测 **33→100（Δ+67）**、必修项 4→0；`chinese-geo demo` 打印分项前后表；零网络、可复现；`test_demo.py` 5 项（含确定性）+ cli 1 项；311 测试。
- [x] B2. **真实站点案例研究模板** `docs/case-study/TEMPLATE.md`：固定字段 + 采集 schema(JSON) + monitor prompt 矩阵步骤。**⏳ 真实数据人来填**。 ✅ 完成：基本信息 / 体检前后 7 维表 / 改了什么 / 引用率·SoV 前后 + monitor 步骤 / 合法 JSON 采集 schema / 结论，全字段 ⏳ 占位、零编造；`test_case_study.py` 4 项（含 JSON 可解析 + 术语中性）；315 测试。
- [x] B3. **提交一份真实样例 audit 报告** `examples/sample-report.md`：loop 跑 `chinese-geo audit <真实公开站>` 抓**真实**输出落盘。 ✅ 完成：实跑 `chinese-geo audit https://example.com` 落盘真实报告（63/100、7 维分项 + 🔴必修清单，非手写）；带重现说明；`test_sample_report.py` 3 项钉真实结构 + 术语中性；318 测试。
- [x] B4. **README 示例输出换成真实的**：用 B3 的真实输出替换 README 里手写的假样例（诚实化）。 ✅ 完成：README「示例输出」换成 example.com 真实报告摘录（63/100、真实分项 + 必修项）+ 链到完整 `examples/sample-report.md`；删掉旧手写假样例（20/100）；`test_readme_sample.py` 钉"示例总分 = 真实报告总分"防再造假；320 测试。

### Track C —— 产品化（开发者级）
- [x] C1. **`examples/` 目录**：fixture 站（一个"差站"+ 期望改进点）、一条 quickstart 脚本、真实样例报告（B3）。 ✅ 完成：`examples/bad-site.html`（故意做差的反面教材，`run_audit` 实测 **52/100**、报 content/structure/discovery 必修项）+ `examples/quickstart.sh`（跑刚 clone 的源码 `demo`，零网络实测 33→100）+ `examples/README.md`（期望改进点表 + 指 `sample-report.md`）；`test_examples.py` 6 项钉"源码层缺要件 + 真实低分"防漂移（差站偷偷改好会变红）；326 测试。
- [x] C2. **quickstart 打磨**：README"快速开始"做到 clone→一条命令→看到结果；把 `chinese-geo demo` 放到首屏。 ✅ 完成：「快速开始」重构成两段——首屏 hero 把 `chinese-geo demo` 单独成块（clone→装→一条命令），配真实 **33/100 → 100/100** 说明（数字取自 `run_demo()`、`test_readme_quickstart.py` 钉死防手写假数字）+ 没装也能跑提示；其余命令降到「接着体检你自己的站」第二块；尾部加指向 `examples/` 目录链接。`test_readme_quickstart.py` 4 项（clone+install / demo 在 audit 前 / demo 数字=实测 / examples 链接）；330 测试。
- [x] C3. **文档同步过一遍**：INSTALL/AGENTS/README 与 A/B 的新能力对齐。 ✅ 完成：核对发现三份文档的 init --agent 11-agent 清单已与 `generate.py _AGENTS` 一致、无过时裸 `seogeo <子命令>`（命令名统一 chinese-geo）；唯一真缺口＝INSTALL.md 没提 `chinese-geo demo`（B1 自证）和 `examples/`（C1），已在「第 1 步」补上（装完先跑 demo 自证 + 指向 examples/，不硬编码分数避免无测试的漂移点）。新增 `test_docs_sync.py` 3 项 anti-drift（清单=代码、无过时命令名、INSTALL 覆盖 demo+examples），漏一个就变红。333 测试。

### Track D —— 收尾增强（选做 / 低优；必修＝A/B/C，C 清完即"必修完成"，D 视情况做或留人，别耗）
- [ ] D1. audit 加规则：图片 alt 缺失检查（`rules/img_alt.py` + 测试）。
- [ ] D2. audit 加规则：答案胶囊字数软提示（只 warn、注明"经验范围非硬标准"）。
- [ ] D3. structure 确定性背书：把"答案胶囊字数/FAQ/表格存在"下沉成 CLI 能力，structure SKILL 回调。
- [ ] D4. playwright 真渲染接线：`[render]` extra 接进 rendering 规则、填 `rendered_html`，无则降级；可注入零网络测试。
- [ ] D5. BYOK 引擎补 Gemini 原生 + 文心 Qianfan client（各零网络测试）；元宝无公开 API → 文档标注跳过。
- [ ] D6. CLI/MCP 胶水单测继续加厚（每子命令/每工具 happy-path + 坏输入不崩）。

---

## 需要人来做（不在 loop 范围，loop 只备好模板/清单）
- **发版策略（2026-06-20 更新：loop 最后不发版，等人审查）**：① `0.3.0`（改名）随时单发、修好 `/plugin install`（急、独立，你的 button）；② **loop 不触发任何发版**——必修（A/B/C）做完就**停下、把本地提交 + 测试状态交给你审查**，**不催发版、不发"可发版"信号、不 push、不 bump**。发不发版、发哪个版，你审查完全权决定（与本 loop 解耦）。
- 在真实 **Codex / CodeBuddy / Qoder / Kimi / opencode** 里实跑一遍，按 `docs/verify/VERIFY-<name>.md` 勾选、贴 transcript/截图。
- 真实站点案例：把生成的修复**应用到你自己的站** → 等收录 → 用**真 API key** 跑 `monitor` 拿引用率/SoV 前后对比 → 填进 `docs/case-study/`。
- 把本地 loop 提交 push / 开 PR 合进 main（reconcile 已完成、命名已是 chinese-geo）。

---

## 完成的定义
A/B/C 三轨全 `[x]`、`pytest` 全绿、`pip install -e .` 可用、`chinese-geo demo` 跑通看到前后对比、每家 agent 有"用法卡 + 真实输出 + 验证清单"、README 用真实样例。
真 agent 实跑、真站案例、发版——见"需要人来做"，留给你。
