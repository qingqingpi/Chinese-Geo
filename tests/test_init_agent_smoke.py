"""跨 agent 接入冒烟测试：临时目录里实跑 `chinese-geo init --agent <X>`（经 CLI main，零网络），
验证产出文件正确、MCP 键名/路径正确、不覆盖已有。

注：这是对**已有** init --agent（A1/A1b 实现）的端到端冒烟/回归测试——验证既有行为，故首跑即绿。
"""
import json

import pytest

from seogeo.cli import main
from seogeo.generate import build_agent_bundle

_ALL_AGENTS = ["claude", "codex", "gemini", "cursor", "generic",
               "codebuddy", "kimi", "opencode", "qoder", "trae", "lingma"]


@pytest.mark.parametrize("agent", _ALL_AGENTS)
def test_init_agent_writes_every_landing_file(agent, tmp_path):
    code = main(["init", "--agent", agent, "--output", str(tmp_path)])
    assert code == 0
    for fname in build_agent_bundle(agent):
        assert (tmp_path / fname).exists(), f"{agent}: 应写出 {fname}"


def test_standard_mcp_json_key_and_command(tmp_path):
    # 标准 agent 的 .mcp.json：键 mcpServers / 服务名 chinese-geo / 命令 chinese-geo-mcp
    main(["init", "--agent", "claude", "--output", str(tmp_path)])
    cfg = json.loads((tmp_path / ".mcp.json").read_text(encoding="utf-8"))
    assert cfg["mcpServers"]["chinese-geo"]["command"] == "chinese-geo-mcp"


def test_opencode_special_mcp_key_and_type(tmp_path):
    # opencode 特判：opencode.json 用键 mcp（非 mcpServers）、server 带 type=local
    main(["init", "--agent", "opencode", "--output", str(tmp_path)])
    cfg = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
    assert "mcp" in cfg and "mcpServers" not in cfg
    assert cfg["mcp"]["chinese-geo"]["type"] == "local"
    assert cfg["mcp"]["chinese-geo"]["command"] == ["chinese-geo-mcp"]


def test_trae_mcp_lands_in_trae_dir_not_root(tmp_path):
    main(["init", "--agent", "trae", "--output", str(tmp_path)])
    assert (tmp_path / ".trae" / "mcp.json").exists()
    assert not (tmp_path / ".mcp.json").exists()


def test_guidance_agents_write_setup_md_not_mcp_json(tmp_path):
    # UI-only / 全局 MCP 的 agent（qoder/lingma/kimi）写手动指引、不写 .mcp.json
    for agent in ("qoder", "lingma", "kimi"):
        d = tmp_path / agent
        main(["init", "--agent", agent, "--output", str(d)])
        assert list(d.glob("MCP-SETUP-*.md")), f"{agent}: 应写 MCP-SETUP-*.md"
        assert not (d / ".mcp.json").exists(), f"{agent}: 不该写 .mcp.json"


def test_does_not_overwrite_existing_file(tmp_path):
    # 不覆盖已有：预置 CLAUDE.md，init 后内容不变
    (tmp_path / "CLAUDE.md").write_text("ORIGINAL", encoding="utf-8")
    code = main(["init", "--agent", "claude", "--output", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == "ORIGINAL"


def test_unknown_agent_returns_error_code(tmp_path):
    assert main(["init", "--agent", "nonsense", "--output", str(tmp_path)]) == 2
