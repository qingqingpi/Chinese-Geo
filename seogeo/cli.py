"""seogeo CLI 入口。

  seogeo audit <url> [--format md|json]
      抓 robots/llms/sitemap/首页 → 跑全部检查 → 打分 → 中文报告（默认）或 JSON。
  seogeo monitor prompts --industry <行业/品类>
      生成去品牌化 prompt 矩阵，逐条粘进各 AI 引擎收集回答。
  seogeo monitor score --answers <file.json> --brand <品牌> [--aliases a,b] [--competitors A,B]
      从粘回的回答（JSON：{引擎:[回答,...]}）算 引用率 + SoV（零 key、确定性）。
"""
from __future__ import annotations

import json
import sys
from urllib.parse import urlparse

from seogeo.fetch import fetch
from seogeo.generate import generate_robots, generate_schema
from seogeo.monitor import generate_prompts, score_answers, verdict
from seogeo.pipeline import run_audit
from seogeo.report import render_json, render_markdown
from seogeo.rules.base import AuditContext

_USAGE = (
    "用法：\n"
    "  seogeo audit <域名或URL> [--format md|json]\n"
    "  seogeo monitor prompts --industry <行业/品类>\n"
    "  seogeo monitor score --answers <file.json> --brand <品牌> [--aliases a,b] [--competitors A,B]\n"
    "  seogeo bots gen [--sitemap <url>] [--no-domestic] [--no-overseas]\n"
    "  seogeo schema gen <organization|article|faqpage|breadcrumb>"
)


def _arg(args: list, flag: str, default=None):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default


def _csv(args: list, flag: str) -> list:
    return [x.strip() for x in (_arg(args, flag) or "").split(",") if x.strip()]


def _origin(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def _fetch_text(url: str):
    resp, err = fetch(url)
    if err:
        return None, err
    if resp["status"] == 200:
        return resp["text"], None
    if resp["status"] == 404:
        return None, None
    return None, f"HTTP {resp['status']}"


def _cmd_audit(args: list) -> int:
    if not args:
        print(_USAGE)
        return 2
    fmt = _arg(args, "--format", "md")
    origin = _origin(args[0])
    html, html_err = _fetch_text(origin)
    if html_err:
        print(f"⚠️  无法抓取首页 HTML（{html_err}）—— 结构/内容/渲染类检查将基于空内容", file=sys.stderr)
    robots_txt, robots_error = _fetch_text(origin + "/robots.txt")
    llms_txt, _ = _fetch_text(origin + "/llms.txt")
    sitemap_xml, _ = _fetch_text(origin + "/sitemap.xml")

    ctx = AuditContext(url=origin, html=html or "",
                       robots_txt=robots_txt, robots_error=robots_error,
                       llms_txt=llms_txt, sitemap_xml=sitemap_xml)
    result = run_audit(ctx)
    print(render_json(result) if fmt == "json" else render_markdown(result))
    return 1 if any(r["priority"] == "Critical" for r in result.recommendations) else 0


def _cmd_monitor(args: list) -> int:
    sub = args[0] if args else ""
    if sub == "prompts":
        industry = _arg(args, "--industry")
        if not industry:
            print("需要 --industry <行业/品类>")
            return 2
        prompts = generate_prompts(industry)
        print(f"# 去品牌化 prompt 矩阵（{industry}）—— 逐条粘进各 AI 引擎，把回答收集起来\n")
        for i, p in enumerate(prompts, 1):
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
        result = score_answers(answers, brand, _csv(args, "--aliases"), competitors)
        print(f"# 引用监控（品牌：{brand}）\n")
        for engine, m in result.items():
            if engine == "_overall":
                continue
            print(f"- {engine}：引用率 {m['citation_rate']:.0%}（{verdict(m['citation_rate'])}）"
                  f" ｜ SoV {m['share_of_voice']:.0%} ｜ 提及 {m['brand_mentions']} 次 / 答 {m['answered']} 题")
        ov = result["_overall"]["citation_rate"]
        print(f"\n总引用率：{ov:.0%}（{verdict(ov)}）　基准：<10% 差 / 10–30% 良 / >30% 优")
        return 0
    print(_USAGE)
    return 2


def _cmd_bots(args: list) -> int:
    if args and args[0] == "gen":
        print(generate_robots(
            allow_domestic="--no-domestic" not in args,
            allow_overseas="--no-overseas" not in args,
            sitemap_url=_arg(args, "--sitemap"),
        ))
        return 0
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


def main(argv: list | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else ""
    if cmd == "audit":
        return _cmd_audit(argv[1:])
    if cmd == "monitor":
        return _cmd_monitor(argv[1:])
    if cmd == "bots":
        return _cmd_bots(argv[1:])
    if cmd == "schema":
        return _cmd_schema(argv[1:])
    print(_USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main())
