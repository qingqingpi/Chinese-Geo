"""structure 确定性背书（D3，含 D2 的答案胶囊字数）：非评分结构信号，供 seogeo-structure SKILL 回调。

答案胶囊字数是经验范围、非硬标准（honesty calibration 0cd528b）——所以做成"信号 / advisory"，
不进 audit 评分（不扣分、不污染总分）。
"""
import json

from seogeo.structure_signals import analyze_structure, render_structure


def test_headings_list_table():
    html = ("<h1>标题</h1><h2>一</h2><h2>二</h2>"
            "<ul><li>x</li></ul><table><tr><td>a</td></tr></table>")
    s = analyze_structure(html)
    assert s["headings"]["h1"] == 1
    assert s["headings"]["h2"] == 2
    assert s["has_list"] is True
    assert s["has_table"] is True


def test_faq_via_jsonld():
    html = '<script type="application/ld+json">{"@type":"FAQPage"}</script>'
    assert analyze_structure(html)["faq"]["jsonld_faqpage"] is True


def test_faq_via_question_headings():
    s = analyze_structure("<h2>什么是 GEO？</h2><h2>怎么做</h2><h3>这样行吗?</h3>")
    assert s["faq"]["question_headings"] == 2  # 中文？与英文? 都算


def test_capsule_buckets_count_paragraph_chars():
    short = "<p>" + "正" * 50 + "</p>"   # 适中（40–150 字）
    wall = "<p>" + "字" * 400 + "</p>"    # 过长（>300）
    cap = analyze_structure(short + wall)["capsule"]
    assert cap["paragraphs"] == 2
    assert cap["well_sized"] == 1
    assert cap["too_long"] == 1
    assert "经验" in cap["note"] and "非硬标准" in cap["note"]  # 诚实标注


def test_empty_html_graceful():
    s = analyze_structure("")
    assert s["capsule"]["paragraphs"] == 0
    assert s["has_table"] is False
    assert s["faq"]["question_headings"] == 0


def test_render_md_is_non_scoring_and_honest():
    md = render_structure(analyze_structure("<h1>t</h1><p>" + "正" * 50 + "</p>"), "md")
    assert "结构信号" in md and "答案胶囊" in md
    assert "非评分" in md          # 明确不计分
    assert "非硬标准" in md         # 诚实标注经验范围


def test_render_json_roundtrips():
    j = json.loads(render_structure(analyze_structure("<h1>t</h1>"), "json"))
    assert j["headings"]["h1"] == 1


# —— code-review #4：块捕获状态机的隐式闭合 / EOF / 边界 ——

def test_capsule_counts_paragraphs_with_implicit_close():
    # HTML5 允许省略 </p>：<p>a<p>b 两段都要计入（隐式闭合 + EOF 冲洗）
    html = "<p>" + "正" * 50 + "<p>" + "字" * 60
    assert analyze_structure(html)["capsule"]["paragraphs"] == 2


def test_unclosed_question_heading_at_eof_detected():
    # 未闭合标题在 EOF 也要记录 → FAQ 问句识别不漏
    assert analyze_structure("<h2>这是问题吗？")["faq"]["question_headings"] == 1


def test_heading_interrupting_paragraph_keeps_both():
    # 标题打断段落（隐式边界）：段落不该整段丢失，标题也要记到
    s = analyze_structure("<p>" + "正" * 50 + "<h2>小标题</h2>")
    assert s["capsule"]["paragraphs"] == 1
    assert s["headings"]["h2"] == 1
