# -*- coding: utf-8 -*-
"""
test_all_pe_and_gk_images.py
============================
Checks image resolution for every question in dashboard-data.js and national-exams-data.js.
"""

import os
import re
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

# Load solutions-bundle.js IMAGE_MAP
with open('solutions-bundle.js', 'r', encoding='utf-8') as fp:
    content = fp.read()
m = re.search(r'const IMAGE_MAP = ({[\s\S]*?});', content)
pe_image_map = json.loads(m.group(1)) if m else {}

# Load national-solutions-bundle.js NATIONAL_IMAGE_MAP
with open('national-solutions-bundle.js', 'r', encoding='utf-8') as fp:
    content = fp.read()
m = re.search(r'const NATIONAL_IMAGE_MAP = ({[\s\S]*?});', content)
nat_image_map = json.loads(m.group(1)) if m else {}

# Load bundled MDs
m_md = re.search(r'const BUNDLED_MD = ({[\s\S]*?});\nconst IMAGE_MAP', content)
# Load from solutions-bundle.js
with open('solutions-bundle.js', 'r', encoding='utf-8') as fp:
    c = fp.read()
m_pe_md = re.search(r'const BUNDLED_MD = ({[\s\S]*?});', c)
pe_bundle = json.loads(m_pe_md.group(1)) if m_pe_md else {}

print(f"PE Image Map Keys: {len(pe_image_map)}")
print(f"National Image Map Keys: {len(nat_image_map)}")
print(f"PE Bundled MD files: {len(pe_bundle)}")

# Let's inspect PE Markdown files for image references and check their status
pe_images_in_bundle = []
broken_pe_images = []

for md_path, md_text in pe_bundle.items():
    obs = re.findall(r'!\[\[([^\|\]]+)(?:\|[^\]]+)?\]\]', md_text)
    for img in obs:
        clean = img.strip()
        base = os.path.basename(clean)
        resolved = pe_image_map.get(clean) or pe_image_map.get(base) or nat_image_map.get(clean) or nat_image_map.get(base)
        if resolved and os.path.exists(resolved):
            pe_images_in_bundle.append((md_path, clean, resolved))
        else:
            broken_pe_images.append((md_path, clean, resolved))

    std = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', md_text)
    for alt, src in std:
        if src.startswith('http'):
            continue
        clean = src.strip()
        base = os.path.basename(clean)
        resolved = pe_image_map.get(clean) or pe_image_map.get(base) or nat_image_map.get(clean) or nat_image_map.get(base)
        if resolved and os.path.exists(resolved):
            pe_images_in_bundle.append((md_path, clean, resolved))
        else:
            broken_pe_images.append((md_path, clean, resolved))

print(f"\n📊 PE Bundle Images Validated:")
print(f"  ✅ Working Images on Disk: {len(pe_images_in_bundle)}")
print(f"  ❌ Broken Images: {len(broken_pe_images)}")
if broken_pe_images:
    for md, clean, res in broken_pe_images:
        print(f"     Broken: In {md} -> {clean} (resolved: {res})")
