# -*- coding: utf-8 -*-
import sys
import os

try:
    from PIL import Image, ImageOps, ImageChops
except ImportError:
    # Fallback to local vendored scripts/lib if present
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(workspace, 'scripts', 'lib'))
    from PIL import Image, ImageOps, ImageChops

out_dir = '依考科分類/05_電力系統/images'
os.makedirs(out_dir, exist_ok=True)

def crop_and_autotrim(src_file, box, out_name):
    src_path = os.path.join(out_dir, src_file)
    if not os.path.exists(src_path):
        print(f"Warning: {src_path} not found")
        return
    im = Image.open(src_path).convert('RGB')
    cropped = im.crop(box)
    
    # Auto-trim whitespace
    gray = cropped.convert('L')
    table = [255 if i < 240 else 0 for i in range(256)]
    binary = gray.point(table, '1')
    bbox = binary.getbbox()
    if bbox:
        pad = 16
        w, h = cropped.size
        tight_box = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(w, bbox[2] + pad),
            min(h, bbox[3] + pad)
        )
        cropped = cropped.crop(tight_box)
        
    out_path = os.path.join(out_dir, out_name)
    cropped.save(out_path, optimize=True)
    print(f"✅ Generated {out_name}: size {cropped.size}")

# 114 年
crop_and_autotrim('114年_電機工程技師_電力系統_p1.png', (0, 300, 1148, 1100), '114年_電力系統_第2題_單線圖.png')
crop_and_autotrim('114年_電機工程技師_電力系統_p2.png', (0, 0, 1146, 750), '114年_電力系統_第4題_短路單線圖.png')

# 113 年
crop_and_autotrim('113年_電機工程技師_電力系統_p1.png', (0, 0, 1147, 650), '113年_電力系統_第1題_並聯負載圖.png')
crop_and_autotrim('113年_電機工程技師_電力系統_p1.png', (0, 600, 1147, 1421), '113年_電力系統_第2題_同步機短路圖.png')

# 112 年
crop_and_autotrim('112年_電機工程技師_電力系統_p1.png', (0, 0, 1146, 700), '112年_電力系統_第1題_圖一四分裂導線.png')
crop_and_autotrim('112年_電機工程技師_電力系統_p2.png', (0, 0, 1145, 600), '112年_電力系統_第3題_圖二4Bus單線圖.png')
crop_and_autotrim('112年_電機工程技師_電力系統_p2.png', (0, 550, 1145, 1144), '112年_電力系統_第4題_圖三單機無窮母線圖.png')

# 111 年
crop_and_autotrim('111年_電機工程技師_電力系統_p1.png', (0, 200, 1146, 1424), '111年_電力系統_第2題_五匯流排阻抗圖.png')
crop_and_autotrim('111年_電機工程技師_電力系統_p2.png', (0, 0, 1145, 783), '111年_電力系統_第4題_長程線路模型圖.png')

# 110 年
crop_and_autotrim('110年_電機工程技師_電力系統_p1.png', (0, 450, 1147, 1609), '110年_電力系統_第2題_三匯流排單線圖.png')
crop_and_autotrim('110年_電機工程技師_電力系統_p2.png', (0, 200, 1146, 1200), '110年_電力系統_第4題_經濟調度損耗單線圖.png')

# 109 年
crop_and_autotrim('109年_電機工程技師_電力系統_p1.png', (0, 200, 1147, 800), '109年_電力系統_第2題_雙分裂導線幾何圖.png')
crop_and_autotrim('109年_電機工程技師_電力系統_p1.png', (0, 750, 1147, 1493), '109年_電力系統_第3題_二匯流排潮流圖.png')
crop_and_autotrim('109年_電機工程技師_電力系統_p2.png', (0, 0, 1165, 800), '109年_電力系統_第4題_系統電抗表與單線圖.png')

# 108 年
crop_and_autotrim('108年_電機工程技師_電力系統_p1.png', (0, 450, 1147, 1237), '108年_電力系統_第2題_快速解耦潮流圖.png')
crop_and_autotrim('108年_電機工程技師_電力系統_p2.png', (0, 0, 1145, 750), '108年_電力系統_第3題_雙發電機故障圖.png')
crop_and_autotrim('108年_電機工程技師_電力系統_p2.png', (0, 700, 1145, 1376), '108年_電力系統_第4題_發電機差動保護電路圖.png')
crop_and_autotrim('108年_電機工程技師_電力系統_p3.png', (0, 0, 1148, 733), '108年_電力系統_第5題_雙迴線故障單線圖.png')

# 107 年
crop_and_autotrim('107年_電機工程技師_電力系統_p1.png', (0, 0, 1147, 800), '107年_電力系統_第1題_輸電線負載圖.png')
crop_and_autotrim('107年_電機工程技師_電力系統_p1.png', (0, 750, 1147, 1582), '107年_電力系統_第2題_變壓器等效圖.png')
crop_and_autotrim('107年_電機工程技師_電力系統_p2.png', (0, 0, 1143, 501), '107年_電力系統_第3題_發電機併網圖.png')

# 106 年
crop_and_autotrim('106年_電機工程技師_電力系統_p1.png', (0, 600, 1329, 2045), '106年_電機工程技師_電力系統_第2題_阻抗單線圖.png')
crop_and_autotrim('106年_電機工程技師_電力系統_p2.png', (0, 0, 1326, 1022), '106年_電機工程技師_電力系統_第4題_差動電驛保護圖.png')

# 105 年
crop_and_autotrim('105年_電機工程技師_電力系統_p1.png', (0, 200, 1329, 1100), '105年_電力系統_第2題_三匯流排潮流圖.png')
crop_and_autotrim('105年_電機工程技師_電力系統_p1.png', (0, 950, 1329, 1834), '105年_電力系統_第3題_同步機接地單線圖.png')

# 104 年
crop_and_autotrim('104年_電機工程技師_電力系統_p1.png', (0, 400, 1334, 1939), '104年_電力系統_第1題_圖一系統單線圖.png')
crop_and_autotrim('104年_電機工程技師_電力系統_p2.png', (0, 0, 1335, 750), '104年_電力系統_第2題_變壓器並聯電路圖.png')
crop_and_autotrim('104年_電機工程技師_電力系統_p2.png', (0, 700, 1335, 1250), '104年_電力系統_第3題_兩發電機併網圖.png')
crop_and_autotrim('104年_電機工程技師_電力系統_p2.png', (0, 1200, 1335, 1695), '104年_電力系統_第4題_三匯流排阻抗圖.png')
