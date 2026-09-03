# -*- coding: utf-8 -*-
import os
import re

print("=== 🚀 批次強化全資料庫防坑 Warning 卡片 ===")

warnings_map = {
    '04_電機機械': r"""
> [!WARNING]
> ⚠️ **電機機械 核心防坑與閱卷踩雷提醒**：
> 1. **變壓器阻抗折合**：低壓側折合至高壓側乘以變比平方 $a^2$；自耦變壓器共用繞組電流為高低壓側電流之差值。
> 2. **感應機最大轉矩**：最大轉矩 $T_{max}$ 與轉子電阻 $R_2$ 無關，但產生最大轉矩之轉差率 $s_{max}$ 與 $R_2$ 成正比。
> 3. **同步機相量計算**：同步電動機 $\mathbf{E}_f = \mathbf{V}_\phi - \mathbf{I}_a \mathbf{Z}_s$；同步發電機 $\mathbf{E}_f = \mathbf{V}_\phi + \mathbf{I}_a \mathbf{Z}_s$。
""",
    '01_電路學': r"""
> [!WARNING]
> ⚠️ **電路學 核心防坑與閱卷踩雷提醒**：
> 1. **複數功率共軛**：$\mathbf{S} = \mathbf{V}\mathbf{I}^* = P + jQ$，電流 $\mathbf{I}$ 務必取共軛，電感性負載 $Q > 0$（落後），電容性負載 $Q < 0$（超前）。
> 2. **三相功率計算**：三相總功率公式 $P = \sqrt{3}V_L I_L \cos\theta = 3V_\phi I_\phi \cos\theta$，代入線電壓時必有 $\sqrt{3}$。
> 3. **一階暫態連續性**：電感電流 $i_L(0^+) = i_L(0^-)$ 與電容電壓 $v_C(0^+) = v_C(0^-)$ 不可突變。
""",
    '05_電力系統': r"""
> [!WARNING]
> ⚠️ **電力系統 核心防坑與閱卷踩雷提醒**：
> 1. **對稱成分故障計算**：單相接地 (SLG) 故障電流為 $I_f = 3I_{a1} = \frac{3V_f}{Z_1 + Z_2 + Z_0 + 3Z_n}$，千萬不可漏乘 3 倍！
> 2. **旋轉相量符號**：$a^2 - a = -j\sqrt{3}$，而 $a - a^2 = +j\sqrt{3}$，正負序相量展開切勿混淆。
> 3. **等面積準則**：計算擺動極限角 $(\pi - \delta_0 - \delta_1)$ 時，分母角度嚴格必須使用**弧度 (Radian)** 代入！
""",
    '06_工業配電': r"""
> [!WARNING]
> ⚠️ **工業配電 核心防坑與閱卷踩雷提醒**：
> 1. **短路電流計算**：三相對稱短路電流 $I_{sc} = \frac{S_{base}}{\sqrt{3} V_L X_{pu}}$，分母必帶 $\sqrt{3}$。
> 2. **功因改善電容容量**：$Q_c = P(\tan\theta_1 - \tan\theta_2)$，串聯 6% 電抗器時電容器端電壓會上升至 $\frac{1}{1-0.06}V \approx 1.064V$。
> 3. **電壓降容許限度**：三相壓降 $\Delta V = \sqrt{3} I (R\cos\theta + X\sin\theta)$，幹線壓降需 $\le 3\%$，幹線加分路總壓降需 $\le 5\%$。
"""
}

count_updated = 0

for subj_dir, warn_text in warnings_map.items():
    folder = os.path.join('📝 個人題解與錯題本', subj_dir)
    if not os.path.exists(folder):
        continue
    for f in os.listdir(folder):
        if f.endswith('_全卷完整詳細題解.md'):
            fpath = os.path.join(folder, f)
            with open(fpath, 'r', encoding='utf-8') as fp:
                content = fp.read()
            
            if '> [!WARNING]' not in content:
                new_content = content.rstrip() + '\n\n---\n' + warn_text + '\n'
                with open(fpath, 'w', encoding='utf-8') as fp:
                    fp.write(new_content)
                count_updated += 1
                print(f"  ✅ 已安全注入標準防坑 Warning: {fpath}")

print(f"\n🎉 總共更新強化了 {count_updated} 份題解檔案！")
