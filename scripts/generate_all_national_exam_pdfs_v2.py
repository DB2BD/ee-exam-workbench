# -*- coding: utf-8 -*-
"""Retired legacy synthetic GK PDF writer; kept only to fail closed safely."""


def main() -> int:
    raise SystemExit(
        "Retired: only official MOEX PDFs may be presented as exam sources. "
        "This legacy command is disabled and will not create or overwrite PDFs."
    )


if __name__ == "__main__":
    main()
