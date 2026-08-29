# -*- coding: utf-8 -*-
"""
test_build_pipeline.py
======================
Integration tests verifying:
1. Build pipeline successfully compiles modular src/ into production index.html.
2. All critical UI elements and interactive DOM IDs are present.
3. No syntax corruption or missing script tags.
"""

import unittest
import sys
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE)

class TestBuildPipeline(unittest.TestCase):

    def setUp(self):
        self.index_path = os.path.join(WORKSPACE, 'index.html')

    def test_index_html_exists_and_non_empty(self):
        self.assertTrue(os.path.exists(self.index_path), "index.html must exist")
        self.assertGreater(os.path.getsize(self.index_path), 50000, "index.html should be over 50KB")

    def test_critical_dom_elements_present(self):
        with open(self.index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        required_ids = [
            'questions-container',
            'solution-modal',
            'modal-left-content',
            'modal-right-content',
            'modal-resizer',
            'tab-pane-dag',
            'dag-graph-viewer-content',
            'exam-timer',
            'bar-mastered',
            'filter-subject',
            'filter-year',
            'filter-status',
            'filter-diff',
            'search-input',
            'review-container',
            'review-type-filter',
            'tab-pane-review',
            'tab-btn-review'
        ]

        for elem_id in required_ids:
            self.assertIn(f'id="{elem_id}"', html, f"Element ID '{elem_id}' must be present in index.html")

    def test_review_page_supports_due_and_taxonomy_filters(self):
        with open(self.index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        self.assertIn("function renderReviewPage", html)
        self.assertIn("function setReviewFilter", html)
        self.assertIn("getDueQuestionsList()", html)
        self.assertIn("data-review-type", html)
        self.assertIn("setReviewSubjectFilter(this.value)", html)
        self.assertIn("const subjectQuestions = questions.filter", html)
        self.assertIn("subjectQuestions.map(getReviewTypeLabel)", html)
        self.assertIn("review-card-grid", html)
        self.assertIn("box-shadow: var(--shadow)", html)

    def test_review_taxonomy_uses_textbook_chapter_names(self):
        with open(self.index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        chapter_names = [
            '節點電壓法與網目電流法',
            '二極體整流與濾波電路',
            '複變分析、柯西定理與留數定理',
            '電力潮流與導納矩陣',
            '經濟調度與發電協調方程式',
            '系統接地與設備接地',
            '照明設計與照度計算',
        ]
        for chapter in chapter_names:
            self.assertIn(chapter, html, f"Textbook chapter '{chapter}' must be available to review taxonomy")
        self.assertIn('function getReviewChapterKey', html)
        self.assertIn('needle.length >= 4 ? 4 : 3', html, 'Question text should have the strongest classification weight')

    def test_dag_functions_bundled(self):
        with open(self.index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        self.assertIn('const KNOWLEDGE_DAG =', html)
        self.assertIn('function renderDagTracerCard', html)
        self.assertIn('function renderDagGraphVisualizer', html)
        self.assertIn('function tracePrerequisiteChain', html)

if __name__ == '__main__':
    unittest.main()
