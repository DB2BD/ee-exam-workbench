# -*- coding: utf-8 -*-
"""建立 GitHub Pages 最小但完整的靜態發布目錄。"""

from pathlib import Path
import shutil
import sys
import json
import os
import re

ROOT = Path(os.environ.get("PAGES_STAGE_ROOT", Path(__file__).resolve().parents[1])).resolve()
DEST = Path(os.environ.get("PAGES_STAGE_DEST", ROOT / "_site")).resolve()
ROOT_FILES = ["index.html", "dashboard-data.js", "solutions-bundle.js", "national-exams-data.js", "national-solutions-bundle.js"]
ASSET_ROOTS = ["data/official_pdfs", "reports/circuit-diagrams", "依考科分類"]
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".pdf", ".woff", ".woff2", ".ttf"}
RUNTIME_LIBS = {
    "libs/katex.min.css",
    "libs/katex.min.js",
    "libs/auto-render.min.js",
    "libs/marked.min.js",
}


def stage() -> tuple[int, int]:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir()
    count = 0
    size = 0
    for name in ROOT_FILES:
        source = ROOT / name
        if not source.is_file():
            raise FileNotFoundError(name)
        target = DEST / name
        shutil.copy2(source, target)
        count += 1
        size += target.stat().st_size
    for name in sorted(RUNTIME_LIBS):
        source = ROOT / name
        if not source.is_file():
            raise FileNotFoundError(name)
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        count += 1
        size += target.stat().st_size
    fonts_root = ROOT / "libs/fonts"
    if fonts_root.exists():
        for source in fonts_root.rglob("*"):
            if not source.is_file() or source.suffix.lower() not in ASSET_SUFFIXES:
                continue
            target = DEST / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            count += 1
            size += target.stat().st_size
    for root_name in ASSET_ROOTS:
        source_root = ROOT / root_name
        if not source_root.exists():
            continue
        for source in source_root.rglob("*"):
            if not source.is_file() or source.suffix.lower() not in ASSET_SUFFIXES:
                continue
            target = DEST / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            count += 1
            size += target.stat().st_size
    return count, size


def assignment(path: Path, marker: str):
    text = path.read_text(encoding="utf-8")
    start = text.find(marker)
    if start < 0:
        return None
    return json.JSONDecoder().raw_decode(text[start + len(marker):].lstrip())[0]


def verify_staged() -> None:
    required = set(ROOT_FILES) | RUNTIME_LIBS
    for bundle, marker in [
        (DEST / "solutions-bundle.js", "const IMAGE_MAP = "),
        (DEST / "national-solutions-bundle.js", "const NATIONAL_IMAGE_MAP = "),
    ]:
        mapping = assignment(bundle, marker) or {}
        required.update(value for value in mapping.values() if isinstance(value, str))
    crop_map = assignment(DEST / "dashboard-data.js", "const QUESTION_CROP_MAP = ") or {}
    required.update(value for value in crop_map.values() if isinstance(value, str))
    for data_file, pattern in [
        (DEST / "dashboard-data.js", r"questions:\s*(\[[\s\S]*?\])\s*,\s*\n\s*sevenLayers"),
        (DEST / "national-exams-data.js", r"questions:\s*(\[[\s\S]*?\])\s*\n\s*\};"),
    ]:
        matched = re.search(pattern, data_file.read_text(encoding="utf-8"))
        if not matched:
            raise ValueError(f"無法解析題目清單：{data_file.name}")
        for question in json.loads(matched.group(1)):
            for index in (7, 14):
                if index < len(question) and isinstance(question[index], str) and question[index] and not question[index].startswith(("http://", "https://")):
                    required.add(question[index])
    invalid = []
    missing = []
    for reference in required:
        normalized = reference.replace("\\", "/")
        relative = Path(normalized)
        if relative.is_absolute() or ".." in relative.parts:
            invalid.append(reference)
            continue
        if not (DEST / normalized.removeprefix("./")).is_file():
            missing.append(reference)
    if invalid:
        raise ValueError(f"staging 含不安全引用路徑；首項：{sorted(invalid)[0]}")
    missing.sort()
    if missing:
        raise FileNotFoundError(f"staging 缺少 {len(missing)} 個執行期資產；首項：{missing[0]}")


if __name__ == "__main__":
    try:
        files, total = stage()
        verify_staged()
    except (OSError, ValueError) as error:
        print(f"❌ Pages staging 失敗：{error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"✅ Pages staging：{files} files，{total / 1024 / 1024:.1f} MiB → {DEST}")
