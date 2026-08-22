#!/usr/bin/env python3
from fractions import Fraction

def solve_108_q2_pure_python():
    print("=== 108年 電路學 第二題 純 Python 精確推導 ===")
    
    # 設參考節點為最下方接地線 (0V)
    # 設節點電壓：
    # V2 = v (4歐姆跨壓)
    # V1 = v + 6 (6V獨立電壓源)
    # i1 = 流向左側之電流 = 向上流經 1歐姆 => i1 = -V1/1 = -(v + 6) = -v - 6
    # V3 = V2 + 4*i1 = v + 4*(-v - 6) = -3*v - 24
    
    # 頂部節點 4 (Node 4):
    # KCL at Node 4: 6 + (V4 - V3)/1 + V4/2 = 0
    # 1.5 * V4 - V3 + 6 = 0 => 1.5 * V4 = V3 - 6 = (-3*v - 24) - 6 = -3*v - 30
    # => V4 = (-3*v - 30) / 1.5 = -2*v - 20
    # => v2 = V4 - V3 = (-2*v - 20) - (-3*v - 24) = v + 4
    
    # 超級節點 (Supernode: Node 1 + Node 2 + Node 3) KCL:
    # 流出電流 = 流入電流
    # V1/1 + V2/4 = 6 (from Node 4 to 1) + v2 (from Node 4 to 3) + 1.5*v2 (from ground to 3)
    # (v + 6) + v/4 = 6 + 2.5 * (v + 4)
    # 1.25 * v + 6 = 2.5 * v + 16
    # -1.25 * v = 10 => v = -10 / 1.25 = -8 V
    
    v = Fraction(-10, 1) / Fraction(5, 4)
    V1 = v + 6
    i1 = -V1
    V3 = v + 4 * i1
    V4 = -2 * v - 20
    v2 = V4 - V3
    P_2ohm = (V4**2) / 2
    
    print(f"v (4歐姆跨壓) = {v} V ({float(v):.2f} V)")
    print(f"V1 (左側節點) = {V1} V ({float(V1):.2f} V)")
    print(f"i1 (左下電流) = {i1} A ({float(i1):.2f} A)")
    print(f"V3 (中間節點) = {V3} V ({float(V3):.2f} V)")
    print(f"V4 (頂部節點) = {V4} V ({float(V4):.2f} V)")
    print(f"v2 (1歐姆跨壓) = {v2} V ({float(v2):.2f} V)")
    print(f"P_2ohm (2歐姆消耗功率) = {P_2ohm} W ({float(P_2ohm):.2f} W)")
    
    # 驗算各支路 KCL 守恆：
    # 節點 4 流出總和：
    kcl_node4 = 6 + (V4 - V3)/1 + V4/2
    print(f"驗算 節點 4 KCL: {kcl_node4} (應為 0)")
    
    # 超級節點 KCL：
    kcl_super = (V1/1 + v/4) - (6 + v2 + Fraction(3,2)*v2)
    print(f"驗算 超級節點 KCL: {kcl_super} (應為 0)")

if __name__ == '__main__':
    solve_108_q2_pure_python()
