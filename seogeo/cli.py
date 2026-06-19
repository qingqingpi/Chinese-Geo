"""seogeo CLI 入口。

  seogeo audit <url> [--format md|json]
  seogeo bots gen [--sitemap <url>] [--no-domestic] [--no-overseas]
  seogeo bots verify <ip> <bot>
  seogeo schema gen <organization|article|faqpage|breadcrumb>
  seogeo llms gen [--title <站点名>] [--summary <一句话简介>]
  seogeo init [--site <站点名>] [--sitemap <url>] [--output <目录>]
  seogeo monitor prompts --industry <行业/品类>
  seogeo monitor run --industry <X> --brand <品牌> [--engines deepseek,openai] [--aliases a,b] [--competitors A,B]
  seogeo monitor score --answers <file.json> --brand <品牌> [--aliases a,b] [--competitors A,B]
"""
from __future__ import annotations

import json
import sys

from seogeo.botverify import verify_bot_ip
from seogeo.engines import available_engines, run_matrix
from seogeo.generate import (
    build_init_bundle, generate_llms, generate_robots, generate_schema, write_bundle,
)
from seogeo.monitor import generate_prompts, score_answers, verdict
from seogeo.report import render_json, render_markdown
from seogeo.service import audit_url

_USAGE = (
    "用法：\n"
    "  seogeo audit <域名或URL> [--format md|json]\n"
    "  seogeo bots gen [--sitemap <url>] [--no-domestic] [--no-overseas]\n"
    "  seogeo bots verify <ip> <Baiduspider|Bytespider|PetalBot|Sogou web spider|YisouSpider>\n"
    "  seogeo schema gen <organization|article|faqpage|breadcrumb>\n"
    "  seogeo llms gen [--title <站点名>] [--summary <一句话简介>]\n"
    "  seogeo init [--site <站点名>] [--sitemap <url>] [--output <目录>]\n"
    "  seogeo monitor prompts --industry <行业/品类>\n"
    "  seogeo monitor run --industry <X> --brand <品牌> [--engines deepseek,openai] [--aliases a,b] [--competitors A,B]\n"
    "  seogeo monitor score --answers <file.json> --brand <品牌> [--aliases a,b] [--competitors A,B]"
)


def _arg(args: list, flag: str, default=None):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default


def _csv(args: list, flag: str) -> list:
    return [x.strip() for x in (_arg(args, flag) or "").split(",") if x.strip()]


def _cmd_audit(args: list) -> int:
    if not args:
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
    print("用法：seogeo schema gen <organization|article|faqpage|breadcrumb>")
    return 2


def _cmd_llms(args: list) -> int:
    if args and args[0] == "gen":
        print(generate_llms(_arg(args, "--title", "<站点名>"), _arg(args, "--summary")))
        return 0
    print("用法：seogeo llms gen [--title <站点名>] [--summary <一句话简介>]")
    return 2


def _cmd_init(args: list) -> int:
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


def main(argv: list | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else ""
    dispatch = {"audit": _cmd_audit, "bots": _cmd_bots, "schema": _cmd_schema,
                "llms": _cmd_llms, "init": _cmd_init, "monitor": _cmd_monitor}
    if cmd in dispatch:
        return dispatch[cmd](argv[1:])
    print(_USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main())
