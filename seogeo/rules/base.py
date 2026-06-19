"""规则系统基座：审计上下文 + 检查结果。

契约设计移植自 SEOmator `types.ts`（AuditContext / RuleResult）：每条检查吃同一个
AuditContext、吐一个 CheckOutcome。严重度由 run() 返回的 status 动态决定（pass/warn/fail），
不是规则的静态属性。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AuditContext:
    """一次审计共享的数据。Tier1 总有（html/headers）；Tier2 网络抓的可选（robots/sitemap）；
    Tier4 渲染可选（rendered_html）。"""
    url: str
    html: str = ""
    headers: dict = field(default_factory=dict)
    status: int = 200
    robots_txt: str | None = None
    robots_error: str | None = None  # 抓 robots.txt 失败的原因（403/网络错误等）；区别于"真无 robots"
    llms_txt: str | None = None
    sitemap_xml: str | None = None
    rendered_html: str | None = None
    dom: object | None = None  # 解析后的 DomScanner（由 pipeline 从 html 解析）
    bytespider_blocked: bool | None = None  # Bytespider 服务端硬拦探测结果（None=未探测）


@dataclass
class CheckOutcome:
    """单条检查的结果。"""
    id: str
    status: str  # "pass" | "warn" | "fail"
    message: str  # 人话结论
    recommendation: str = ""  # 修复建议（fail/warn 时给）
    score: int = 0  # 该 check 实得分
    max_score: int = 0
    evidence: dict = field(default_factory=dict)
    category: str = ""  # 由 pipeline 从 registry 标注，供打分按类目分组


def outcome(rule_id: str, weight: int, status: str, message: str,
            recommendation: str = "", evidence: dict | None = None) -> CheckOutcome:
    """按 status 折算得分（pass=满分 / warn=半分 / fail=0）构造 CheckOutcome。"""
    score = {"pass": weight, "warn": weight // 2, "fail": 0}[status]
    return CheckOutcome(rule_id, status, message, recommendation, score, weight, evidence or {})


@dataclass
class Rule:
    id: str
    category: str
    weight: int
    run: Callable


class Registry:
    """规则注册表：一规则一文件，用 @register 装饰器自注册（SEOmator registry.ts 思路）。"""

    def __init__(self) -> None:
        self._rules: dict = {}

    def register(self, *, id: str, category: str, weight: int):
        def deco(fn):
            if id in self._rules:
                raise ValueError(f"duplicate rule id: {id}")
            self._rules[id] = Rule(id, category, weight, fn)
            return fn
        return deco

    def all(self) -> list:
        return list(self._rules.values())

    def get(self, rule_id: str):
        return self._rules.get(rule_id)


REGISTRY = Registry()         # 全局默认注册表
register = REGISTRY.register   # 便捷装饰器（绑定到全局）
