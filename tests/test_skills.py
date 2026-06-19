"""跨 agent 可移植性护栏：SKILL.md 必须 vendor-neutral 且术语中性（CLAUDE.md L4 铁律①）。

skill 正文绝不能出现某家专属语法（如 Claude 的 !`command` 动态执行）——否则换个
runtime 就废。产品也不得出现地缘对立词（一律改用 国内 / 海外）。这就是那个"校验脚本"。
"""
import glob
import os

import pytest

_SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")
_SKILLS = sorted(glob.glob(os.path.join(_SKILLS_DIR, "*", "SKILL.md")))


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_all_five_skills_present():
    names = {os.path.basename(os.path.dirname(p)) for p in _SKILLS}
    assert {"seogeo-audit", "seogeo-monitor", "seogeo-structure",
            "seogeo-content", "seogeo-offsite"} <= names


@pytest.mark.parametrize("path", _SKILLS, ids=lambda p: os.path.basename(os.path.dirname(p)))
def test_skill_has_frontmatter_name_and_description(path):
    text = _read(path)
    assert text.startswith("---\n")
    front = text.split("---", 2)[1]
    assert "name:" in front and "description:" in front


@pytest.mark.parametrize("path", _SKILLS, ids=lambda p: os.path.basename(os.path.dirname(p)))
def test_skill_is_vendor_neutral(path):
    # Claude 专属：!`command` 动态执行；正文出现即破坏跨 agent 可移植
    assert "!`" not in _read(path), f"{path} 含 Claude 专属 !`command` 语法"


# 用码点构造禁用词，避免本文件自身在产品源码里出现这两个字面词（自我遵守中性化铁律）。
_BANNED_GEO_TERMS = (chr(0x4e2d) + chr(0x56fd), chr(0x897f) + chr(0x65b9))  # 两个地缘对立词


@pytest.mark.parametrize("path", _SKILLS, ids=lambda p: os.path.basename(os.path.dirname(p)))
def test_skill_uses_neutral_terminology(path):
    text = _read(path)
    for banned in _BANNED_GEO_TERMS:
        assert banned not in text, f"{path} 含禁用地缘对立词，应改用 国内 / 海外"
