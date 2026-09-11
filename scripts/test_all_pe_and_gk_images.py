# -*- coding: utf-8 -*-
"""Audit PE／GK solution image maps and every bundled Markdown image ref."""

import json
import os
import re
from urllib.parse import unquote


WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)


def parse_json_assignment(source, marker):
    """Parse one JSON object without regex-truncating strings containing ``});``."""
    start = source.find(marker)
    if start < 0:
        return {}
    value, _ = json.JSONDecoder().raw_decode(source[start + len(marker):].lstrip())
    return value


def load_bundle(path, md_marker, image_marker):
    with open(path, 'r', encoding='utf-8') as fp:
        source = fp.read()
    return (
        parse_json_assignment(source, md_marker),
        parse_json_assignment(source, image_marker),
    )


pe_bundle, pe_image_map = load_bundle(
    'solutions-bundle.js', 'const BUNDLED_MD = ', 'const IMAGE_MAP = '
)
gk_bundle, gk_image_map = load_bundle(
    'national-solutions-bundle.js',
    'const NATIONAL_BUNDLED_MD = ',
    'const NATIONAL_IMAGE_MAP = ',
)


def image_refs(markdown):
    refs = re.findall(r'!\[\[([^|\]]+)(?:\|[^\]]+)?\]\]', markdown)
    refs += re.findall(r'!\[[^\]]*\]\(([^)\n]+)\)', markdown)
    return [ref.strip() for ref in refs if ref.strip()]


def lookup_image(image_ref, preferred_map, fallback_map):
    clean = unquote(image_ref.strip()).replace('\\', '/')
    clean = clean.split('?', 1)[0].split('#', 1)[0]
    clean = clean.removeprefix('./')
    candidates = [clean, os.path.basename(clean)]
    for image_map in (preferred_map, fallback_map):
        for candidate in candidates:
            resolved = image_map.get(candidate)
            if resolved:
                return resolved
    return ''


def audit_bundle(label, bundle, preferred_map, fallback_map):
    broken = []
    checked = 0
    for md_path, md_text in bundle.items():
        for image_ref in image_refs(md_text):
            if re.match(r'^(?:data:|blob:|https?:|//)', image_ref, re.I):
                continue
            checked += 1
            resolved = lookup_image(image_ref, preferred_map, fallback_map)
            if not resolved or not os.path.exists(resolved):
                broken.append((md_path, image_ref, resolved))

    missing_targets = [
        (key, value) for key, value in preferred_map.items()
        if not value or not os.path.exists(value)
    ]
    print(f'{label} Image Map Keys: {len(preferred_map)}')
    print(f'{label} Bundled MD files: {len(bundle)}')
    print(f'{label} Markdown image refs checked: {checked}')
    print(f'{label} mapped targets missing on disk: {len(missing_targets)}')
    print(f'{label} broken Markdown refs: {len(broken)}')
    for md_path, image_ref, resolved in broken:
        print(f'  Broken: {md_path} -> {image_ref} (resolved: {resolved or "none"})')
    return broken, missing_targets


pe_broken, pe_missing = audit_bundle('PE', pe_bundle, pe_image_map, gk_image_map)
gk_broken, gk_missing = audit_bundle('GK', gk_bundle, gk_image_map, pe_image_map)

if pe_broken or gk_broken or pe_missing or gk_missing:
    raise SystemExit(1)

print('✅ PE／GK 圖片映射、題解引用與實體檔案全部通過。')
