from __future__ import annotations

import unittest

from lattice.sources.arxiv import parse_arxiv_feed
from lattice.sources.openalex import reconstruct_abstract


class SourceParsingTest(unittest.TestCase):
    def test_reconstruct_openalex_abstract(self) -> None:
        inverted_index = {
            "Solid": [0],
            "state": [1],
            "electrolytes": [2],
            "enable": [3],
            "safer": [4],
            "batteries.": [5],
        }
        text = reconstruct_abstract(inverted_index)
        self.assertEqual(text, "Solid state electrolytes enable safer batteries.")

    def test_parse_arxiv_feed(self) -> None:
        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2501.00001v1</id>
    <updated>2025-01-01T00:00:00Z</updated>
    <published>2025-01-01T00:00:00Z</published>
    <title> Solid-state battery review </title>
    <summary> A short summary about electrolytes. </summary>
    <author><name>Jane Doe</name></author>
    <category term="cond-mat.mtrl-sci" />
  </entry>
</feed>"""
        rows = parse_arxiv_feed(xml_text, domain="materials")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["schema_type"], "Document")
        self.assertEqual(rows[0]["source_type"], "arxiv")
        self.assertIn("electrolytes", rows[0]["payload"]["text"])


if __name__ == "__main__":
    unittest.main()
