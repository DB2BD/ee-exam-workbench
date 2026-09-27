"""Ensure canonical solution links in the generated review index resolve."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "reports" / "manual-review-index.md"
QID_LINK_RE = re.compile(
    r"\[(?P<qid>(?:EE|GK)-[A-Za-z0-9-]+)\]\((?P<url>[^)]+)\)"
)


class TestManualReviewIndexLinks(unittest.TestCase):
    def test_every_markdown_solution_link_resolves_to_an_existing_file(self):
        text = INDEX.read_text(encoding="utf-8")
        rows = [
            line for line in text.splitlines()
            if re.match(r"^\| (?:EE|GK)-[A-Za-z0-9-]+ \|", line)
        ]
        links = list(QID_LINK_RE.finditer(text))
        row_qids = {line.split("|", 2)[1].strip() for line in rows}
        link_qids = [match.group("qid") for match in links]

        self.assertTrue(rows, "manual review index contains no question rows")
        self.assertEqual(set(link_qids), row_qids)
        self.assertEqual(len(link_qids), len(row_qids))
        self.assertIn("%20", " ".join(match.group("url") for match in links))

        for match in links:
            qid = match.group("qid")
            url = match.group("url")
            with self.subTest(qid=qid, url=url):
                self.assertNotIn(" ", url, "spaces in Markdown URLs must be encoded")
                self.assertNotRegex(url, r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
                target = unquote(url.split("#", 1)[0])
                resolved = (INDEX.parent / target).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT.resolve()), resolved)
                self.assertTrue(resolved.is_file(), resolved)
                self.assertEqual(resolved.suffix, ".md")
                self.assertEqual(resolved.stem, qid)


if __name__ == "__main__":
    unittest.main()
