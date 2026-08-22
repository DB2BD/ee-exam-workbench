#!/usr/bin/env python3
"""
108 年電力系統第二題與第三題 第一原理獨立物理驗算腳本 (Adversarial Audit Script - Standard Library)
"""
import math
import cmath

def audit_108_q2():
    print("="*60)
    print("⚡ 審計 108 年電力系統第 2 題 (FDLF 快速解耦潮流)")
    print("="*60)
    
    # -B' = [[12, -12], [-12, 20]]
    # det(-B') = 12*20 - (-12)^2 = 240 - 144 = 96
    # (-B')^-1 = 1/96 * [[20, 12], [12, 12]] = [[5/24, 1/8], [1/8, 1/8]]
    inv_B_prime = [
        [5.0 / 24.0, 1.0 / 8.0],
        [1.0 / 8.0, 1.0 / 8.0]
    ]

    # -B'' = [20] -> (-B'')^-1 = 0.05
    inv_B_double_prime = 1.0 / 20.0

    # Iteration 1
    dP2_0 = 0.70 / 1.01
    dP3_0 = -0.90 / 1.0
    
    dTheta2_1 = inv_B_prime[0][0] * dP2_0 + inv_B_prime[0][1] * dP3_0
    dTheta3_1 = inv_B_prime[1][0] * dP2_0 + inv_B_prime[1][1] * dP3_0
    
    dTheta2_deg = math.degrees(dTheta2_1)
    dTheta3_deg = math.degrees(dTheta3_1)
    print(f"Iteration 1: theta2 = {dTheta2_deg:.4f} deg, theta3 = {dTheta3_deg:.4f} deg")

    # Q3 mismatch: Q3(0) = -0.28
    Q3_0 = -0.28
    dQ3_0 = (-0.80 - Q3_0) / 1.0
    dV3_1 = inv_B_double_prime * dQ3_0
    V3_1 = 1.0 + dV3_1
    print(f"Iteration 1: |V3| = {V3_1:.4f} pu (Delta |V3| = {dV3_1:.4f})")
    print("="*60)

def audit_108_q3():
    print("="*60)
    print("⚡ 審計 108 年電力系統第 3 題 (非對稱故障與變壓器相角位移)")
    print("="*60)
    V_base_G1 = 20.0 # kV
    V_base_G2 = 22.0 # kV
    Vf = 515.0 / 500.0 # 1.03 pu

    # G1 + T1 branch
    X1_br1 = 0.10 + 0.175 # 0.275
    X0_br1 = 0.175        # 0.175

    # G2 + T2 branch
    X1_br2 = 0.15 * (1000.0 / 800.0) + 0.16 * (1000.0 / 800.0) # 0.1875 + 0.20 = 0.3875
    # X0_br2 = infinity

    # Transmission line (1500 MVA base -> 1000 MVA)
    X1_line = 0.15 * (1000.0 / 1500.0) # 0.10
    X0_line = 0.40 * (1000.0 / 1500.0) # 0.26667 (4/15)

    # Parallel at HV Bus
    X1_bus = (X1_br1 * X1_br2) / (X1_br1 + X1_br2)
    Z_th1 = 1j * (X1_bus + X1_line)
    Z_th2 = Z_th1
    Z_th0 = 1j * (X0_br1 + X0_line)

    print(f"Z_th1 = {Z_th1.imag:.5f}j pu")
    print(f"Z_th0 = {Z_th0.imag:.5f}j pu")

    # Part 1: 3-Phase Fault at P, find G1 phase C current
    If1 = Vf / Z_th1 # in pu
    I_br1 = If1 * (X1_br2 / (X1_br1 + X1_br2))
    # Y-Delta phase shift (LV lags HV by 30 deg for positive sequence)
    Ia1_G1 = I_br1 * cmath.rect(1.0, math.radians(-30))
    # Phase C is 'a' * Ia1 = Ia1 * exp(+j120 deg)
    Ic_G1 = Ia1_G1 * cmath.rect(1.0, math.radians(120))
    
    I_base_G1 = 1000.0 / (math.sqrt(3) * V_base_G1) # in kA
    Ic_G1_actual = abs(Ic_G1) * I_base_G1

    print("\n--- Part 1: 3-Phase Fault ---")
    print(f"If1 at P = {abs(If1):.4f} pu")
    print(f"I_br1 (HV side) = {abs(I_br1):.4f} pu")
    print(f"Ic_G1 (pu) = {abs(Ic_G1):.4f} < {math.degrees(cmath.phase(Ic_G1)):.2f} deg pu")
    print(f"G1 base current = {I_base_G1:.3f} kA")
    print(f"Ic_G1 (actual) = {Ic_G1_actual:.2f} kA")

    # Part 2: L-L Fault (B-C) at P, find Phase B current at P
    Ia1_LL = Vf / (Z_th1 + Z_th2) # Ia1 = -j * ...
    Ib_LL = -1j * math.sqrt(3) * Ia1_LL
    I_base_line = 1000.0 / (math.sqrt(3) * 500.0) # in kA
    Ib_LL_actual = abs(Ib_LL) * I_base_line

    print("\n--- Part 2: Line-to-Line Fault (B-C) ---")
    print(f"Ia1 = {abs(Ia1_LL):.4f} < {math.degrees(cmath.phase(Ia1_LL)):.2f} deg pu")
    print(f"Ib_fault = {abs(Ib_LL):.4f} < {math.degrees(cmath.phase(Ib_LL)):.2f} deg pu")
    print(f"Line base current = {I_base_line:.4f} kA")
    print(f"Ib_fault (actual) = {Ib_LL_actual:.3f} kA")
    print("="*60)

if __name__ == '__main__':
    audit_108_q2()
    audit_108_q3()
