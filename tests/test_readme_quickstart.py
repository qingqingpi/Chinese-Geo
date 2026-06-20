"""README「快速开始」必须做到 clone → 一条命令 → 看到结果，把 demo 放首屏（C2）。

诚实化：快速开始里若写 demo 的前后分数，必须 = run_demo() 实测（防手写假数字，
和 test_readme_sample.py 钉真实样例同一思路）。
"""
import os
import re

from seogeo.demo import run_demo

_ROOT = os.path.join(os.path.dirname(__file__), os.pardir)


def _readme() -> str:
    with open(os.path.join(_ROOT, "README.md"), encoding="utf-8") as f:
        return f.read()


def _quickstart() -> str:
    """截取「## 🚀 快速开始」到下一个标题（含 ###）之间的正文。"""
    m = re.search(r"## 🚀 快速开始(.*?)(?:\n##|\Z)", _readme(), re.S)
    assert m, "README 应有「## 🚀 快速开始」一节"
    return m.group(1)


def test_quickstart_has_clone_and_install():
    qs = _quickstart()
    assert "git clone" in qs
    assert "pip install -e ." in qs


def test_quickstart_leads_with_demo():
    """demo 是首屏 hero：在快速开始里 demo 出现在 audit 之前（一条命令看到结果）。"""
    qs = _quickstart()
    assert "chinese-geo demo" in qs, "快速开始应含 chinese-geo demo"
    assert qs.index("chinese-geo demo") < qs.index("chinese-geo audit"), \
        "demo 应排在 audit 前（先一条命令看到结果，再体检自己的站）"


def test_quickstart_demo_numbers_are_real():
    """快速开始写的 demo 前后分必须 = run_demo() 实测（手写假数字会变红）。"""
    qs = _quickstart()
    d = run_demo()
    before, after = d["before"].score, d["after"].score
    assert f"{before}/100" in qs, f"快速开始应写 demo 前分 {before}/100（实测，非手写）"
    assert f"{after}/100" in qs, f"快速开始应写 demo 后分 {after}/100（实测，非手写）"


def test_quickstart_links_examples_dir():
    assert "examples" in _quickstart(), "快速开始应指向 examples/ 目录（C1 的开发者级样例）"
