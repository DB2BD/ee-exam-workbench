"""Regression coverage for retired GK writers, exercised only in fixtures."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEGACY_SCRIPTS = (
    "scripts/generate_all_national_exams.py",
    "scripts/generate_all_national_exam_solutions.py",
    "scripts/generate_all_national_exam_pdfs_v2.py",
    "scripts/build_all_authentic_gk_solutions.py",
    "scripts/generate_flagship_gk_diagrams_and_solutions.py",
)

PROBE = textwrap.dedent(
    r"""
    import builtins
    import importlib.util
    import io
    import json
    import os
    from pathlib import Path
    import runpy
    import sys

    target = Path(sys.argv[1]).resolve()
    mode = sys.argv[2]
    args = sys.argv[3:]
    scripts_dir = target.parents[1] if target.parent.name == "legacy_migrations" else target.parent
    sys.path.insert(0, str(scripts_dir))
    sys.dont_write_bytecode = True
    writes = []
    side_effects = []

    def deny_write(operation, path):
        try:
            rendered = os.fspath(path)
        except TypeError:
            rendered = repr(path)
        writes.append({"operation": operation, "path": rendered})
        raise PermissionError("fixture write guard intercepted " + operation + ": " + rendered)

    original_open = builtins.open
    def guarded_open(file, mode="r", *positional, **keywords):
        if any(flag in mode for flag in ("w", "a", "x", "+")):
            deny_write("open(" + mode + ")", file)
        return original_open(file, mode, *positional, **keywords)
    builtins.open = guarded_open

    original_io_open = io.open
    def guarded_io_open(file, mode="r", *positional, **keywords):
        if any(flag in mode for flag in ("w", "a", "x", "+")):
            deny_write("io.open(" + str(mode) + ")", file)
        return original_io_open(file, mode, *positional, **keywords)
    io.open = guarded_io_open

    original_os_open = os.open
    def guarded_os_open(path, flags, *positional, **keywords):
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        if flags & write_flags:
            deny_write("os.open", path)
        return original_os_open(path, flags, *positional, **keywords)
    os.open = guarded_os_open

    def guarded_mkdir(path, *args, **kwargs):
        deny_write("mkdir", path)
    os.mkdir = guarded_mkdir
    os.makedirs = lambda path, *args, **kwargs: deny_write("makedirs", path)
    pathlib_mkdir = Path.mkdir
    def guarded_path_mkdir(self, *args, **kwargs):
        deny_write("Path.mkdir", self)
    Path.mkdir = guarded_path_mkdir
    Path.write_text = lambda self, *args, **kwargs: deny_write("Path.write_text", self)
    Path.write_bytes = lambda self, *args, **kwargs: deny_write("Path.write_bytes", self)

    original_chdir = os.chdir
    def guarded_chdir(path):
        side_effects.append({"operation": "chdir", "path": os.fspath(path)})
        raise PermissionError("fixture import guard intercepted chdir")
    os.chdir = guarded_chdir

    exception = None
    try:
        if mode == "import":
            name = "legacy_probe_" + target.stem
            spec = importlib.util.spec_from_file_location(name, target)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            if target.name == "generate_all_national_exams.py":
                assert hasattr(module, "EXAM_DATA") and hasattr(module, "SUBJECT_DIRS")
                assert module.EXAM_DATA == {}, "withdrawn synthetic exam text remains importable"
        else:
            sys.argv = [str(target), *args]
            runpy.run_path(str(target), run_name="__main__")
    except BaseException as error:
        exception = {
            "type": type(error).__name__,
            "message": str(error),
            "code": getattr(error, "code", None),
        }
    print("PROBE_RESULT=" + json.dumps({
        "exception": exception,
        "writes": writes,
        "side_effects": side_effects,
    }, ensure_ascii=False))
    """
)


class LegacyGKGeneratorsSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="legacy-gk-writers-")
        cls.fixture = Path(cls.temp_dir.name) / "fixture"
        cls.fixture.mkdir()
        for relative in LEGACY_SCRIPTS:
            source = ROOT / relative
            destination = cls.fixture / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        exam_dir = (
            cls.fixture
            / "04_國考同級題庫"
            / "04_電機機械"
        )
        solution_dir = (
            cls.fixture
            / "02_題解/國考同級題解"
            / "04_電機機械"
        )
        exam_dir.mkdir(parents=True)
        solution_dir.mkdir(parents=True)
        cls.sentinels = {
            exam_dir / "GK_114年_電機機械.md": b"official exam sentinel\x00\xff",
            exam_dir / "GK_114年_高考三級_電機機械.pdf": b"official pdf sentinel\x00\xff",
            solution_dir / "GK_114年_電機機械_全卷完整詳細題解.md": b"official solution sentinel\x00\xff",
        }
        for path, payload in cls.sentinels.items():
            path.write_bytes(payload)
        cls.initial_snapshot = cls._snapshot_fixture_sources()

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    @classmethod
    def _snapshot_fixture_sources(cls):
        protected_roots = (
            cls.fixture / "01_原始試題/依考科",
            cls.fixture / "02_題解/技師題解",
        )
        snapshot = {}
        for root in protected_roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file():
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    snapshot[str(path.relative_to(cls.fixture))] = digest
        return snapshot

    def _probe(self, relative, mode):
        target = self.fixture / relative
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        # Exercise every known force path in the legacy family, not just the
        # default invocation that may already stop before reaching a writer.
        environment["EE_EXAM_ALLOW_SYNTHETIC"] = "1"
        command = [sys.executable, "-c", PROBE, str(target), mode]
        if mode == "direct":
            command.extend(("--force", "--override", "--allow-synthetic", "--yes"))
        completed = subprocess.run(
            command,
            cwd=self.fixture,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        marker = next(
            (line[len("PROBE_RESULT=") :] for line in completed.stdout.splitlines()
             if line.startswith("PROBE_RESULT=")),
            None,
        )
        self.assertIsNotNone(
            marker,
            f"probe did not report its result for {relative}:\n"
            f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        result = json.loads(marker)
        self.assertEqual(
            self._snapshot_fixture_sources(),
            self.initial_snapshot,
            f"fixture official-source bytes changed after {mode} probe of {relative}",
        )
        return result, completed

    def test_imports_are_side_effect_free(self):
        for relative in LEGACY_SCRIPTS:
            with self.subTest(script=relative):
                result, completed = self._probe(relative, "import")
                self.assertIsNone(
                    result["exception"],
                    f"import failed for {relative}: {result}; stderr={completed.stderr}",
                )
                self.assertEqual(
                    result["writes"],
                    [],
                    f"intercepted import-time write attempts for {relative}: {result['writes']}",
                )
                self.assertEqual(
                    result["side_effects"],
                    [],
                    f"intercepted import-time process side effects for {relative}: {result['side_effects']}",
                )

    def test_direct_entrypoints_fail_closed_even_with_force_options(self):
        for relative in LEGACY_SCRIPTS:
            with self.subTest(script=relative):
                result, completed = self._probe(relative, "direct")
                exception = result["exception"]
                self.assertIsNotNone(
                    exception,
                    f"retired direct entrypoint unexpectedly returned for {relative}",
                )
                self.assertEqual(
                    exception["type"],
                    "SystemExit",
                    f"entrypoint did not fail closed explicitly for {relative}: {result}; "
                    f"stderr={completed.stderr}",
                )
                self.assertNotEqual(exception["code"], 0, f"entrypoint accepted invocation: {relative}")
                self.assertEqual(
                    result["writes"],
                    [],
                    f"intercepted direct-entry write attempts for {relative}: {result['writes']}",
                )
                self.assertEqual(
                    result["side_effects"],
                    [],
                    f"intercepted direct-entry process side effects for {relative}: {result['side_effects']}",
                )


if __name__ == "__main__":
    unittest.main()
