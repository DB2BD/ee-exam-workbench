# -*- coding: utf-8 -*-
import json
import re
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]


def load_bundle_ids(path):
    text = Path(path).read_text(encoding='utf-8')
    match = re.search(r'^\s*questions\s*:\s*', text, re.MULTILINE)
    questions = json.JSONDecoder().raw_decode(text[match.end():].lstrip())[0]
    return {row[0] for row in questions}


class TestTaxonomyManifest(unittest.TestCase):
    def test_golden_set_references_existing_questions_and_chapters(self):
        manifest = json.loads((WORKSPACE / 'data/taxonomy/golden-set.json').read_text(encoding='utf-8'))
        ids = load_bundle_ids(WORKSPACE / 'dashboard-data.js')
        dag_source = (WORKSPACE / 'src/data/knowledge-dag.js').read_text(encoding='utf-8')
        chapter_ids = set(re.findall(r"'([a-z0-9]+(?:-[a-z0-9]+)+)'\s*:\s*\{", dag_source))
        missing_questions = []
        missing_chapters = []
        for case in manifest['positiveCases']:
            if case['chapterId'] not in chapter_ids:
                missing_chapters.append(case['chapterId'])
            missing_questions.extend(qid for qid in case['questionIds'] if qid not in ids)
        for case in manifest['hardNegatives']:
            if case['actualChapterId'] not in chapter_ids or case['confusableWith'] not in chapter_ids:
                missing_chapters.extend([case['actualChapterId'], case['confusableWith']])
            if case['questionId'] not in ids:
                missing_questions.append(case['questionId'])
        self.assertEqual(missing_questions, [])
        self.assertEqual(missing_chapters, [])


if __name__ == '__main__':
    unittest.main()
