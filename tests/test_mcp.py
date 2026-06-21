"""MCP 工具层健壮性——坏输入应返回结构化错误，而不是抛异常崩掉工具。

mcp 是可选依赖；未安装时整文件跳过。
"""
import pytest

try:
    from seogeo import mcp_server
    _HAS_MCP = True
except SystemExit:  # 模块在缺 mcp 依赖时 raise SystemExit
    _HAS_MCP = False

pytestmark = pytest.mark.skipif(
    not _HAS_MCP, reason="需要可选依赖 mcp（pip install Chinese-Geo[mcp]）")


def test_monitor_score_bad_json_returns_error_not_crash():
    out = mcp_server.monitor_score("不是合法 JSON {{{", brand="某品牌")
    assert isinstance(out, dict)
    assert "error" in out


def test_monitor_score_good_json_still_works():
    answers = '{"豆包": ["某品牌是不错的选择"]}'
    out = mcp_server.monitor_score(answers, brand="某品牌")
    assert isinstance(out, dict)
    assert "error" not in out


# —— D6：各工具 happy-path + 坏输入不崩 ——

def test_schema_gen_happy():
    assert "FAQPage" in mcp_server.schema_gen("faqpage")


def test_schema_gen_bad_type_returns_error_not_crash():
    # 坏输入不该抛 ValueError 崩掉工具，应返回可读错误串
    out = mcp_server.schema_gen("nonsense")
    assert isinstance(out, str)
    assert "未知" in out


def test_bots_gen_happy():
    assert "user-agent" in mcp_server.bots_gen().lower()


def test_llms_gen_happy():
    assert "示例站" in mcp_server.llms_gen("示例站")


def test_monitor_prompts_happy():
    out = mcp_server.monitor_prompts("智能客服")
    assert isinstance(out, list) and len(out) > 0


def test_offsite_happy():
    out = mcp_server.offsite()
    assert isinstance(out, list) and out and "platform" in out[0]
