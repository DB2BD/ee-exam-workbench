# -*- coding: utf-8 -*-
import json
import re

with open('dashboard-data.js', 'r', encoding='utf-8') as f:
    raw = f.read()

m = re.search(r'questions:\s*(\[[\s\S]*?\])\s*,\s*\n\s*sevenLayers', raw)
questions = json.loads(m.group(1))

in_prog = [q for q in questions if q[9] != 'verified']
print(f"Total in_progress PE questions: {len(in_prog)}")
for q in in_prog[:20]:
    print(f"  {q[0]} (Yr {q[2]}, Sid {q[1]}, Q{q[3]}): {q[4]} | solLink: {q[6]}")
