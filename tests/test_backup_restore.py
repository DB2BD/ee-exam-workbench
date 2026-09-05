# -*- coding: utf-8 -*-
"""Behavioral tests for atomic cross-category backup and restore seams."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestBackupRestore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = r'''
const fs = require('fs'), vm = require('vm');
const storageData = {};
const localStorage = {
  getItem: key => Object.prototype.hasOwnProperty.call(storageData, key) ? storageData[key] : null,
  setItem: (key, value) => { storageData[key] = String(value); },
  removeItem: key => { delete storageData[key]; },
};
const ctx = {
  console, localStorage, currentExamCategory: 'PE', progressState: {}, starredState: {}, recallState: {},
  getManualTopicLabels: () => ({}),
};
vm.createContext(ctx);
for (const file of [
  'dashboard-data.js',
  'national-exams-data.js',
  'src/data/knowledge-dag.js',
  'src/state/sm2Store.js',
]) {
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
}
const result = vm.runInContext(process.argv[1], ctx);
process.stdout.write(JSON.stringify(result));
'''

    def run_js(self, expression):
        completed = subprocess.run(
            ["node", "-e", self.script, expression],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout.splitlines()[-1])

    def options(self):
        return {
            "questionIdsByCategory": {"PE": ["EE-pe", "EE-pe-2"], "GK": ["GK-gk"]},
            "recordsByCategory": {
                "PE": [
                    ["EE-pe", "01", 114, 1, "題目", [], "solution", "official", 3, "verified", [], False],
                    ["EE-pe-2", "02", 113, 1, "題目", [], "solution", "official", 3, "verified", [], False],
                ],
                "GK": [["GK-gk", "01", 114, 1, "題目", [], "solution", "official", 3, "pending", [], False]],
            },
        }

    def payload(self):
        return {
            "schema": "ee-exam-user-backup",
            "version": "2.0.0",
            "progressByCategory": {"PE": {"EE-pe": 1}, "GK": {"GK-gk": 2}},
            "starredByCategory": {"PE": {"EE-pe": True}, "GK": {"GK-gk": False}},
            "sm2Schedule": {"EE-pe": {"repetitions": 1, "interval": 4, "easeFactor": 2.7, "lastReviewed": "2026-09-01", "nextReviewDate": "2026-09-05"}},
            "recallState": {"EE-pe": {"level": 2, "streak": 1, "attempts": 2, "lastAchieved": 2, "lastErrorType": "公式忘記", "lastReviewed": "2026-09-01"}},
            "manualTopicLabels": {"EE-pe": {"chapterId": "ct-ohm-kcl-kvl", "source": "user", "updatedAt": "2026-09-01T00:00:00.000Z"}},
        }

    def test_export_contains_both_categories_and_shared_learning_state(self):
        result = self.run_js(
            "(() => { progressState={ 'EE-pe':1 }; starredState={ 'EE-pe':true }; "
            "localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1})); "
            "localStorage.setItem('GK_EXAM_PROGRESS_V1', JSON.stringify({'GK-gk':2})); "
            "localStorage.setItem('EE_EXAM_STARRED_V1', JSON.stringify({'EE-pe':true})); "
            "localStorage.setItem('GK_EXAM_STARRED_V1', JSON.stringify({'GK-gk':false})); "
            "sm2Schedule={'EE-pe':{repetitions:1,interval:4,easeFactor:2.7,lastReviewed:'2026-09-01',nextReviewDate:'2026-09-05'}}; "
            "recallState={'EE-pe':{level:2,streak:1,attempts:2,lastAchieved:2,lastErrorType:'公式忘記',lastReviewed:'2026-09-01'}}; "
            "getManualTopicLabels=()=>({'EE-pe':{chapterId:'ct-ohm-kcl-kvl',source:'user'}}); "
            "const data=JSON.parse(exportAllUserDataJSON()); return {version:data.version, pe:data.progressByCategory.PE, gk:data.progressByCategory.GK, starred:data.starredByCategory, schedule:Object.keys(data.sm2Schedule), recall:Object.keys(data.recallState), labels:Object.keys(data.manualTopicLabels), legacy:data.progressState}; })()"
        )
        self.assertEqual(result["version"], "2.0.0")
        self.assertEqual(result["pe"], {"EE-pe": 1})
        self.assertEqual(result["gk"], {"GK-gk": 2})
        self.assertEqual(result["starred"]["PE"], {"EE-pe": True})
        self.assertEqual(result["starred"]["GK"], {"GK-gk": False})
        self.assertEqual(result["schedule"], ["EE-pe"])
        self.assertEqual(result["recall"], ["EE-pe"])
        self.assertEqual(result["labels"], ["EE-pe"])
        self.assertEqual(result["legacy"], {"EE-pe": 1})

    def test_invalid_backup_is_rejected_before_any_storage_or_memory_change(self):
        payload = self.payload()
        options = self.options()
        expression = (
            "(() => { const options = " + json.dumps(options, ensure_ascii=False) + "; "
            "const base = " + json.dumps(payload, ensure_ascii=False) + "; "
            "localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1})); progressState={'EE-pe':1}; "
            "const before=localStorage.getItem('EE_EXAM_PROGRESS_V1'); const cases=[]; "
            "for (const [name, mutate] of Object.entries({version:d=>d.version='9.9.9', qid:d=>d.progressByCategory.PE['EE-unknown']=1, status:d=>d.progressByCategory.PE['EE-pe']=9, starred:d=>d.starredByCategory.PE['EE-pe']='yes', sm2:d=>d.sm2Schedule['EE-pe'].easeFactor=9, recall:d=>d.recallState['EE-pe'].level=9, manual:d=>d.manualTopicLabels['EE-pe'].chapterId='el-ohm-law'})) { const bad=JSON.parse(JSON.stringify(base)); mutate(bad); const res=validateUserDataBackup(bad, options); cases.push({name,success:res.success,storage:localStorage.getItem('EE_EXAM_PROGRESS_V1'),memory:progressState['EE-pe']}); } "
            "return {before, cases}; })()"
        )
        result = self.run_js(expression)
        self.assertEqual(result["before"], json.dumps({"EE-pe": 1}, separators=(",", ":")))
        self.assertTrue(all(not case["success"] and case["storage"] == result["before"] and case["memory"] == 1 for case in result["cases"]))

    def test_merge_and_replace_have_explicit_non_destructive_semantics(self):
        payload = self.payload()
        options = self.options()
        expression = (
            "(() => { const options = " + json.dumps(options, ensure_ascii=False) + "; const payload=" + json.dumps(payload, ensure_ascii=False) + "; "
            "localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1,'EE-pe-2':2})); localStorage.setItem('GK_EXAM_PROGRESS_V1', JSON.stringify({'GK-gk':1})); "
            "let merge=applyUserDataBackup(payload, 'merge', options); const merged={pe:JSON.parse(localStorage.getItem('EE_EXAM_PROGRESS_V1')),gk:JSON.parse(localStorage.getItem('GK_EXAM_PROGRESS_V1')),count:merge.summary.progress}; "
            "localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1,'EE-pe-2':2})); localStorage.setItem('GK_EXAM_PROGRESS_V1', JSON.stringify({'GK-gk':1})); "
            "let replace=applyUserDataBackup(payload, 'replace', options); const replaced={pe:JSON.parse(localStorage.getItem('EE_EXAM_PROGRESS_V1')),gk:JSON.parse(localStorage.getItem('GK_EXAM_PROGRESS_V1')),count:replace.summary.progress}; return {merged,replaced}; })()"
        )
        result = self.run_js(expression)
        self.assertEqual(result["merged"]["pe"], {"EE-pe": 1, "EE-pe-2": 2})
        self.assertEqual(result["merged"]["gk"], {"GK-gk": 2})
        self.assertEqual(result["replaced"]["pe"], {"EE-pe": 1})
        self.assertEqual(result["replaced"]["gk"], {"GK-gk": 2})
        self.assertEqual(result["merged"]["count"], 3)
        self.assertEqual(result["replaced"]["count"], 2)

    def test_storage_write_failure_rolls_back_every_key_and_memory(self):
        payload = self.payload()
        options = self.options()
        expression = (
            "(() => { const options = " + json.dumps(options, ensure_ascii=False) + "; const payload=" + json.dumps(payload, ensure_ascii=False) + "; "
            "localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1})); localStorage.setItem('GK_EXAM_PROGRESS_V1', JSON.stringify({'GK-gk':1})); "
            "localStorage.setItem('EE_EXAM_STARRED_V1', JSON.stringify({'EE-pe':false})); progressState={'EE-pe':1}; const before={}; "
            "for (const key of ['EE_EXAM_PROGRESS_V1','GK_EXAM_PROGRESS_V1','EE_EXAM_STARRED_V1','GK_EXAM_STARRED_V1','EE_EXAM_SM2_SCHEDULE_V1','EE_EXAM_RECALL_V1','EE_MANUAL_TOPIC_LABELS_V1','EE_EXAM_BACKUP_META_V1']) before[key]=localStorage.getItem(key); "
            "const original=localStorage.setItem; localStorage.setItem=(key,value)=>{ if(key==='EE_EXAM_RECALL_V1') throw new Error('simulated'); original(key,value); }; "
            "const result=applyUserDataBackup(payload, 'replace', options); const after={}; "
            "for (const key of Object.keys(before)) after[key]=localStorage.getItem(key); return {success:result.success,before,after,memory:progressState['EE-pe']}; })()"
        )
        result = self.run_js(expression)
        self.assertFalse(result["success"])
        self.assertEqual(result["before"], result["after"])
        self.assertEqual(result["memory"], 1)

    def test_metadata_write_failure_rolls_back_learning_writes(self):
        payload = self.payload()
        options = self.options()
        expression = (
            "(() => { const options = " + json.dumps(options, ensure_ascii=False) + "; const payload=" + json.dumps(payload, ensure_ascii=False) + "; "
            "localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1})); progressState={'EE-pe':1}; const before=localStorage.getItem('EE_EXAM_PROGRESS_V1'); "
            "const original=localStorage.setItem; localStorage.setItem=(key,value)=>{ if(key==='EE_EXAM_BACKUP_META_V1') throw new Error('metadata failure'); original(key,value); }; "
            "const result=applyUserDataBackup(payload,'replace',options); return {success:result.success,storage:localStorage.getItem('EE_EXAM_PROGRESS_V1'),memory:progressState['EE-pe']}; })()"
        )
        result = self.run_js(expression)
        self.assertFalse(result["success"])
        self.assertEqual(result["storage"], json.dumps({"EE-pe": 1}, separators=(",", ":")))
        self.assertEqual(result["memory"], 1)

    def test_v2_replace_requires_a_complete_category_snapshot(self):
        payload = self.payload()
        options = self.options()
        expression = (
            "(() => { const options = " + json.dumps(options, ensure_ascii=False) + "; const payload=" + json.dumps(payload, ensure_ascii=False) + "; "
            "delete payload.progressByCategory.GK; localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1})); const before=localStorage.getItem('EE_EXAM_PROGRESS_V1'); "
            "const result=applyUserDataBackup(payload,'replace',options); return {success:result.success,storage:localStorage.getItem('EE_EXAM_PROGRESS_V1'),memory:progressState}; })()"
        )
        result = self.run_js(expression)
        self.assertFalse(result["success"])
        self.assertEqual(result["storage"], json.dumps({"EE-pe": 1}, separators=(",", ":")))
        self.assertEqual(result["memory"], {})

    def test_v2_merge_allows_a_partial_category_snapshot(self):
        payload = self.payload()
        options = self.options()
        expression = (
            "(() => { const options = " + json.dumps(options, ensure_ascii=False) + "; const payload=" + json.dumps(payload, ensure_ascii=False) + "; "
            "delete payload.progressByCategory.GK; delete payload.starredByCategory.GK; "
            "localStorage.setItem('GK_EXAM_PROGRESS_V1', JSON.stringify({'GK-gk':1})); "
            "const result=applyUserDataBackup(payload,'merge',options); return {success:result.success,gk:JSON.parse(localStorage.getItem('GK_EXAM_PROGRESS_V1'))}; })()"
        )
        result = self.run_js(expression)
        self.assertTrue(result["success"])
        self.assertEqual(result["gk"], {"GK-gk": 1})

    def test_legacy_replace_updates_current_category_and_preserves_other_category(self):
        options = self.options()
        legacy = {
            "version": "1.0.0",
            "progressState": {"EE-pe": 2},
            "starredState": {"EE-pe": True},
            "sm2Schedule": {},
            "recallState": {},
            "manualTopicLabels": {},
        }
        expression = (
            "(() => { const options = " + json.dumps(options, ensure_ascii=False) + "; const payload=" + json.dumps(legacy, ensure_ascii=False) + "; "
            "localStorage.setItem('EE_EXAM_PROGRESS_V1', JSON.stringify({'EE-pe':1,'EE-pe-2':2})); localStorage.setItem('GK_EXAM_PROGRESS_V1', JSON.stringify({'GK-gk':1})); "
            "const result=applyUserDataBackup(payload,'replace',options); return {success:result.success,pe:JSON.parse(localStorage.getItem('EE_EXAM_PROGRESS_V1')),gk:JSON.parse(localStorage.getItem('GK_EXAM_PROGRESS_V1'))}; })()"
        )
        result = self.run_js(expression)
        self.assertTrue(result["success"])
        self.assertEqual(result["pe"], {"EE-pe": 2})
        self.assertEqual(result["gk"], {"GK-gk": 1})


if __name__ == "__main__":
    unittest.main()
