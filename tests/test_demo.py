"""chinese-geo demo：内置 fixture 站 体检→修复→复检，前后分数对比（零 key、零网络、可复现）。"""
from seogeo.demo import render_demo, run_demo


def test_demo_score_improves_after_fix():
    d = run_demo()
    assert d["after"].score > d["before"].score   # 修复后分更高（最小自证的核心）
    assert d["before"].score < 100                 # "差站"确实有问题


def test_demo_is_deterministic():
    # 零网络、可复现：跑两次结果一致
    assert run_demo()["after"].score == run_demo()["after"].score
    assert run_demo()["before"].score == run_demo()["before"].score


def test_demo_fixes_structure_and_content_dimensions():
    d = run_demo()
    b, a = d["before"], d["after"]
    # 用 chinese-geo 自己的生成器补的：结构化（JSON-LD）+ 内容（H1/正文/列表）实测抬升
    assert a.breakdown["structure"]["earned"] > b.breakdown["structure"]["earned"]
    assert a.breakdown["content"]["earned"] > b.breakdown["content"]["earned"]


def test_demo_fixes_domestic_bot_access():
    d = run_demo()
    # "差站" robots 挡了 Bytespider（Critical），修复后放行
    assert d["after"].breakdown["domestic"]["earned"] > d["before"].breakdown["domestic"]["earned"]


def test_render_demo_shows_before_after():
    out = render_demo()
    assert "修复前" in out and "修复后" in out
    assert "chinese-geo demo" in out
