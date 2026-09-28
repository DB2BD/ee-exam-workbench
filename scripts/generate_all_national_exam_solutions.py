# -*- coding: utf-8 -*-
"""Retired legacy GK solution writer; kept only to fail closed safely."""


def main() -> int:
    raise SystemExit(
        "Retired: this legacy writer can overwrite source-linked GK solutions. "
        "Use reviewed, source-hash-bound solution files instead."
    )


if __name__ == "__main__":
    main()
