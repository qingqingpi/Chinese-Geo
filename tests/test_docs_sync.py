"""文档同步（C3）：INSTALL / AGENTS / README 与 A/B/C 新能力对齐，且跨文档 + 与代码一致（anti-drift）。

- init --agent 清单：三份文档都必须含 generate.py `_AGENTS` 的全部 agent（漏一个就变红 → 防文档落后于代码）。
- 命令名统一 chinese-geo：产品文档不出现过时的裸 `seogeo <子命令>`。
- INSTALL 覆盖 demo + examples/：B1 的零网络自证 + C1 的开发者级样例目录要进安装文档。
"""
import os
import re

from seogeo.generate import _AGENTS

_ROOT = os.path.join(os.path.dirname(__file__), os.pardir)
_DOCS = ("README.md", "AGENTS.md", "INSTALL.md")


def _read(name: str) -> str:
    with open(os.path.join(_ROOT, name), encoding="utf-8") as f:
        return f.read()


def test_init_agent_list_matches_code_in_all_docs():
    """README/AGENTS/INSTALL 的 init --agent 清单都必须含 _AGENTS 全部 agent（与代码一致）。"""
    keys = set(_AGENTS)
    for doc in _DOCS:
        m = re.search(r"init --agent <([^>]+)>", _read(doc))
        assert m, f"{doc} 应有 init --agent <...> 清单"
        listed = set(re.split(r"\|", m.group(1)))
        missing = keys - listed
        assert not missing, f"{doc} 的 init --agent 清单漏了 {missing}（与 generate.py _AGENTS 不一致）"


def test_product_docs_have_no_stale_cli_command():
    """命令名是 chinese-geo：产品文档不该出现裸 `seogeo <子命令>`（seogeo.cli 模块、seogeo-* skill 名不算）。"""
    for doc in _DOCS:
        stale = re.findall(r"\bseogeo (audit|bots|schema|llms|init|monitor|offsite|demo)\b", _read(doc))
        assert not stale, f"{doc} 含过时命令 seogeo {stale}（应为 chinese-geo）"


def test_install_covers_demo_and_examples():
    """INSTALL 应教 demo 自证 + 指向 examples/（与 B1/C1/C2 对齐）。"""
    body = _read("INSTALL.md")
    assert "chinese-geo demo" in body, "INSTALL 应教 chinese-geo demo（零网络自证）"
    assert "examples/" in body, "INSTALL 应指向 examples/ 目录"
