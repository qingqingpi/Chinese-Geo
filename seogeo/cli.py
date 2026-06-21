"""chinese-geo CLI 入口。

  chinese-geo audit <url> [--format md|json]
  chinese-geo bots gen [--sitemap <url>] [--no-domestic] [--no-overseas]
  chinese-geo bots verify <ip> <bot>
  chinese-geo schema gen <organization|article|faqpage|breadcrumb>
  chinese-geo llms gen [--title <站点名>] [--summary <一句话简介>]
  chinese-geo init [--site <站点名>] [--sitemap <url>] [--output <目录>]      # 生成站点产物
  chinese-geo init --agent <claude|codex|gemini|cursor|generic|codebuddy|kimi|opencode|qoder|trae|lingma> [--output .] # 接入某 agent
  chinese-geo monitor prompts --industry <行业/品类>
  chinese-geo monitor run --industry <X> --brand <品牌> [--engines deepseek,openai] [--aliases a,b] [--competitors A,B]
  chinese-geo monitor score --answers <file.json> --brand <品牌> [--aliases a,b] [--competitors A,B]
  chinese-geo offsite [--engine <豆包|元宝|文心|通义|DeepSeek|Kimi>] [--audience b2b|consumer]
"""
from __future__ import annotations

import json
import os
import sys

from seogeo.botverify import verify_bot_ip
from seogeo.demo import render_demo
from seogeo.engines import available_engines, run_matrix
from seogeo.generate import (
    build_agent_bundle, build_init_bundle, generate_llms, generate_robots,
    generate_schema, write_bundle,
)
from seogeo.monitor import generate_prompts, score_answers, verdict
from seogeo.offsite import cross_post_set, recommend
from seogeo.report import render_json, render_markdown
from seogeo.service import audit_url, fetch_text
from seogeo.structure_signals import analyze_structure, render_structure

_USAGE = (
    "用法：\n"
    "  chinese-geo audit <域名或URL> [--format md|json]\n"
    "  chinese-geo bots gen [--sitemap <url>] [--no-domestic] [--no-overseas]\n"
    "  chinese-geo bots verify <ip> <Baiduspider|Bytespider|PetalBot|Sogou web spider|YisouSpider>\n"
    "  chinese-geo schema gen <organization|article|faqpage|breadcrumb>\n"
    "  chinese-geo llms gen [--title <站点名>] [--summary <一句话简介>]\n"
    "  chinese-geo init [--site <站点名>] [--sitemap <url>] [--output <目录>]\n"
    "  chinese-geo init --agent <claude|codex|gemini|cursor|generic|codebuddy|kimi|opencode|qoder|trae|lingma> [--output .]\n"
    "  chinese-geo monitor prompts --industry <行业/品类>\n"
    "  chinese-geo monitor run --industry <X> --brand <品牌> [--engines deepseek,openai] [--aliases a,b] [--competitors A,B]\n"
    "  chinese-geo monitor score --answers <file.json> --brand <品牌> [--aliases a,b] [--competitors A,B]\n"
    "  chinese-geo offsite [--engine <豆包|元宝|文心|通义|DeepSeek|Kimi>] [--audience b2b|consumer]\n"
    "  chinese-geo structure <域名或URL> [--format md|json]   # 确定性结构信号（答案胶囊字数/FAQ/表格），非评分，供 structure 判断层\n"
    "  chinese-geo demo                                  # 内置 fixture 站：体检→修复→复检，前后分数对比（零 key 自证）"
)


def _arg(args: list, flag: str, default=None):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default


def _csv(args: list, flag: str) -> list:
    return [x.strip() for x in (_arg(args, flag) or "").split(",") if x.strip()]


def _cmd_audit(args: list) -> int:
    if not args or args[0].startswith("-"):  # 缺 URL，或把 --flag 误当 URL
        print(_USAGE)
        return 2
    fmt = _arg(args, "--format", "md")
    result = audit_url(args[0])
    print(render_json(result) if fmt == "json" else render_markdown(result))
    return 1 if any(r["priority"] == "Critical" for r in result.recommendations) else 0


def _cmd_bots(args: list) -> int:
    if args and args[0] == "gen":
        print(generate_robots(
            allow_domestic="--no-domestic" not in args,
            allow_overseas="--no-overseas" not in args,
            sitemap_url=_arg(args, "--sitemap"),
        ))
        return 0
    if len(args) >= 3 and args[0] == "verify":
        ip, bot = args[1], args[2]
        ok = verify_bot_ip(ip, bot)
        print(f"{ip} 声称是 {bot}：" + ("✅ 真实（反向 + 正向 DNS 校验通过）" if ok else "❌ 伪造 / 无法校验"))
        return 0 if ok else 1
    print(_USAGE)
    return 2


def _cmd_schema(args: list) -> int:
    if len(args) >= 2 and args[0] == "gen":
        try:
            print(generate_schema(args[1]))
        except ValueError as e:
            print(str(e))
            return 2
        return 0
    print("用法：chinese-geo schema gen <organization|article|faqpage|breadcrumb>")
    return 2


def _cmd_llms(args: list) -> int:
    if args and args[0] == "gen":
        print(generate_llms(_arg(args, "--title", "<站点名>"), _arg(args, "--summary")))
        return 0
    print("用法：chinese-geo llms gen [--title <站点名>] [--summary <一句话简介>]")
    return 2


def _init_agent(agent: str, out_dir: str) -> int:
    try:
        bundle = build_agent_bundle(agent)
    except ValueError as e:
        print(str(e))
        return 2
    wrote, skipped = [], []
    for name, content in bundle.items():
        path = os.path.join(out_dir, name)
        if os.path.exists(path):  # 不覆盖用户已有文件
            skipped.append(path)
            continue
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        wrote.append(path)
    for p in wrote:
        print(f"✅ 写入：{p}")
    for p in skipped:
        print(f"⏭ 已存在，跳过（如需可手动并入 chinese-geo 段）：{p}")
    # 提示按 MCP 策略分流：引导型（kimi/qoder/lingma）写的是 MCP-SETUP-*.md，需手动；其余写了真配置文件
    has_guide = any("MCP-SETUP" in os.path.basename(p) for p in wrote + skipped)
    mcp_note = ("MCP 需手动配置：见写入的 MCP-SETUP-*.md（把其中 JSON 贴进设置面板 / 全局配置）"
                if has_guide else "MCP 已配好：写入的配置文件里 chinese-geo 服务即可用")
    print(f"\n{agent} 接入完成。{mcp_note}"
          "（需 pip install \"Chinese-Geo[mcp]\" 让 chinese-geo-mcp 在 PATH 上）。")
    return 0


def _cmd_init(args: list) -> int:
    agent = _arg(args, "--agent")
    if agent:
        return _init_agent(agent, _arg(args, "--output", "."))
    out_dir = _arg(args, "--output", "seogeo-output")
    bundle = build_init_bundle(
        site_title=_arg(args, "--site", "<站点名>"),
        sitemap_url=_arg(args, "--sitemap"),
        summary=_arg(args, "--summary"),
    )
    paths = write_bundle(bundle, out_dir)
    print(f"✅ 已生成 {len(paths)} 个文件到 {out_dir}/：")
    for p in paths:
        print(f"  - {p}")
    print("\n下一步：把文件里的占位符 <…> 改成真实信息；robots.txt / llms.txt 放站点根目录，"
          "schema 片段贴进 <head>，按 canonical 清单逐页自查。")
    return 0


def _print_score(result: dict, brand: str) -> None:
    print(f"# 引用监控（品牌：{brand}）\n")
    for engine, m in result.items():
        if engine == "_overall":
            continue
        print(f"- {engine}：引用率 {m['citation_rate']:.0%}（{verdict(m['citation_rate'])}）"
              f" ｜ SoV {m['share_of_voice']:.0%} ｜ 提及 {m['brand_mentions']} 次 / 答 {m['answered']} 题")
    ov = result["_overall"]["citation_rate"]
    print(f"\n总引用率：{ov:.0%}（{verdict(ov)}）　基准：<10% 差 / 10–30% 良 / >30% 优")


def _cmd_monitor(args: list) -> int:
    sub = args[0] if args else ""
    if sub == "prompts":
        industry = _arg(args, "--industry")
        if not industry:
            print("需要 --industry <行业/品类>")
            return 2
        print(f"# 去品牌化 prompt 矩阵（{industry}）—— 逐条粘进各 AI 引擎，把回答收集起来\n")
        for i, p in enumerate(generate_prompts(industry), 1):
            print(f"{i}. [{p['stage']}] {p['text']}")
        return 0
    if sub == "score":
        path = _arg(args, "--answers")
        brand = _arg(args, "--brand")
        if not path or not brand:
            print("需要 --answers <file.json> 和 --brand <品牌>")
            return 2
        competitors = {name: [] for name in _csv(args, "--competitors")}
        with open(path, encoding="utf-8") as f:
            answers = json.load(f)
        _print_score(score_answers(answers, brand, _csv(args, "--aliases"), competitors), brand)
        return 0
    if sub == "run":
        industry = _arg(args, "--industry")
        brand = _arg(args, "--brand")
        if not industry or not brand:
            print("需要 --industry <行业/品类> 和 --brand <品牌>")
            return 2
        avail = available_engines()
        if not avail:
            print("没有可用引擎：先设置至少一个 API key 环境变量，例如 DEEPSEEK_API_KEY / "
                  "OPENAI_API_KEY / PERPLEXITY_API_KEY / DASHSCOPE_API_KEY / ARK_API_KEY / MOONSHOT_API_KEY。")
            return 2
        only = _csv(args, "--engines") or None
        used = [e for e in (only or avail) if e in avail]
        prompts = [p["text"] for p in generate_prompts(industry)]
        print(f"# BYOK 自动跑：{len(prompts)} 问 × {len(used)} 引擎（{', '.join(used)}）…", file=sys.stderr)
        answers = run_matrix(prompts, engines=only)
        competitors = {name: [] for name in _csv(args, "--competitors")}
        _print_score(score_answers(answers, brand, _csv(args, "--aliases"), competitors), brand)
        print("\n注：BYOK 调的是各引擎 API 模型，默认不联网检索（Perplexity 除外）；"
              "要测真实联网引用，仍以消费版手动粘贴为准（monitor prompts + score）。")
        return 0
    print(_USAGE)
    return 2


def _cmd_offsite(args: list) -> int:
    engine = _arg(args, "--engine")
    audience = _arg(args, "--audience")
    plats = recommend(engine=engine, audience=audience)
    filt = []
    if engine:
        filt.append(f"喂 {engine}")
    if audience:
        filt.append("B2B/科技" if audience == "b2b" else "消费/生活")
    print("# 国内社媒 / 站外平台矩阵" + (f"（筛选：{'、'.join(filt)}）" if filt else "") + "\n")
    if not plats:
        print("没有匹配平台。引擎：豆包/元宝/文心/通义/DeepSeek/Kimi；受众：b2b/consumer。")
        return 0
    print("## 推荐平台（平台 → 喂哪些引擎 ｜ 受众 ｜ 开放/封闭；次行=被哪个搜索索引 + 打法）")
    for p in plats:
        aud = "/".join("B2B" if a == "b2b" else "消费" for a in p.audiences)
        kind = "开放" if p.open else "封闭(平台内SEO)"
        print(f"- {p.name} → 喂 {'/'.join(p.engines)} ｜ {aud} ｜ {kind}")
        print(f"    被索引：{p.indexed_by}　{p.tip}")
    print("\n## 一题多发（同文改写、多平台同步）")
    print(" / ".join(cross_post_set()) + " —— 一次产出、多源覆盖")
    closed = [p for p in plats if not p.open]
    if closed:
        print("\n## 封闭型（外部 AI 不引，想被引就进场内做平台内 SEO）")
        for p in closed:
            print(f"- {p.name}：{p.tip}")
    print("\n> 每家 AI 主要吃自己生态——按目标引擎 / 受众选平台分发，别一稿到处糊；"
          "占比是单行业样本，方向可信、数值仅参考。")
    return 0


def _cmd_structure(args: list) -> int:
    if not args or args[0].startswith("-"):  # 缺 URL，或把 --flag 误当 URL
        print(_USAGE)
        return 2
    url = args[0]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    html, err = fetch_text(url)
    if html is None:  # 抓不到就别拿空 HTML 当"页面无结构"误报
        print(f"无法获取页面 HTML（{err or 'HTTP 404'}）。先确认 URL 可访问再重试。")
        return 2
    print(render_structure(analyze_structure(html), _arg(args, "--format", "md")))
    return 0


def _cmd_demo(args: list) -> int:
    print(render_demo())
    return 0


def main(argv: list | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else ""
    dispatch = {"audit": _cmd_audit, "bots": _cmd_bots, "schema": _cmd_schema,
                "llms": _cmd_llms, "init": _cmd_init, "monitor": _cmd_monitor,
                "offsite": _cmd_offsite, "structure": _cmd_structure, "demo": _cmd_demo}
    if cmd in dispatch:
        return dispatch[cmd](argv[1:])
    print(_USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main())
