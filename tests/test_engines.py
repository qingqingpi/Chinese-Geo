"""BYOK 引擎自动跑（铁律2）：自带 key 时把 prompt 矩阵自动喂给各 AI 引擎。

多数引擎（OpenAI / DeepSeek / 通义 / 豆包 / Kimi / Perplexity）都暴露 OpenAI 兼容
/chat/completions，故用一个泛化客户端 + 注册表覆盖。HTTP 与 env 均可注入，零网络可测。
"""
import pytest

from seogeo.engines import ENGINES, ask, available_engines, run_matrix


def _fake_http(prefix="答案"):
    def http(url, headers, payload):
        http.calls.append({"url": url, "headers": headers, "payload": payload})
        msg = payload["messages"][0]["content"]
        return {"choices": [{"message": {"content": f"{prefix}:{msg}"}}]}
    http.calls = []
    return http


# ---- 注册表 ----

def test_registry_covers_domestic_and_overseas():
    assert {"deepseek", "qwen", "doubao", "moonshot"} <= set(ENGINES)   # 国内
    assert {"openai", "perplexity"} <= set(ENGINES)                      # 海外
    for e in ENGINES.values():
        assert e.base_url.startswith("http") and e.model and e.key_env


# ---- available_engines ----

def test_available_engines_filters_by_env():
    assert available_engines(env={"DEEPSEEK_API_KEY": "x", "IRRELEVANT": "y"}) == ["deepseek"]


def test_available_engines_empty_when_no_keys():
    assert available_engines(env={}) == []


# ---- ask ----

def test_ask_builds_openai_request_and_parses():
    http = _fake_http("回答")
    out = ask("deepseek", "你好", api_key="sk-x", http=http)
    assert out == "回答:你好"
    c = http.calls[0]
    assert c["url"].endswith("/chat/completions")
    assert c["headers"]["Authorization"] == "Bearer sk-x"
    assert c["payload"]["model"] == "deepseek-chat"
    assert c["payload"]["messages"][0]["content"] == "你好"


def test_ask_missing_key_raises():
    with pytest.raises(RuntimeError):
        ask("deepseek", "q", env={}, http=_fake_http())


def test_ask_model_override_via_env():
    http = _fake_http()
    ask("doubao", "q", api_key="k", http=http, env={"DOUBAO_MODEL": "ep-123"})
    assert http.calls[0]["payload"]["model"] == "ep-123"


# ---- run_matrix（返回 score_answers 直接吃的形状）----

def test_run_matrix_returns_score_ready_shape():
    http = _fake_http("A")
    out = run_matrix(["q1", "q2"], env={"DEEPSEEK_API_KEY": "x"}, http=http)
    assert set(out) == {"deepseek"}
    assert out["deepseek"] == ["A:q1", "A:q2"]


def test_run_matrix_skips_engines_without_key():
    out = run_matrix(["q"], engines=["deepseek", "openai"],
                     env={"DEEPSEEK_API_KEY": "x"}, http=_fake_http())
    assert set(out) == {"deepseek"}  # openai 无 key → 跳过


# ---- D5：Gemini 原生协议 + 文心（Qianfan v2 兼容） ----

def _fake_gemini_http(prefix="答案"):
    def http(url, headers, payload):
        http.calls.append({"url": url, "headers": headers, "payload": payload})
        text = payload["contents"][0]["parts"][0]["text"]
        return {"candidates": [{"content": {"parts": [{"text": f"{prefix}:{text}"}]}}]}
    http.calls = []
    return http


def test_registry_includes_gemini_and_ernie():
    assert "gemini" in ENGINES and "ernie" in ENGINES
    assert ENGINES["gemini"].protocol == "gemini"
    assert ENGINES["ernie"].protocol == "openai"  # 文心走百度千帆 v2 OpenAI 兼容端点


def test_ask_gemini_native_request_and_parse():
    http = _fake_gemini_http("回答")
    out = ask("gemini", "你好", api_key="gk", http=http)
    assert out == "回答:你好"
    c = http.calls[0]
    assert ":generateContent" in c["url"] and "key=gk" in c["url"]  # query key，非 Bearer
    assert "Authorization" not in c["headers"]
    assert c["payload"]["contents"][0]["parts"][0]["text"] == "你好"


def test_ask_ernie_uses_openai_compatible_qianfan_v2():
    http = _fake_http("回答")
    out = ask("ernie", "你好", api_key="qk", http=http)
    assert out == "回答:你好"
    c = http.calls[0]
    assert c["url"].startswith("https://qianfan.baidubce.com/v2")
    assert c["url"].endswith("/chat/completions")
    assert c["headers"]["Authorization"] == "Bearer qk"


def test_available_engines_includes_gemini_and_ernie():
    avail = available_engines(env={"GEMINI_API_KEY": "x", "QIANFAN_API_KEY": "y"})
    assert "gemini" in avail and "ernie" in avail


def test_run_matrix_mixes_protocols():
    # 同一矩阵里 gemini（原生）与 deepseek（兼容）都能跑，回答正确归位
    def http(url, headers, payload):
        if ":generateContent" in url:
            t = payload["contents"][0]["parts"][0]["text"]
            return {"candidates": [{"content": {"parts": [{"text": "G:" + t}]}}]}
        t = payload["messages"][0]["content"]
        return {"choices": [{"message": {"content": "D:" + t}}]}
    env = {"GEMINI_API_KEY": "g", "DEEPSEEK_API_KEY": "d"}
    out = run_matrix(["问"], engines=["gemini", "deepseek"], http=http, env=env)
    assert out["gemini"] == ["G:问"] and out["deepseek"] == ["D:问"]
