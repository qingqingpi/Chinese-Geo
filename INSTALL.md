# 安装 china-geo（命令 `seogeo`）

分两层：**L0 CLI（所有 agent 都要）** + **各 agent 的原生集成（可选，体验更顺）**。设计原则是"越底层越通用"——CLI 100% 覆盖，上层按 agent 支持度优雅降级。

## 第 1 步：装 CLI（必装，运行时零依赖）

当前从源码安装（发行名 `china-geo`，命令名 `seogeo`；PyPI 发布后即可直接 `pip install china-geo`）：

```bash
git clone https://github.com/qingqingpi/china-geo
cd china-geo
pip install -e .            # 得到 `seogeo` 命令（纯标准库）
pip install -e ".[mcp]"     # 想用 MCP 再加（得到 `seogeo-mcp`）
```

装完，任何 agent 都能直接 shell 调：`seogeo audit example.com`。

## 第 2 步：各 agent 原生集成（可选）

### Claude Code —— 一键插件（skills + MCP）

```
/plugin marketplace add qingqingpi/china-geo
/plugin install seogeo
```

装上后 5 个技能自动可用：`/seogeo:seogeo-audit`、`seogeo-structure`、`seogeo-content`、`seogeo-offsite`、`seogeo-monitor`；根目录 `.mcp.json` 里的 `seogeo` MCP 服务也会注册（需先 `pip install "china-geo[mcp]"`，让 `seogeo-mcp` 在 PATH 上）。

### Codex / opencode / CodeBuddy / Qoder / Kimi / Cursor / Trae 等

仓库根的 **`AGENTS.md`** 是事实标准指令文件，这些 agent 会自动读到，知道何时调 `seogeo` 与各 skill。再按支持度叠加：

- **支持 MCP 的**：把根目录 `.mcp.json` 里的 `seogeo` 服务加进该 agent 的 MCP 配置。Codex 走 `~/.codex/config.toml`：

  ```toml
  [mcp_servers.seogeo]
  command = "seogeo-mcp"
  ```
- **支持 Agent Skills 的**（Codex / CodeBuddy / Kimi 等）：`skills/*/SKILL.md` 是 vendor-neutral 纯 Markdown，放进该 agent 的 skills 目录即可。
- **都不支持的**（如 Cursor）：直接 `seogeo <命令>` 命令行也能拿到约 80% 价值。

> **懒人快捷**：在你的项目根跑 `seogeo init --agent <claude|codex|gemini|cursor|generic>`，自动写好该 agent 的指令文件（`CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `.cursor/rules/seogeo.mdc`）+ `.mcp.json`；已存在的文件不会被覆盖。

## 分层一览

| 层 | 产物 | 覆盖 |
|---|---|---|
| L0 确定性引擎 | `seogeo` CLI（pip 装，零依赖） | 100%，所有 agent shell 可调 |
| L1 指令 | `AGENTS.md`（`CLAUDE.md` 软链到它） | 30+ agent 事实标准 |
| L2 工具 | `.mcp.json` → `seogeo-mcp`（7 工具） | 几乎全 agent |
| L3 判断逻辑 | `skills/*/SKILL.md`（5 个，vendor-neutral） | 准通用 |
| L4 各家专属糖 | `.claude-plugin/`（Claude 插件 + marketplace） | 各家不通用，逐 agent 薄加 |
