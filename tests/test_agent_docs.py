"""每个 agent 的"用法卡" docs/agents/<name>.md：

- 存在（A2 指定的 8 家都得有）；
- 接入落点与 build_agent_bundle 的真实产物一致（防文档漂移——卡片别说错装到哪）；
- 含一键接入命令 + 真实 audit 输出片段（非手写假样例）。
"""
import os

import pytest

from seogeo.generate import build_agent_bundle

_DOCS = os.path.join(os.path.dirname(__file__), os.pardir, "docs", "agents")
# A2：有独立接入故事的 8 家（顺序＝ Claude→Codex→CodeBuddy→Kimi→opencode→Qoder→Trae→Lingma）
_CARD_AGENTS = ["claude", "codex", "codebuddy", "kimi", "opencode", "qoder", "trae", "lingma"]


def _card(name: str) -> str:
    with open(os.path.join(_DOCS, name + ".md"), encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("agent", _CARD_AGENTS)
def test_usage_card_exists(agent):
    assert os.path.exists(os.path.join(_DOCS, agent + ".md")), f"缺 docs/agents/{agent}.md"


@pytest.mark.parametrize("agent", _CARD_AGENTS)
def test_card_lists_its_real_landing_files(agent):
    # 卡片必须提到 init --agent 真正写的每个落点（指令文件 + MCP 产物），与代码同步、防漂移
    card = _card(agent)
    for fname in build_agent_bundle(agent):
        assert fname in card, f"{agent} 卡片应提到接入落点 {fname}"


@pytest.mark.parametrize("agent", _CARD_AGENTS)
def test_card_shows_init_and_real_audit_output(agent):
    card = _card(agent)
    assert f"init --agent {agent}" in card             # 一键接入命令
    assert "chinese-geo audit" in card                  # 调法
    assert ("总分" in card) or ("体检报告" in card)     # 真实 audit 输出片段（非手写假样例）


@pytest.mark.parametrize("agent", _CARD_AGENTS)
def test_card_terminology_neutral(agent):
    # 产品目录术语中性：不出现地缘国名/方位词，统一"国内/海外"
    card = _card(agent)
    assert chr(0x4e2d) + chr(0x56fd) not in card  # 不含"中国"
    assert chr(0x897f) + chr(0x65b9) not in card  # 不含"西方"
