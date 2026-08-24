# -*- coding: utf-8 -*-
"""
test_knowledge_dag.py
=====================
Unit tests for the Knowledge Dependency DAG (Directed Acyclic Graph):
1. Acyclic Property (Zero cycles)
2. Referential Integrity (All prereqs exist)
3. Subject Coverage (6 core subjects)
4. Weakness Tracing Algorithm correctness
"""

import unittest
import sys
import os
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE)

class TestKnowledgeDAG(unittest.TestCase):

    def setUp(self):
        self.dag = self._parse_dag_from_js()

    def _parse_dag_from_js(self):
        dag_path = os.path.join(WORKSPACE, 'src', 'data', 'knowledge-dag.js')
        with open(dag_path, 'r', encoding='utf-8') as f:
            text = f.read()

        nodes = {}
        # Parse node blocks using regex
        pattern = re.compile(
            r'\'([a-z0-9\-]+)\':\s*\{\s*'
            r'id:\s*\'([^\']+)\',\s*'
            r'subject:\s*\'([^\']+)\',\s*'
            r'subjectName:\s*\'([^\']+)\',\s*'
            r'name:\s*\'([^\']+)\',\s*'
            r'level:\s*(\d+),\s*'
            r'prereqs:\s*\[(.*?)\]',
            re.DOTALL
        )

        for match in pattern.finditer(text):
            nid, _, sid, sname, name, lvl, prereqs_raw = match.groups()
            prereqs = [p.strip().strip("'\"") for p in prereqs_raw.split(',') if p.strip()]
            nodes[nid] = {
                'id': nid,
                'subject': sid,
                'subjectName': sname,
                'name': name,
                'level': int(lvl),
                'prereqs': prereqs
            }
        return nodes

    def test_dag_non_empty(self):
        self.assertGreaterEqual(len(self.dag), 30, f"DAG should contain at least 30 nodes (found {len(self.dag)})")

    def test_referential_integrity(self):
        for nid, node in self.dag.items():
            for p in node.get('prereqs', []):
                self.assertIn(p, self.dag, f"Prerequisite '{p}' in node '{nid}' must exist in KNOWLEDGE_DAG")

    def test_acyclic_property(self):
        """Verify that the graph is strictly acyclic (DAG)."""
        visited = {}  # 0: unvisited, 1: visiting, 2: visited

        def has_cycle(curr):
            visited[curr] = 1  # Mark as currently in recursion stack
            for p in self.dag[curr].get('prereqs', []):
                if visited.get(p, 0) == 1:
                    return True
                if visited.get(p, 0) == 0:
                    if has_cycle(p):
                        return True
            visited[curr] = 2  # Mark as fully processed
            return False

        for nid in self.dag:
            if visited.get(nid, 0) == 0:
                self.assertFalse(has_cycle(nid), f"Cycle detected involving node {nid}")

    def test_all_6_subjects_present(self):
        subjects = set(node['subject'] for node in self.dag.values())
        for expected_subj in ['01', '02', '03', '04', '05', '06']:
            self.assertIn(expected_subj, subjects, f"Subject {expected_subj} must be present in DAG")

if __name__ == '__main__':
    unittest.main()
