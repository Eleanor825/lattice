from __future__ import annotations

from html.parser import HTMLParser
import urllib.request

from lattice.sources.common import DEFAULT_USER_AGENT, _open_with_retries, timestamp_now
from lattice.utils import normalize_whitespace, slugify


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""
        self.description = ""
        self.og_description = ""

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            attrs_dict = {key.lower(): value for key, value in attrs}
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description" and content and not self.description:
                self.description = content
            if prop == "og:description" and content and not self.og_description:
                self.og_description = content

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self.in_title:
            self.title += data


def fetch_page_document(source_name: str, url: str, domain: str, *, note: str = "") -> list[dict[str, object]]:
    request = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    with _open_with_retries(request) as response:
        text = response.read().decode("utf-8", "ignore")

    parser = _MetadataParser()
    parser.feed(text)
    title = normalize_whitespace(parser.title) or source_name.replace("_", " ").title()
    description = normalize_whitespace(parser.og_description or parser.description)
    body = description or note or f"Landing page capture for {source_name}."
    source_id = f"{source_name}-{slugify(title)}"
    return [
        {
            "schema_type": "Document",
            "source_type": source_name,
            "source_id": source_id,
            "url_or_ref": url,
            "timestamp": timestamp_now(),
            "license": "official source page terms",
            "domain": domain,
            "provenance_chain": [source_id],
            "payload": {
                "title": title,
                "text": body,
                "sections": [],
            },
        }
    ]
