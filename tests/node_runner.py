"""Drop-in for ``subprocess.run(["node", "-"], input=script, ...)`` backed by one long-lived Node worker.

Starting Node costs ~0.1 s; behaviour tests call it hundreds of times.  ``run`` sends the script to
``tests/node_worker.cjs`` (one per test process) and returns a ``CompletedProcess`` with the same
returncode/stdout/stderr.  Calls that set ``env`` (e.g. a TZ override) and scripts that evaluate code in
Node's own global scope (``runInThisContext``) still start their own Node.
"""

import atexit
import json
import subprocess
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = Path(__file__).with_name("node_worker.cjs")
_lock = threading.Lock()
_proc = None


def _worker():
    global _proc
    if _proc is None or _proc.poll() is not None:
        _proc = subprocess.Popen(
            ["node", str(WORKER)], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        atexit.register(_proc.kill)
    return _proc


def run(script, *, env=None, check=False, cwd=None, timeout=None, **_ignored):
    if env is not None or "runInThisContext" in script:
        return subprocess.run(["node", "-"], input=script, cwd=cwd or ROOT, env=env,
                              capture_output=True, text=True, check=check, timeout=timeout)
    with _lock:
        proc = _worker()
        proc.stdin.write(json.dumps({"script": script}) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
    if not line:
        raise RuntimeError("tests/node_worker.cjs exited unexpectedly")
    reply = json.loads(line)
    done = subprocess.CompletedProcess(["node", "-"], reply["code"], reply["stdout"], reply["stderr"])
    if check:
        done.check_returncode()
    return done
