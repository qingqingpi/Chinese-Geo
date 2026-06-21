"""CLI dispatch 健壮性——手写参数解析的边角，坏输入不该悄悄做错事。"""
from seogeo.cli import main


def test_audit_rejects_flag_as_url(capsys):
    # `seogeo audit --format`：--format 不该被当成 URL 去体检（旧版会体检 "https://--format"），
    # 应识别出"缺少 URL"并提示用法。
    code = main(["audit", "--format"])
    assert code == 2
    assert "用法" in capsys.readouterr().out


def test_audit_empty_prints_usage(capsys):
    code = main(["audit"])
    assert code == 2
    assert "用法" in capsys.readouterr().out


def test_init_agent_guidance_message_points_to_manual_setup(tmp_path, capsys):
    # 引导型 agent（qoder 的 MCP 是 UI-only）：完成提示不该谎称写好了 .mcp.json，而要指向手动配置
    code = main(["init", "--agent", "qoder", "--output", str(tmp_path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "手动" in out                              # 提示手动配 MCP
    assert ".mcp.json 里的 chinese-geo" not in out    # 不谎称写好了 .mcp.json


def test_init_agent_standard_message_says_mcp_ready(tmp_path, capsys):
    # 标准 agent（claude 写真 .mcp.json）：提示 MCP 已配好
    code = main(["init", "--agent", "claude", "--output", str(tmp_path)])
    assert code == 0
    assert "已配好" in capsys.readouterr().out


def test_demo_prints_before_after_comparison(capsys):
    # `chinese-geo demo`：内置 fixture 站前后分数对比（零 key、零网络）
    code = main(["demo"])
    assert code == 0
    out = capsys.readouterr().out
    assert "修复前" in out and "修复后" in out


def test_structure_no_url_prints_usage(capsys):
    assert main(["structure"]) == 2
    assert "用法" in capsys.readouterr().out


def test_structure_happy_path(monkeypatch, capsys):
    # 零网络：注入 fetch_text → 走 analyze + render
    monkeypatch.setattr("seogeo.cli.fetch_text",
                        lambda url: ("<h1>标题</h1><p>" + "正" * 50 + "</p>", None))
    assert main(["structure", "example.com"]) == 0
    assert "结构信号" in capsys.readouterr().out


def test_structure_fetch_error_does_not_crash(capsys, monkeypatch):
    # 抓不到页面 → 友好报错 + 退出码 2，绝不拿空 HTML 当"无结构"误报
    monkeypatch.setattr("seogeo.cli.fetch_text", lambda url: (None, "timeout"))
    assert main(["structure", "https://x.com"]) == 2
    assert "无法获取" in capsys.readouterr().out


# —— D6：各零网络子命令 happy-path + 坏输入不崩 ——

def test_schema_gen_happy(capsys):
    assert main(["schema", "gen", "faqpage"]) == 0
    assert "FAQPage" in capsys.readouterr().out


def test_schema_gen_bad_type_exits_2(capsys):
    assert main(["schema", "gen", "nonsense"]) == 2
    assert "未知" in capsys.readouterr().out


def test_bots_gen_happy(capsys):
    assert main(["bots", "gen"]) == 0
    assert "user-agent" in capsys.readouterr().out.lower()


def test_llms_gen_happy(capsys):
    assert main(["llms", "gen", "--title", "示例站"]) == 0
    assert "示例站" in capsys.readouterr().out


def test_monitor_prompts_happy(capsys):
    assert main(["monitor", "prompts", "--industry", "智能客服"]) == 0
    assert "智能客服" in capsys.readouterr().out


def test_monitor_prompts_missing_industry_exits_2(capsys):
    assert main(["monitor", "prompts"]) == 2
    assert "industry" in capsys.readouterr().out.lower()


def test_monitor_score_via_file(tmp_path, capsys):
    import json
    f = tmp_path / "answers.json"
    f.write_text(json.dumps({"豆包": ["某品牌不错"]}), encoding="utf-8")
    assert main(["monitor", "score", "--answers", str(f), "--brand", "某品牌"]) == 0
    assert "引用" in capsys.readouterr().out


def test_offsite_happy(capsys):
    assert main(["offsite"]) == 0
    assert "平台" in capsys.readouterr().out


def test_unknown_command_prints_usage(capsys):
    assert main(["frobnicate"]) == 2
    assert "用法" in capsys.readouterr().out
