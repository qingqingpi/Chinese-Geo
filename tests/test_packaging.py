"""L4 打包产物校验：Claude 插件清单 / 市场 / MCP 声明必须是合法 JSON 且字段齐全。

这些是"一键安装"的地基，手滑写坏 JSON 就装不上——用测试钉住。
"""
import json
import os

_ROOT = os.path.join(os.path.dirname(__file__), "..")


def _load(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def test_plugin_manifest_valid():
    m = _load(".claude-plugin/plugin.json")
    assert m["name"] == "seogeo"
    assert m["description"]


def test_marketplace_lists_seogeo():
    m = _load(".claude-plugin/marketplace.json")
    assert "seogeo" in [p["name"] for p in m["plugins"]]
    assert m["plugins"][0]["source"]  # 有来源


def test_mcp_json_declares_server():
    m = _load(".mcp.json")
    assert "seogeo" in m["mcpServers"]
    assert m["mcpServers"]["seogeo"]["command"]
