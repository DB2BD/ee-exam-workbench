# -*- coding: utf-8 -*-
import os
import re
import json

base_dir = '/Users/a/技師考試/歷屆試題_104-114年'
os.chdir(base_dir)

# Load IMAGE_MAP from solutions-bundle.js
with open('solutions-bundle.js', 'r', encoding='utf-8') as fp:
    txt = fp.read()

m = re.search(r'const IMAGE_MAP = ({.*?});', txt, re.DOTALL)
if m:
    image_map = json.loads(m.group(1))
else:
    image_map = {}

print(f"IMAGE_MAP entries: {len(image_map)}")

# Scan all markdown files for any image reference
all_img_refs = []
for root, dirs, files in os.walk('.'):
    if any(s in root for s in ['.git', 'node_modules', '.agents', '.system_generated']):
        continue
    for f in files:
        if f.endswith('.md'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
            
            # Find ![[...]]
            for im in re.findall(r'!\[\[(.*?)\]\]', content):
                clean = im.split('|')[0].strip()
                all_img_refs.append((fpath, clean, 'obsidian'))
            
            # Find ![alt](...)
            for alt, src in re.findall(r'!\[(.*?)\]\((.*?)\)', content):
                if not src.startswith('http'):
                    all_img_refs.append((fpath, src.strip(), 'markdown'))

print(f"Total image references across markdown files: {len(all_img_refs)}")

# Check resolution for every image reference
broken_disk = []
broken_map = []

for fpath, ref, itype in all_img_refs:
    # 1. Test relative to fpath
    rel_on_disk = os.path.normpath(os.path.join(os.path.dirname(fpath), ref.split('#')[0].split('?')[0]))
    exists_rel = os.path.exists(rel_on_disk)
    
    # 2. Test basename in entire repository
    basename = os.path.basename(ref)
    clean_name = re.sub(r'^\./', '', ref).strip()
    
    # Check in image_map
    resolved_web = image_map.get(clean_name) or image_map.get(basename) or image_map.get(ref)
    web_exists = False
    if resolved_web and os.path.exists(resolved_web):
        web_exists = True
        
    if not exists_rel and not web_exists:
        broken_disk.append((fpath, ref, itype))
    if not web_exists:
        broken_map.append((fpath, ref, itype, resolved_web))

print(f"\n❌ Broken on disk (File does not exist anywhere): {len(broken_disk)}")
for fpath, ref, itype in broken_disk:
    print(f"   - in {fpath}: {ref} ({itype})")

print(f"\n⚠️ Web IMAGE_MAP unresolved: {len(broken_map)}")
for fpath, ref, itype, res in broken_map[:15]:
    print(f"   - in {fpath}: {ref} -> mapped to '{res}'")
if len(broken_map) > 15:
    print(f"   ... and {len(broken_map)-15} more")
