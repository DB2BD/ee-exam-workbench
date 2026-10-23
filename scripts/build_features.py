# -*- coding: utf-8 -*-
"""Run the data generator of every optional feature (src/features/<name>/build.py), if it has one."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    status = 0
    for script in sorted((ROOT / "src" / "features").glob("*/build.py")):
        done = subprocess.run([sys.executable, str(script)], cwd=ROOT)
        status = status or done.returncode
    return status


if __name__ == "__main__":
    sys.exit(main())
