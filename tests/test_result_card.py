# -*- coding: utf-8 -*-
"""WP4 結果卡: model, scoring, store + SM-2 mapping, legacy migration, backup, view-model."""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    "src/data/questionPoints.generated.js",
    "src/data/targetAllocation.generated.js",
    "src/domain/studyPlan.js",
    "src/state/sm2Store.js",
    "src/state/resultCardStore.js",
    "src/components/resultCard.js",
]
KEY = "EE_EXAM_RESULT_CARD_V1"
PRACTICE_KEY = "EE_EXAM_DAILY_PRACTICE_V1"


def run_node(expression, storage=None):
    sources = "\n".join((ROOT / s).read_text(encoding="utf-8") for s in SOURCES)
    script = f"""
const vm = require('vm');
const data = {json.dumps(storage or {}, ensure_ascii=False)};
const localStorage = {{
  getItem: k => Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null,
  setItem: (k, v) => {{ data[k] = String(v); }},
  removeItem: k => {{ delete data[k]; }},
}};
const context = {{ console, localStorage }};
vm.createContext(context);
vm.runInContext({json.dumps(sources + chr(10) + 'globalThis.__result = (' + expression + ');', ensure_ascii=False)}, context);
process.stdout.write(JSON.stringify({{result: context.__result, storage: data}}));
"""
    done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def parts(*marks):
    return [{"label": "整題", "points": 20, "mark": m} for m in marks]


class TestModelAndScoring(unittest.TestCase):
    def test_multi_part_model(self):
        model = run_node("buildResultModel('EE-114-03-5')")["result"]
        self.assertEqual(model["total"], 30)
        self.assertEqual([p["points"] for p in model["parts"]], [20, 10])
        self.assertEqual(len(model["parts"]), 2)

    def test_whole_only_model(self):
        model = run_node("buildResultModel('EE-114-01-2')")["result"]
        self.assertEqual(model["total"], 20)
        self.assertEqual(model["parts"], [{"label": "整題", "points": 20}])

    def test_main_vs_basic_scoring(self):
        out = run_node("""({
          main: scoreResult({tier:'main', total:20, parts:[{label:'整題', points:20}]}, ['o']),
          basic: scoreResult({tier:'basic', total:20, parts:[{label:'整題', points:20}]}, ['o']),
          basicTri: scoreResult({tier:'basic', total:20, parts:[{label:'整題', points:20}]}, ['tri']),
          mixed: scoreResult({tier:'main', total:30, parts:[{label:'a', points:20},{label:'b', points:10}]}, ['o','tri']),
          partial: scoreResult({tier:'main', total:30, parts:[{label:'a', points:20},{label:'b', points:10}]}, ['o', null]),
        })""")["result"]
        self.assertEqual(out["main"]["estimate"], 20)
        self.assertEqual(out["basic"]["estimate"], 10)
        self.assertEqual(out["basicTri"]["estimate"], 5)
        self.assertEqual(out["mixed"]["estimate"], 25)
        self.assertTrue(out["mixed"]["complete"])
        self.assertFalse(out["partial"]["complete"])

    def test_sm2_rating_mapping(self):
        out = run_node("[resultCardSM2Rating(['o','o']), resultCardSM2Rating(['o','tri']), resultCardSM2Rating(['tri','x','o']), resultCardSM2Rating([])]")["result"]
        self.assertEqual(out, [5, 3, 1, None])


class TestStore(unittest.TestCase):
    def test_save_updates_sm2_and_reads_back(self):
        expr = """(() => {
          const r = saveResultRecord({qid:'EE-114-03-5', source:'random', at: 1700000000000,
            parts:[{label:'（一）', points:20, mark:'o'},{label:'（二）', points:10, mark:'x'}], errors:['C','Z','C'], note:'n'});
          return {r, latest: latestRecordFor('EE-114-03-5'), all: getResultRecords({source:'random'}), sm2: sm2Schedule['EE-114-03-5']};
        })()"""
        out = run_node(expr)
        res = out["result"]
        self.assertTrue(res["r"]["ok"])
        rec = res["latest"]
        self.assertEqual(rec["errors"], ["C"])
        self.assertEqual(rec["total"], 30)
        self.assertEqual(rec["tier"], "basic")  # EE-114-03-5 is a 基本分 question
        self.assertEqual(rec["estimate"], 10)  # 20*0.5 + 10*0
        self.assertEqual(rec["source"], "random")
        self.assertEqual(len(res["all"]), 1)
        self.assertEqual(res["sm2"]["interval"], 1)
        self.assertEqual(res["sm2"]["repetitions"], 0)  # x -> 忘記 (rating 1)
        stored = json.loads(out["storage"][KEY])
        self.assertEqual(stored["version"], 1)
        self.assertTrue(any("SM2" in k for k in out["storage"]))

    def test_all_correct_gets_independent_recall(self):
        out = run_node("""(() => { saveResultRecord({qid:'EE-114-01-2', source:'review', parts:[{label:'整題', points:20, mark:'o'}]});
          return sm2Schedule['EE-114-01-2']; })()""")["result"]
        self.assertEqual(out["repetitions"], 1)
        self.assertGreater(out["easeFactor"], 2.5)

    def test_tri_gets_hint_rating(self):
        out = run_node("""(() => { saveResultRecord({qid:'EE-114-01-2', source:'review', parts:[{label:'整題', points:20, mark:'tri'}]});
          return sm2Schedule['EE-114-01-2']; })()""")["result"]
        self.assertEqual(out["repetitions"], 1)
        self.assertLess(out["easeFactor"], 2.5)

    def test_invalid_record_rejected(self):
        out = run_node("[saveResultRecord({qid:'', parts:[]}).ok, saveResultRecord({qid:'EE-114-01-2', parts:[{label:'a',points:1,mark:'?'}]}).error]")["result"]
        self.assertEqual(out, [False, "invalid_record"])

    def test_malformed_storage_is_not_overwritten(self):
        for raw in ["{not json", json.dumps({"version": 2, "records": []}), json.dumps({"version": 1, "records": [{"id": 1}]}), json.dumps([])]:
            out = run_node("""(() => ({ save: saveResultRecord({qid:'EE-114-01-2', parts:[{label:'整題', points:20, mark:'o'}]}),
              list: getResultRecords({}) }))()""", storage={KEY: raw})
            self.assertFalse(out["result"]["save"]["ok"])
            self.assertEqual(out["result"]["list"], [])
            self.assertEqual(out["storage"][KEY], raw)

    def test_storage_throwing_is_safe(self):
        sources = "\n".join((ROOT / s).read_text(encoding="utf-8") for s in SOURCES)
        script = f"""
const vm = require('vm');
const localStorage = {{ getItem: () => {{ throw new Error('blocked'); }}, setItem: () => {{ throw new Error('blocked'); }}, removeItem: () => {{}} }};
const context = {{ console: {{ log() {{}}, error() {{}} }}, localStorage }};
vm.createContext(context);
vm.runInContext({json.dumps(sources + chr(10) + "globalThis.__r = [saveResultRecord({qid:'EE-114-01-2', parts:[{label:'整題', points:20, mark:'o'}]}).ok, getResultRecords({}).length, latestRecordFor('x')];")}, context);
process.stdout.write(JSON.stringify(context.__r));
"""
        done = subprocess.run(["node", "-"], input=script, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout), [False, 0, None])


class TestMigration(unittest.TestCase):
    PRACTICE = json.dumps({
        "version": 1,
        "completionByQuestion": {
            "EE-114-03-5": {"completedAt": 1700000000000, "rating": 5, "errorType": None},
            "EE-114-01-2": {"completedAt": 1700000100000, "rating": 3, "errorType": "計算錯"},
            "EE-114-01-3": {"completedAt": 1700000200000, "rating": 1, "errorType": None},
            "EE-114-01-1": 1700000300000,
        },
        "activeSession": None,
    })

    def test_migration_idempotent_and_originals_untouched(self):
        storage = {PRACTICE_KEY: self.PRACTICE}
        out = run_node("""(() => {
          const first = migrateLegacyResultRecords();
          const second = migrateLegacyResultRecords();
          const list = getResultRecords({});
          return {first, second, list};
        })()""", storage=storage)
        res = out["result"]
        self.assertEqual(res["first"]["migrated"], 3)
        self.assertTrue(res["second"]["already"])
        self.assertEqual(len(res["list"]), 3)
        by_qid = {r["qid"]: r for r in res["list"]}
        self.assertEqual(by_qid["EE-114-03-5"]["parts"][0]["mark"], "o")
        self.assertEqual(by_qid["EE-114-01-2"]["parts"][0]["mark"], "tri")
        self.assertEqual(by_qid["EE-114-01-2"]["errors"], ["C"])
        self.assertEqual(by_qid["EE-114-01-3"]["parts"][0]["mark"], "x")
        for r in res["list"]:
            self.assertTrue(r["legacy"])
            self.assertEqual(r["source"], "legacy")
        self.assertEqual(out["storage"][PRACTICE_KEY], self.PRACTICE)
        self.assertTrue(json.loads(out["storage"][KEY])["migrated"])
        # legacy records do not touch SM-2
        sm2_keys = [k for k in out["storage"] if "SM2" in k]
        self.assertEqual(sm2_keys, [])

    def test_save_triggers_migration_once(self):
        out = run_node("""(() => { saveResultRecord({qid:'EE-114-01-2', source:'today', parts:[{label:'整題', points:20, mark:'o'}]});
          saveResultRecord({qid:'EE-114-01-2', source:'today', parts:[{label:'整題', points:20, mark:'x'}]});
          return getResultRecords({}).map(r => r.source); })()""", storage={PRACTICE_KEY: self.PRACTICE})["result"]
        self.assertEqual(out.count("legacy"), 3)
        self.assertEqual(out.count("today"), 2)

    def test_malformed_practice_store_yields_nothing(self):
        out = run_node("(() => ({m: migrateLegacyResultRecords(), n: getResultRecords({}).length}))()",
                       storage={PRACTICE_KEY: "{oops"})["result"]
        self.assertEqual(out["n"], 0)
        self.assertTrue(out["m"]["ok"])


class TestBackup(unittest.TestCase):
    def test_snapshot_includes_key_and_merge_unions_by_id(self):
        rec = lambda i, q: {"id": i, "qid": q, "at": 1, "source": "today", "tier": "main", "parts": parts("o"), "errors": [], "note": "", "total": 20, "estimate": 20}
        local = {"version": 1, "records": [rec("a", "EE-114-01-2")]}
        incoming = {"version": 1, "records": [rec("a", "EE-114-01-2"), rec("b", "EE-114-01-3")]}
        out = run_node("""(() => {
          const snap = buildUserBackupSnapshot();
          const merged = backupMergeResultCard(%s, %s);
          const errs = [];
          backupValidateResultCard({version:1, records:[{id:'x'}]}, errs);
          return {snapKeys: Object.keys(snap), snapRecords: snap.resultCard.records.length, ids: merged.records.map(r => r.id), errs: errs.length};
        })()""" % (json.dumps(local), json.dumps(incoming)), storage={KEY: json.dumps(local)})["result"]
        self.assertIn("resultCard", out["snapKeys"])
        self.assertEqual(out["snapRecords"], 1)
        self.assertEqual(out["ids"], ["a", "b"])
        self.assertGreater(out["errs"], 0)

    def test_source_wires_restore_and_rollback(self):
        text = (ROOT / "src/state/sm2Store.js").read_text(encoding="utf-8")
        self.assertIn("EE_EXAM_RESULT_CARD_V1", text)
        self.assertIn("[BACKUP_RESULT_CARD_KEY, JSON.stringify(nextResultCard)]", text)
        self.assertRegex(text, r"BACKUP_TODAY_TASK_KEY, BACKUP_RESULT_CARD_KEY, BACKUP_MOCK_EXAM_TIMER_KEY")

    def test_correction_seen_roundtrip_and_merge_keeps_latest(self):
        seen = "EE_EXAM_ANSWER_CORRECTION_SEEN_V1"
        out = run_node("""(() => {
          const snap = JSON.parse(JSON.stringify(buildUserBackupSnapshot()));
          const exported = snap.answerCorrectionSeen;
          snap.answerCorrectionSeen = {'EE-112-01-2': 50, 'EE-113-02-1': 7, bad: 'x'};
          const applied = applyUserDataBackup(snap, 'merge');
          return {exported, ok: applied.success, error: applied.error || null, stored: JSON.parse(localStorage.getItem('%s'))};
        })()""" % seen, storage={seen: json.dumps({"EE-112-01-2": 9, "EE-113-02-1": 99})})["result"]
        self.assertEqual(out["exported"], {"EE-112-01-2": 9, "EE-113-02-1": 99})
        self.assertTrue(out["ok"], out["error"])
        self.assertEqual(out["stored"], {"EE-112-01-2": 50, "EE-113-02-1": 99})

    def test_restore_roundtrip_merge(self):
        rec = {"id": "b", "qid": "EE-114-01-3", "at": 5, "source": "today", "tier": "main", "parts": parts("x"), "errors": [], "note": "", "total": 20, "estimate": 0}
        old = {"id": "a", "qid": "EE-114-01-2", "at": 1, "source": "today", "tier": "main", "parts": parts("o"), "errors": [], "note": "", "total": 20, "estimate": 20}
        out = run_node("""(() => {
          const payload = JSON.parse(JSON.stringify(buildUserBackupSnapshot()));
          payload.resultCard = {version: 1, records: [%s]};
          const applied = applyUserDataBackup(payload, 'merge');
          return {ok: applied.success, error: applied.error || null, ids: JSON.parse(localStorage.getItem('%s')).records.map(r => r.id)};
        })()""" % (json.dumps(rec), KEY), storage={KEY: json.dumps({"version": 1, "records": [old]})})["result"]
        self.assertTrue(out["ok"], out["error"])
        self.assertEqual(sorted(out["ids"]), ["a", "b"])


class TestViewModel(unittest.TestCase):
    def test_header_rows_and_chips(self):
        out = run_node("""({
          fresh: resultCardViewModel('EE-114-03-5', [], []),
          ok: resultCardViewModel('EE-114-03-5', ['o','o'], ['C']),
          tri: resultCardViewModel('EE-114-03-5', ['o','tri'], ['C']),
          done: resultCardViewModel('EE-114-03-5', ['o','x'], []),
        })""")["result"]
        self.assertTrue(out["fresh"]["header"].startswith("EE-114-03-5"))
        self.assertEqual([r["pointsText"] for r in out["fresh"]["rows"]], ["20 分", "10 分"])
        self.assertFalse(out["fresh"]["canSave"])
        self.assertEqual(out["fresh"]["errorChips"], [])
        self.assertEqual(out["ok"]["errorChips"], [])
        self.assertEqual(out["ok"]["estimateText"], "估計 15／30 分")
        self.assertTrue(out["ok"]["canSave"])
        self.assertEqual([c["code"] for c in out["tri"]["errorChips"]], list("RSFCKUT"))
        self.assertTrue(next(c for c in out["tri"]["errorChips"] if c["code"] == "C")["selected"])
        self.assertEqual(out["tri"]["estimateText"], "估計 12.5／30 分")
        self.assertEqual(out["done"]["estimateText"], "估計 10／30 分")

    def test_basic_header_hint(self):
        basic_qid = run_node("Object.keys(TARGET_ALLOCATION.questionTiers).find(q => TARGET_ALLOCATION.questionTiers[q].tier === 'basic')")["result"]
        out = run_node(f"resultCardViewModel('{basic_qid}', ['o'], [])")["result"]
        self.assertEqual(out["tierLabel"], "基本分")
        self.assertEqual(out["hint"], "○＝骨架寫完")
        self.assertTrue(out["header"].endswith("基本分"))
        self.assertEqual(out["estimate"], out["total"] / 2 if len(out["rows"]) == 1 else out["estimate"])

    def test_mock_source_wording(self):
        basic_qid = run_node("Object.keys(TARGET_ALLOCATION.questionTiers).find(q => TARGET_ALLOCATION.questionTiers[q].tier === 'basic')")["result"]
        out = run_node(f"({{mock: resultCardViewModel('{basic_qid}', ['o'], [], 'mock'), today: resultCardViewModel('{basic_qid}', ['o'], [], 'today')}})")["result"]
        o = lambda vm: next(b for b in vm["markButtons"] if b["mark"] == "o")["text"]
        self.assertEqual(o(out["mock"]), "全對")
        self.assertNotIn("骨架寫完", out["mock"]["hint"])
        self.assertEqual(o(out["today"]), "骨架寫完")
        self.assertEqual(out["today"]["hint"], "○＝骨架寫完")

    def test_text_escaped(self):
        out = run_node("""[resultCardEscape('<img src=x onerror=alert(1)>&"\\''), (() => {
          const vm = resultCardViewModel('<b>x</b>', ['o'], []); return vm.header; })()]""")["result"]
        self.assertNotIn("<", out[0])
        self.assertIn("&lt;img", out[0])
        # the DOM builder escapes via resultCardEscape and uses textContent for the header
        src = (ROOT / "src/components/resultCard.js").read_text(encoding="utf-8")
        self.assertIn("textContent = vm.header", src)
        self.assertNotIn("autofocus", src)
        self.assertNotIn(".focus()", src)



class TestDockedCollapse(unittest.TestCase):
    def test_docked_card_starts_collapsed_inline_card_does_not(self):
        src = (ROOT / "src/components/resultCard.js").read_text(encoding="utf-8")
        self.assertIn("function resultCardStartsCollapsed", src)
        out = subprocess.run(["node", "-"], input=src + "\nprocess.stdout.write(JSON.stringify([resultCardStartsCollapsed({}), resultCardStartsCollapsed({expanded:true}), resultCardStartsCollapsed({mount:{}})]));", capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout), [True, False, False])
        self.assertIn("做完了？記錄作答結果", src)


if __name__ == "__main__":
    unittest.main()
