"""生成器：把诊断变成可复制的修复产物。

- generate_robots：推荐 robots.txt——国内爬虫"各家单独成块"（差异化核心）、海外爬虫可合并。
- generate_schema：JSON-LD 脚手架（Organization/Article/FAQPage/Breadcrumb）。
"""
import pytest

from seogeo.generate import (
    build_agent_bundle,
    build_init_bundle,
    generate_llms,
    generate_robots,
    generate_schema,
    write_bundle,
)


# ---- robots ----

def test_robots_separate_block_per_domestic_bot():
    out = generate_robots()
    # 每个国内爬虫各自单独成块（对 Bytespider/搜狗 是保险做法）
    assert "User-agent: Baiduspider\nAllow: /" in out
    assert "User-agent: Bytespider\nAllow: /" in out
    assert "User-agent: Sogou web spider\nAllow: /" in out


def test_robots_allows_overseas_bots():
    out = generate_robots()
    assert "GPTBot" in out
    assert "PerplexityBot" in out


def test_robots_has_default_allow_all():
    assert "User-agent: *" in generate_robots()


def test_robots_includes_sitemap_when_given():
    out = generate_robots(sitemap_url="https://x.com/sitemap.xml")
    assert "Sitemap: https://x.com/sitemap.xml" in out


def test_robots_notes_bytespider_hardblock():
    # 提示 Bytespider 不守 robots、需服务端硬拦
    out = generate_robots()
    assert "Bytespider" in out
    assert "robots" in out and ("硬拦" in out or "WAF" in out)


def test_robots_can_skip_domestic():
    out = generate_robots(allow_domestic=False)
    assert "Baiduspider" not in out


# ---- schema ----

def test_schema_organization():
    out = generate_schema("organization")
    assert '"@type": "Organization"' in out
    assert "schema.org" in out


def test_schema_faqpage():
    out = generate_schema("faqpage")
    assert "FAQPage" in out
    assert "Question" in out


def test_schema_case_insensitive():
    assert "Article" in generate_schema("Article")


def test_schema_wrapped_in_script_tag():
    assert generate_schema("organization").startswith('<script type="application/ld+json">')


def test_schema_unknown_raises():
    with pytest.raises(ValueError):
        generate_schema("nonsense")


# ---- llms.txt ----

def test_llms_starts_with_title_h1():
    assert generate_llms("示例公司").startswith("# 示例公司")


def test_llms_summary_as_blockquote():
    assert "> 一句话简介" in generate_llms("示例公司", summary="一句话简介")


def test_llms_has_section_with_link_bullets():
    # llms.txt 规范核心结构：至少一个 H2 段 + markdown 链接条目
    out = generate_llms("示例公司")
    assert "## " in out
    assert "](" in out


def test_llms_renders_given_links():
    out = generate_llms("示例公司", links=[("产品介绍", "https://x.com/p", "核心产品")])
    assert "[产品介绍](https://x.com/p)" in out
    assert "核心产品" in out


def test_llms_notes_overseas_oriented():
    # 诚实标注：llms.txt 主要面向海外引擎（国内基本无效）
    assert "海外" in generate_llms("示例公司")


# ---- init bundle ----

def test_init_bundle_has_four_artifacts():
    bundle = build_init_bundle("示例公司")
    assert {"robots.txt", "llms.txt"} <= set(bundle)
    assert any("schema" in k for k in bundle)
    assert any(k.endswith(".md") for k in bundle)  # canonical / meta 清单


def test_init_bundle_robots_carries_sitemap():
    bundle = build_init_bundle("示例公司", sitemap_url="https://x.com/sitemap.xml")
    assert "Sitemap: https://x.com/sitemap.xml" in bundle["robots.txt"]


def test_init_bundle_llms_uses_site_title():
    assert "# 示例公司" in build_init_bundle("示例公司")["llms.txt"]


def test_init_bundle_canonical_checklist_mentions_canonical_and_lang():
    bundle = build_init_bundle("示例公司")
    md = next(v for k, v in bundle.items() if k.endswith(".md"))
    assert "canonical" in md.lower()
    assert "lang" in md.lower()  # <html lang> 也在清单里


# ---- write_bundle ----

def test_write_bundle_creates_dir_and_files(tmp_path):
    out = str(tmp_path / "out")  # 目录尚不存在，应被创建
    paths = write_bundle({"robots.txt": "X", "llms.txt": "Y"}, out)
    assert (tmp_path / "out" / "robots.txt").read_text(encoding="utf-8") == "X"
    assert (tmp_path / "out" / "llms.txt").read_text(encoding="utf-8") == "Y"
    assert len(paths) == 2


def test_write_bundle_creates_nested_dirs(tmp_path):
    write_bundle({".cursor/rules/x.mdc": "Y"}, str(tmp_path / "p"))
    assert (tmp_path / "p" / ".cursor" / "rules" / "x.mdc").read_text(encoding="utf-8") == "Y"


# ---- agent 安装包（init --agent）----

def test_agent_bundle_claude_has_instruction_and_mcp():
    b = build_agent_bundle("claude")
    assert "CLAUDE.md" in b and ".mcp.json" in b
    assert "chinese-geo audit" in b["CLAUDE.md"]


def test_agent_bundle_cursor_uses_nested_rules_path():
    assert ".cursor/rules/seogeo.mdc" in build_agent_bundle("cursor")


def test_agent_bundle_mcp_is_valid_json_with_server():
    import json
    mcp = json.loads(build_agent_bundle("gemini")[".mcp.json"])
    assert "chinese-geo" in mcp["mcpServers"]


def test_agent_bundle_instruction_is_neutral_terminology():
    blurb = build_agent_bundle("claude")["CLAUDE.md"]
    assert chr(0x4e2d) + chr(0x56fd) not in blurb  # 不含地缘国名词
    assert chr(0x897f) + chr(0x65b9) not in blurb  # 不含地缘方位词


def test_agent_bundle_unknown_raises():
    with pytest.raises(ValueError):
        build_agent_bundle("nonsense")


# ---- A1: 国内 / 开源 agent（CodeBuddy / Kimi / opencode）----

def test_agent_bundle_codebuddy_uses_own_instruction_and_standard_mcp():
    import json
    b = build_agent_bundle("codebuddy")
    assert "CODEBUDDY.md" in b                          # CodeBuddy 专属指令文件
    assert "mcpServers" in json.loads(b[".mcp.json"])   # 项目级 .mcp.json（mcpServers）


def test_agent_bundle_opencode_uses_opencode_json_with_mcp_key_and_type():
    import json
    b = build_agent_bundle("opencode")
    assert "AGENTS.md" in b
    cfg = json.loads(b["opencode.json"])
    assert "mcp" in cfg and "mcpServers" not in cfg      # opencode 用 mcp，不是 mcpServers
    assert cfg["mcp"]["chinese-geo"]["type"] == "local"  # 每个 server 必须带 type


def test_agent_bundle_kimi_gives_manual_mcp_guide_not_home_path():
    b = build_agent_bundle("kimi")
    assert "AGENTS.md" in b                              # 指令走事实标准 AGENTS.md
    assert any("MCP-SETUP" in name for name in b)        # 全局 MCP → 手动指引文件
    assert not any(name.startswith(("/", "~")) for name in b)  # 绝不写 home / 绝对路径


# ---- A1b: rules-dir 指令 + UI-only MCP（Qoder / Trae / Lingma）----

def test_agent_bundle_qoder_writes_root_agents_and_ui_mcp_guide():
    b = build_agent_bundle("qoder")
    assert "AGENTS.md" in b                              # Qoder 原生读根 AGENTS.md，写它省一套
    assert "MCP-SETUP-qoder.md" in b                     # MCP 是 UI-only → 手动贴 JSON 指引
    assert ".mcp.json" not in b                          # 不自动写 MCP 文件
    assert not any(name.startswith(("/", "~")) for name in b)  # 不碰 app 私有/绝对路径


def test_agent_bundle_trae_uses_rules_dir_and_own_mcp_path():
    import json
    b = build_agent_bundle("trae")
    assert ".trae/rules/project_rules.md" in b           # Trae 指令落点（rules-dir）
    assert ".trae/mcp.json" in b                         # Trae 有稳定项目级 MCP 文件
    assert ".mcp.json" not in b                          # 不是根 .mcp.json
    assert "mcpServers" in json.loads(b[".trae/mcp.json"])  # 键是 mcpServers


def test_agent_bundle_lingma_uses_rules_dir_and_ui_mcp_guide():
    b = build_agent_bundle("lingma")
    assert ".lingma/rules/seogeo.md" in b                # Lingma rules-dir 指令
    assert "MCP-SETUP-lingma.md" in b                    # UI-only（跨工程共享）→ 手动贴 JSON
    assert ".mcp.json" not in b


def test_agent_bundle_ui_mcp_guide_has_pasteable_mcpservers_json():
    import json
    import re
    guide = build_agent_bundle("qoder")["MCP-SETUP-qoder.md"]
    block = re.search(r"```json\n(.*?)\n```", guide, re.S).group(1)  # 指引里要有可直接贴的 JSON
    assert "chinese-geo" in json.loads(block)["mcpServers"]
