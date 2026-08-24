# -*- coding: utf-8 -*-
"""
diagnose_images_and_solutions.py
================================
Scans all markdown files, checks every image reference (![[...]] and ![...](...)),
checks all solution links and PDF links in DB_DATA and NATIONAL_EXAMS_DATA.
"""

import os
import re
import json
import urllib.parse

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

print("🔍 === 1. Checking Image References across all Markdown files ===")
all_md_files = []
for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.git', '.agents', 'node_modules', '.system_generated', '.tempmediaStorage']):
        continue
    for f in files:
        if f.endswith('.md'):
            all_md_files.append(os.path.join(root, f))

# Find all physical images on disk
disk_images = {}
for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.git', '.agents', 'node_modules', '.system_generated', '.tempmediaStorage']):
        continue
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif')):
            rel = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
            disk_images[f] = rel
            disk_images[rel] = rel
            disk_images['./' + rel] = rel
            disk_images[urllib.parse.quote(f)] = rel
            disk_images[urllib.parse.quote(rel)] = rel

print(f"Total physical images found on disk: {len(set(disk_images.values()))}")

missing_images = []
found_images = []

for md in all_md_files:
    with open(md, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()

    # Obsidian ![[...]]
    obs_matches = re.findall(r'!\[\[([^\|\]]+)(?:\|[^\]]+)?\]\]', content)
    for img_ref in obs_matches:
        img_clean = img_ref.strip()
        img_base = os.path.basename(img_clean)
        # Check if exists in disk_images
        resolved = disk_images.get(img_clean) or disk_images.get(img_base) or disk_images.get(urllib.parse.unquote(img_clean))
        if not resolved:
            missing_images.append((md, img_clean, 'Obsidian ![['))
        else:
            found_images.append((md, img_clean, resolved))

    # Standard ![alt](src)
    std_matches = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
    for alt, src in std_matches:
        if src.startswith('http'):
            continue
        src_clean = src.strip()
        src_base = os.path.basename(src_clean)
        resolved = disk_images.get(src_clean) or disk_images.get(src_base) or disk_images.get(urllib.parse.unquote(src_clean))
        if not resolved:
            missing_images.append((md, src_clean, 'Standard ![]()'))
        else:
            found_images.append((md, src_clean, resolved))

print(f"✅ Found and verified image references: {len(found_images)}")
print(f"⚠️ Missing or unmapped image references: {len(missing_images)}")

if missing_images:
    print("\n--- Missing Image Details (first 30): ---")
    for md, ref, style in missing_images[:30]:
        print(f"  ❌ In {md}: '{ref}' ({style})")

print("\n🔍 === 2. Checking Solution Links & PDF Links in DB_DATA ===")
if os.path.exists('dashboard-data.js'):
    with open('dashboard-data.js', 'r', encoding='utf-8') as fp:
        raw = fp.read()
    match = re.search(r'questions:\s*(\[[\s\S]*?\])\s*,\s*\n\s*sevenLayers', raw)
    if match:
        pe_questions = json.loads(match.group(1))
        missing_sols = []
        missing_pdfs = []
        verified_count = 0
        in_progress_count = 0

        for q in pe_questions:
            qid, sid, yr, qnum, topic, tags, solLink, pdfLink, diff, vstatus, ftags, hasDed = q
            if vstatus == 'verified':
                verified_count += 1
            else:
                in_progress_count += 1

            clean_sol = solLink.split('#')[0] if solLink else ''
            if clean_sol and not os.path.exists(clean_sol):
                missing_sols.append((qid, solLink))
            if pdfLink and not os.path.exists(pdfLink):
                missing_pdfs.append((qid, pdfLink))

        print(f"PE Total Questions: {len(pe_questions)}")
        print(f"  - Verified: {verified_count}")
        print(f"  - In Progress: {in_progress_count}")
        print(f"  - Missing Solution Files: {len(missing_sols)}")
        print(f"  - Missing PDF Files: {len(missing_pdfs)}")
        if missing_sols[:5]:
            print(f"    Sample missing sols: {missing_sols[:5]}")
        if missing_pdfs[:5]:
            print(f"    Sample missing pdfs: {missing_pdfs[:5]}")

print("\n🔍 === 3. Checking Solutions & Links in NATIONAL_EXAMS_DATA ===")
if os.path.exists('national-exams-data.js'):
    with open('national-exams-data.js', 'r', encoding='utf-8') as fp:
        raw = fp.read()
    match = re.search(r'questions:\s*(\[[\s\S]*?\])\s*\n\s*\};', raw)
    if match:
        nat_questions = json.loads(match.group(1))
        missing_nat_sols = []
        for q in nat_questions:
            qid = q[0]
            solLink = q[6]
            clean_sol = solLink.split('#')[0] if solLink else ''
            if clean_sol and not os.path.exists(clean_sol):
                missing_nat_sols.append((qid, solLink))
        print(f"National Exams Total Questions: {len(nat_questions)}")
        print(f"  - Missing Solution Files: {len(missing_nat_sols)}")
