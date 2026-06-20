"""README「示例输出」必须是真实的——B3 落盘的真实报告的子集，不是手写假样例（诚实化）。"""
import os
import re

_ROOT = os.path.join(os.path.dirname(__file__), os.pardir)


def _read(p: str) -> str:
    with open(os.path.join(_ROOT, p), encoding="utf-8") as f:
        return f.read()


def test_readme_sample_matches_real_report():
    readme = _read("README.md")
    report = _read("examples/sample-report.md")
    block = re.search(r"### 示例输出.*?```\n(.*?)\n```", readme, re.S)
    assert block, "README 应有 ### 示例输出 代码块"
    sample = block.group(1)
    # 同一被审计的真实公开站
    assert "chinese-geo 体检报告：https://example.com" in sample
    assert "chinese-geo 体检报告：https://example.com" in report
    # README 示例里的总分必须与真实报告一致（手写假分数会让此处变红）
    m = re.search(r"总分 (\d+)/100", sample)
    assert m, "示例应含总分行"
    assert f"总分 {m.group(1)}/100" in report, "README 示例总分必须 = 真实报告总分（非手写）"


def test_readme_links_full_sample_report():
    assert "examples/sample-report.md" in _read("README.md")  # 指向完整真实报告
