"""DOM 扫描器：一遍 `html.parser` 扫出体检需要的全部信号（零依赖，替代 BeautifulSoup）。

移植自竞品 audit 代理给的 `_DomScanner` 骨架，补了 has_list/has_table 与中文友好的 text_length。
"""
from __future__ import annotations

from html.parser import HTMLParser


class DomScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.lang = ""
        self.canonical = ""
        self.headings = {f"h{i}": 0 for i in range(1, 7)}
        self.metas: dict = {}
        self.jsonld_blocks: list = []
        self.links: list = []
        self.has_list = False
        self.has_table = False
        self.images = 0
        self.images_missing_alt = 0  # <img> 无 alt 属性（alt="" 是装饰性合法用法，不计入）
        self._in_title = False
        self._in_jsonld = False
        self._jsonld_buf: list = []
        self._in_skip = False  # script/style 内不计入可见文本
        self._text_parts: list = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html" and a.get("lang"):
            self.lang = a["lang"]
        if tag == "title":
            self._in_title = True
        if tag in self.headings:
            self.headings[tag] += 1
        if tag == "link" and a.get("rel", "").lower() == "canonical":
            self.canonical = a.get("href", "")
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.metas[key.lower()] = a.get("content", "")
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("ul", "ol", "dl"):
            self.has_list = True
        if tag == "table":
            self.has_table = True
        if tag == "img":
            self.images += 1
            if "alt" not in a:
                self.images_missing_alt += 1
        if tag in ("script", "style"):
            self._in_skip = True
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in ("script", "style"):
            self._in_skip = False
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld_blocks.append("".join(self._jsonld_buf))

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        elif not self._in_skip:
            self._text_parts.append(data)

    @property
    def text(self) -> str:
        return " ".join("".join(self._text_parts).split())

    @property
    def text_length(self) -> int:
        """非空白字符数——对中文（无空格）有效。"""
        return len(self.text.replace(" ", ""))

    @property
    def word_count(self) -> int:
        """按空格切词——仅供英文参考；中文不可靠。"""
        return len(self.text.split())


def scan(html: str) -> DomScanner:
    d = DomScanner()
    d.feed(html or "")
    return d
