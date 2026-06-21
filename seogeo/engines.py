"""BYOK 引擎自动跑（铁律2：自带 key 才解锁增强；零依赖、可选）。

把 monitor 的 prompt 矩阵自动喂给各 AI 引擎。多数引擎都暴露 OpenAI 兼容
/chat/completions，故一个泛化客户端 + 注册表即可覆盖国内外。HTTP 与 env 均可注入。

诚实边界：这里调的是各引擎的 **API 模型**，默认不联网检索（Perplexity sonar 除外）；
要测真实"联网引用"，仍以消费版手动粘贴为准（见 seogeo-monitor / `monitor prompts`+`score`）。
"""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Engine:
    name: str
    base_url: str
    model: str       # 默认模型；可用环境变量 {NAME}_MODEL 覆盖
    key_env: str
    web_grounded: bool = False
    protocol: str = "openai"  # "openai"=/chat/completions Bearer；"gemini"=generateContent + query key


ENGINES = {e.name: e for e in [
    # 海外
    Engine("perplexity", "https://api.perplexity.ai", "sonar", "PERPLEXITY_API_KEY", web_grounded=True),
    Engine("openai", "https://api.openai.com/v1", "gpt-4o-mini", "OPENAI_API_KEY"),
    Engine("gemini", "https://generativelanguage.googleapis.com/v1beta", "gemini-1.5-flash",
           "GEMINI_API_KEY", protocol="gemini"),  # 原生 generateContent（非 OpenAI 兼容）
    # 国内
    Engine("deepseek", "https://api.deepseek.com/v1", "deepseek-chat", "DEEPSEEK_API_KEY"),
    Engine("qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus", "DASHSCOPE_API_KEY"),
    Engine("doubao", "https://ark.cn-beijing.volces.com/api/v3", "doubao-pro-32k", "ARK_API_KEY"),
    Engine("moonshot", "https://api.moonshot.cn/v1", "moonshot-v1-8k", "MOONSHOT_API_KEY"),
    # 文心一言：百度千帆 v2 的 OpenAI 兼容端点；BYOK 用户提供 v2 应用 API key（QIANFAN_API_KEY）。
    # 注：千帆鉴权随版本演进，若你的应用走旧版 access_token，请按需在此调整 base_url / 鉴权。
    Engine("ernie", "https://qianfan.baidubce.com/v2", "ernie-4.0-8k", "QIANFAN_API_KEY"),
    # 元宝（腾讯）：无公开 API → 不接入，监控用消费版手动粘贴（monitor prompts + score）。
]}


def _http_post(url: str, headers: dict, payload: dict, timeout: int = 60) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (固定 https 引擎域名)
        return json.loads(r.read().decode("utf-8"))


def available_engines(env=None) -> list:
    """返回已配置 API key（key_env 在 env 里有值）的引擎名。"""
    env = os.environ if env is None else env
    return [name for name, e in ENGINES.items() if env.get(e.key_env)]


def ask(engine_name: str, prompt: str, *, api_key: str | None = None,
        model: str | None = None, http=None, env=None) -> str:
    """问单个引擎一个 prompt，返回回答文本。支持 OpenAI 兼容与 Gemini 原生两种协议。"""
    env = os.environ if env is None else env
    eng = ENGINES[engine_name]
    key = api_key or env.get(eng.key_env)
    if not key:
        raise RuntimeError(f"{engine_name} 缺少 API key —— 请设置环境变量 {eng.key_env}")
    http = http or _http_post
    model = model or env.get(f"{engine_name.upper()}_MODEL") or eng.model

    if eng.protocol == "gemini":  # 原生 generateContent：query key（非 Bearer）、contents/parts 形状
        url = f"{eng.base_url.rstrip('/')}/models/{model}:generateContent?key={key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}],
                   "generationConfig": {"temperature": 0.3}}
        resp = http(url, {"Content-Type": "application/json"}, payload)
        # 安全过滤 / 空响应时 candidates 可能为 []，或候选无 content（finishReason=SAFETY）：
        # 降级成空答案（计为未提及），别让一条被拦的 prompt 抛异常炸掉整个矩阵。
        cands = resp.get("candidates") or []
        parts = ((cands[0].get("content") or {}).get("parts") if cands else None) or []
        return parts[0].get("text", "") if parts else ""

    # OpenAI 兼容 /chat/completions
    url = eng.base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
    resp = http(url, headers, payload)
    return resp["choices"][0]["message"]["content"]


def run_matrix(prompts: list, engines=None, *, http=None, env=None) -> dict:
    """对每个可用引擎跑完整 prompt 矩阵，返回 {引擎: [回答, ...]}——直接喂给 score_answers。"""
    env = os.environ if env is None else env
    avail = available_engines(env)
    names = [n for n in (engines or avail) if n in avail]  # 缺 key 的引擎自动跳过
    return {
        n: [ask(n, p, api_key=env.get(ENGINES[n].key_env), http=http, env=env) for p in prompts]
        for n in names
    }
