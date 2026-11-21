"""Tests for find_papers.py, offline (no network).   python3 -m unittest discover -s tests"""
from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "plugins" / "chizen" / "skills" / "related-work" / "scripts"))
import find_papers  # noqa: E402

# The shape of a Crossref work record (fields as the API names them); values are placeholders.
RECORD = {
    "DOI": "10.1145/0000000.0000001",
    "title": ["A Placeholder Title"],
    "author": [{"given": "Ada", "family": "Example"}, {"given": "Bo", "family": "Sample"},
               {"given": "Cy", "family": "Test"}, {"given": "Di", "family": "Fixture"}],
    "issued": {"date-parts": [[2024, 5]]},
    "container-title": ["Proceedings of a Conference"],
    "type": "proceedings-article",
    "abstract": "<jats:title>Abstract</jats:title><jats:p>Placeholder &amp; text.</jats:p>",
    "is-referenced-by-count": 3,
}


class Records(unittest.TestCase):
    def test_norm_doi(self):
        for s in ("https://doi.org/10.1145/ABC", "doi:10.1145/abc", " 10.1145/abc ",
                  "http://dx.doi.org/10.1145/abc"):
            self.assertEqual(find_papers.norm_doi(s), "10.1145/abc", s)
        self.assertIsNone(find_papers.norm_doi(""))

    def test_from_crossref(self):
        r = find_papers.from_crossref(RECORD)
        self.assertEqual(r["doi"], "10.1145/0000000.0000001")
        self.assertEqual(r["authors"], "Ada Example, Bo Sample, Cy Test et al.")
        self.assertEqual(r["year"], 2024)
        self.assertEqual(r["abstract"], "Placeholder & text.")
        self.assertEqual(r["cited_by"], 3)

    def test_escaped_html_abstract(self):
        self.assertEqual(find_papers.strip_jats("&lt;div&gt; Text &lt;/div&gt;"), "Text")

    def test_openalex_abstract(self):
        r = find_papers.from_openalex({"doi": "https://doi.org/10.1/X", "title": "T",
                                       "abstract_inverted_index": {"world": [1], "hello": [0]},
                                       "authorships": [{"author": {"display_name": "A B"}}]})
        self.assertEqual((r["doi"], r["abstract"], r["authors"]), ("10.1/x", "hello world", "A B"))


class Bib(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_bib_dois_and_marking(self):
        (self.dir / "refs.bib").write_text(
            "@inproceedings{a, doi = {10.1145/0000000.0000001}}\n"
            "@article{b, url = {https://doi.org/10.1/XYZ}}\n")
        known = find_papers.bib_dois(find_papers.paper_bibs(self.dir))
        self.assertEqual(known, {"10.1145/0000000.0000001", "10.1/xyz"})
        cands = [find_papers.from_crossref(RECORD), find_papers.from_crossref(RECORD),
                 {**find_papers.from_crossref(RECORD), "doi": "10.2/new"}]
        marked = find_papers.mark(cands, known, new_only=False)
        self.assertEqual([c["in_bib"] for c in marked], [True, False])  # duplicate dropped
        self.assertEqual(len(find_papers.mark(cands, known, new_only=True)), 1)

    def test_search_cli_offline(self):
        payload = json.dumps({"message": {"items": [RECORD]}}).encode()
        with mock.patch.object(find_papers, "get", return_value=payload) as get:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = find_papers.main(["search", "placeholder", "--since", "2020", "--md"])
        self.assertEqual(code, 0)
        url = get.call_args[0][0]
        self.assertIn("type%3Aproceedings-article", url)
        self.assertIn("from-pub-date%3A2020", url)
        self.assertIn("https://doi.org/10.1145/0000000.0000001", buf.getvalue())

    def test_no_service_exits_1(self):
        with mock.patch.object(find_papers, "get", side_effect=find_papers.Unavailable("down")):
            with redirect_stdout(io.StringIO()), mock.patch("sys.stderr", io.StringIO()):
                self.assertEqual(find_papers.main(["cites", "10.1/x"]), 1)


if __name__ == "__main__":
    unittest.main()
