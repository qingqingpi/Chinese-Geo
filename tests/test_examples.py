"""examples/ 目录（C1，开发者级"clone→一条命令→看到结果"）：
差站 fixture + quickstart 脚本 + 真实样例报告（B3）。

诚实化关键：差站不是手写"看着差"，而是由 chinese-geo 自己的 run_audit **实测**打低分、报必修项——
防有人把 fixture 悄悄改好却还当差站用（与"好站满分"对照，钉住真实行为）。
"""
import os

from seogeo.pipeline import run_audit
from seogeo.rules.base import AuditContext

_EX = os.path.join(os.path.dirname(__file__), os.pardir, "examples")


def _read(name: str) -> str:
    with open(os.path.join(_EX, name), encoding="utf-8") as f:
        return f.read()


def test_examples_has_fixture_site():
    assert os.path.exists(os.path.join(_EX, "bad-site.html")), "缺 examples/bad-site.html 差站 fixture"


def test_examples_has_quickstart_script():
    qs = os.path.join(_EX, "quickstart.sh")
    assert os.path.exists(qs), "缺 examples/quickstart.sh"
    body = _read("quickstart.sh")
    assert body.startswith("#!"), "quickstart.sh 应带 shebang（可执行脚本）"
    assert "demo" in body, "quickstart 应跑 demo（零 key、零网络的自证入口）"


def test_examples_has_readme_documenting_improvements():
    body = _read("README.md")
    assert "期望改进" in body or "改进点" in body, "README 应写明差站的期望改进点"
    assert "bad-site.html" in body
    assert "quickstart" in body
    assert "sample-report.md" in body  # 指向真实样例报告（B3）


def test_fixture_site_is_genuinely_bad_at_source():
    """源码层就缺 GEO 要件——防被人"修好"却仍当差站。"""
    html = _read("bad-site.html")
    assert "lang=" not in html               # 无 <html lang>
    assert "<h1" not in html                 # 无 H1
    assert "application/ld+json" not in html  # 无 JSON-LD
    assert "og:title" not in html            # 无 Open Graph


def test_fixture_site_scores_low_on_real_audit():
    """用 chinese-geo 自己的引擎实测：差站得分低、且有必修项。"""
    html = _read("bad-site.html")
    result = run_audit(AuditContext(url="https://demo.example", html=html, robots_txt=None))
    assert result.score < 70, f"差站不该高分，实测 {result.score}/100"
    crit = [r for r in result.recommendations if r["priority"] == "Critical"]
    assert crit, "差站应至少报一个必修项（Critical）"
    # HTML 派生的两类（结构化 / 内容可引用性）应明显未满分
    assert result.breakdown["structure"]["earned"] < result.breakdown["structure"]["max"]
    assert result.breakdown["content"]["earned"] < result.breakdown["content"]["max"]


def test_examples_terminology_neutral():
    for name in ("bad-site.html", "README.md", "quickstart.sh"):
        body = _read(name)
        assert chr(0x4e2d) + chr(0x56fd) not in body  # 不含"中国"
        assert chr(0x897f) + chr(0x65b9) not in body  # 不含"西方"
