# -*- coding: utf-8 -*-
import re
import os

# 1. Polish 04_電機機械.md 112 年
with open('依考科分類/04_電機機械.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '額定25 Hp、208 V、$60\\text{ Hz}$、Y 接之三相同步電動機',
    '#### 三、 額定25 Hp、208 V、$60\\text{ Hz}$、Y 接之三相同步電動機'
)
text = text.replace(
    '額定35 Hp、380 V、$60\\text{ Hz}$、Y 接之三相感應電動機',
    '#### 四、 額定35 Hp、380 V、$60\\text{ Hz}$、Y 接之三相感應電動機'
)
text = text.replace(
    '額定50 馬力、250V、1200rpm 的直流並激電動機',
    '#### 五、 額定50 馬力、250V、1200rpm 的直流並激電動機'
)

# 113 機械 Q3, Q4, Q5
text = text.replace(
    '一300 V、60 A、1800 轉/分（rpm）的串激直流馬達',
    '#### 三、 一300 V、60 A、1800 轉/分（rpm）的串激直流馬達'
)
text = text.replace(
    '一220 V、$60\\text{ Hz}$、1120 轉/分（rpm）三相感應馬達',
    '#### 四、 一220 V、$60\\text{ Hz}$、1120 轉/分（rpm）三相感應馬達'
)
text = text.replace(
    '一240 V、$60\\text{ Hz}$、4 極電容啟動單相感應馬達',
    '#### 五、 一240 V、$60\\text{ Hz}$、4 極電容啟動單相感應馬達'
)

with open('依考科分類/04_電機機械.md', 'w', encoding='utf-8') as f:
    f.write(text)
print('✅ Fixed 04_電機機械.md')

# 2. Polish 05_電力系統.md 113 & 109
with open('依考科分類/05_電力系統.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 113 年
text = text.replace(
    '如下圖所示，為由一個三相平衡電源供電給兩個並聯三相負載之架構',
    '#### 一、 如下圖所示，為由一個三相平衡電源供電給兩個並聯三相負載之架構'
)
text = text.replace(
    '一部額定為三相、$100\\text{ MVA}$、$24\\text{ kV}$、$60\\text{ Hz}$、暫態電抗0.25',
    '#### 二、 一部額定為三相、$100\\text{ MVA}$、$24\\text{ kV}$、$60\\text{ Hz}$、暫態電抗0.25'
)
text = text.replace(
    '兩部額定容量$1300\\text{ MW}$ 之火力發電機組',
    '#### 三、 兩部額定容量$1300\\text{ MW}$ 之火力發電機組'
)
text = text.replace(
    '一部同步發電機之額定容量為$500\\text{ MW}$，其調速機具有標準的速度調節',
    '#### 四、 一部同步發電機之額定容量為$500\\text{ MW}$，其調速機具有標準的速度調節'
)

# 109 年
text = text.replace(
    '一負載的端電壓( )',
    '#### 一、 一負載的端電壓 $v(t) = \\sqrt{2} V \\cos(\\omega t + \\alpha)\\text{ V}$'
)
text = text.replace(
    '有一三相、$345\\text{ kV}$、$60\\text{ Hz}$ 有換位的輸電線',
    '#### 二、 有一三相、$345\\text{ kV}$、$60\\text{ Hz}$ 有換位的輸電線'
)
text = text.replace(
    '圖一所示為一具有二匯流排之電力系統（two-bus power system）',
    '#### 三、 圖一所示為一具有二匯流排之電力系統（two-bus power system）'
)
text = text.replace(
    '試針對發生在匯流排1 的故障，求其戴維寧相序阻抗',
    '#### 四、 試針對發生在匯流排1 的故障，求其戴維寧相序阻抗'
)
text = text.replace(
    '二座發電廠，有相同燃料成本，燃料成本',
    '#### 五、 二座發電廠，有相同燃料成本，燃料成本'
)
text = text.replace(
    '包含二發電機組之單區域，二機組之額定為$500\\text{ MVA}$',
    '#### 六、 包含二發電機組之單區域，二機組之額定為$500\\text{ MVA}$'
)

with open('依考科分類/05_電力系統.md', 'w', encoding='utf-8') as f:
    f.write(text)
print('✅ Fixed 05_電力系統.md')

# 3. Polish 06_工業配電.md 113 年
with open('依考科分類/06_工業配電.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Clean duplicate headers in 113
text = text.replace('#### 二、 由電錶得知各分廠一', '由電錶得知各分廠一')
text = text.replace('#### 三、 有一阻抗為1.68', '#### 二、 有一阻抗為1.68')
text = text.replace('#### 四、 有一煉鋼廠之電弧爐', '#### 三、 有一煉鋼廠之電弧爐')
text = text.replace('#### 五、 某工廠之三相配電系', '#### 四、 某工廠之三相配電系')
text = text.replace('#### 六、 圖所示，已知電源側', '圖所示，已知電源側')
text = text.replace('#### 七、 有一配電系統之分路', '#### 五、 有一配電系統之分路')

with open('依考科分類/06_工業配電.md', 'w', encoding='utf-8') as f:
    f.write(text)
print('✅ Fixed 06_工業配電.md')
