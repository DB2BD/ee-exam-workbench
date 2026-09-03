# -*- coding: utf-8 -*-
import sys
import os

try:
    from PIL import Image, ImageOps, ImageChops
except ImportError:
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(workspace, 'scripts', 'lib'))
    from PIL import Image, ImageOps, ImageChops

count_cropped = 0
total_saved_pixels = 0

for root, dirs, files in os.walk('.'):
    if '.agents' in root or '.gemini' in root or 'node_modules' in root:
        continue
    for f in sorted(files):
        if f.endswith('.png') or f.endswith('.jpg'):
            full_path = os.path.join(root, f)
            try:
                im = Image.open(full_path).convert('RGB')
                w, h = im.size
                
                # Convert to grayscale
                gray = im.convert('L')
                # Threshold to isolate non-white content (ink pixels)
                table = [255 if i < 240 else 0 for i in range(256)]
                binary = gray.point(table, '1')
                
                bbox = binary.getbbox()
                if bbox:
                    pad = 24
                    crop_box = (
                        max(0, bbox[0] - pad),
                        max(0, bbox[1] - pad),
                        min(w, bbox[2] + pad),
                        min(h, bbox[3] + pad)
                    )
                    
                    cropped_w = crop_box[2] - crop_box[0]
                    cropped_h = crop_box[3] - crop_box[1]
                    
                    # If we cropped away more than 5% of height or width
                    if cropped_w < w * 0.98 or cropped_h < h * 0.98:
                        cropped_im = im.crop(crop_box)
                        cropped_im.save(full_path, optimize=True)
                        count_cropped += 1
                        saved_pct = (1 - (cropped_w * cropped_h) / (w * h)) * 100
                        print(f'✂️ Cropped {f}: {w}x{h} -> {cropped_w}x{cropped_h} (eliminated {saved_pct:.1f}% whitespace)')
            except Exception as e:
                print(f'Error processing {full_path}: {e}')

print(f'\n🎉 Total images auto-cropped: {count_cropped}')
