# -*- coding: utf-8 -*-
import os
import re

base_dir = '/Users/a/技師考試/歷屆試題_104-114年'
os.chdir(base_dir)

# Build comprehensive filename -> canonical relative path map
img_registry = {}
for root, dirs, files in os.walk('.'):
    if any(s in root for s in ['.git', 'node_modules', '.agents', '.system_generated']):
        continue
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp')):
            rel = os.path.relpath(os.path.join(root, f), '.').replace(os.sep, '/')
            img_registry[f] = rel
            img_registry[rel] = rel

print(f"Total image files discovered on disk: {len([k for k in img_registry if not '/' in k])}")

# Scan and standardize all Markdown files
updated_files = 0
total_img_refs = 0

for root, dirs, files in os.walk('.'):
    if any(s in root for s in ['.git', 'node_modules', '.agents', '.system_generated']):
        continue
    for f in files:
        if f.endswith('.md'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
            
            orig = content
            
            # 1. Standardize markdown images ![alt](path)
            def fix_std_img(m):
                global total_img_refs
                total_img_refs += 1
                alt = m.group(1)
                src = m.group(2).strip()
                if src.startswith('http'):
                    return m.group(0)
                
                # Check if src points directly to an existing file relative to fpath
                local_target = os.path.normpath(os.path.join(os.path.dirname(fpath), src))
                if os.path.exists(local_target):
                    return m.group(0)
                
                # Try to find by basename
                basename = os.path.basename(src)
                if basename in img_registry:
                    # Calculate correct relative path from fpath to target
                    target_rel = img_registry[basename]
                    correct_rel = os.path.relpath(target_rel, os.path.dirname(fpath)).replace(os.sep, '/')
                    return f'![{alt}]({correct_rel})'
                return m.group(0)

            content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_std_img, content)
            
            # 2. Check Obsidian images ![[image|size]]
            def fix_obs_img(m):
                global total_img_refs
                total_img_refs += 1
                img_spec = m.group(1)
                parts = img_spec.split('|')
                img_name = parts[0].strip()
                size = parts[1].strip() if len(parts) > 1 else ''
                
                if img_name in img_registry:
                    # It's valid in Obsidian
                    return m.group(0)
                else:
                    basename = os.path.basename(img_name)
                    if basename in img_registry:
                        new_spec = basename + (f'|{size}' if size else '')
                        return f'![[{new_spec}]]'
                return m.group(0)

            content = re.sub(r'!\[\[(.*?)\]\]', fix_obs_img, content)
            
            if content != orig:
                with open(fpath, 'w', encoding='utf-8') as fp:
                    fp.write(content)
                updated_files += 1
                print(f"  🔧 Standardized image paths in: {fpath}")

print(f"\nChecked {total_img_refs} image references across repository.")
print(f"Updated {updated_files} files.")
