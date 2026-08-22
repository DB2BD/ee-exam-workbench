#!/usr/bin/env python3
import math

def audit_108_q5():
    P = 0.8
    Vt = 1.0
    Vinf = 1.0
    Xd_prime = 0.20
    XT = 0.10
    XL = 0.50
    H = 5.0
    f = 60.0
    tc_cycles = 4.5
    tc = tc_cycles / f # 0.075 s

    # 1. Pre-fault
    X_ext = XT + (XL / 2.0) # 0.10 + 0.25 = 0.35
    sin_theta_t = (P * X_ext) / (Vt * Vinf) # 0.8 * 0.35 = 0.28
    theta_t = math.asin(sin_theta_t)
    theta_t_deg = math.degrees(theta_t)
    
    # Vt as complex
    Vt_c = complex(Vt * math.cos(theta_t), Vt * math.sin(theta_t))
    I_c = (Vt_c - Vinf) / (1j * X_ext)
    E_prime_c = Vt_c + 1j * Xd_prime * I_c
    
    E_prime = abs(E_prime_c)
    delta_0 = math.atan2(E_prime_c.imag, E_prime_c.real)
    delta_0_deg = math.degrees(delta_0)
    
    X_pre = Xd_prime + XT + (XL / 2.0) # 0.55
    Pmax1 = (E_prime * Vinf) / X_pre

    print(f"E' = {E_prime:.4f} pu, delta_0 = {delta_0_deg:.4f} deg")
    print(f"Pre-fault: Pe1 = {Pmax1:.4f} sin(delta)")

    # 2. During fault (fault at 30% from sending end on line 1)
    # Y-network from Node 3 (sending bus):
    # Z1 = j(Xd' + XT) = j0.30 (to Node 1)
    # Z2 = j0.50 (to Node 2 via healthy line)
    # Z3 = j(0.30 * 0.50) = j0.15 (to ground fault)
    # Transfer impedance Z12 = Z1 + Z2 + (Z1*Z2)/Z3
    Z1 = 0.30
    Z2 = 0.50
    Z3 = 0.15
    X_during = Z1 + Z2 + (Z1 * Z2) / Z3 # 0.30 + 0.50 + 0.15/0.15 = 0.80 + 1.00 = 1.80
    Pmax2 = (E_prime * Vinf) / X_during
    print(f"During-fault: X_during = {X_during:.4f} pu, Pe2 = {Pmax2:.4f} sin(delta)")

    # 3. Post-fault (line 1 disconnected, line 2 remains)
    X_post = Xd_prime + XT + XL # 0.20 + 0.10 + 0.50 = 0.80
    Pmax3 = (E_prime * Vinf) / X_post
    print(f"Post-fault: X_post = {X_post:.4f} pu, Pe3 = {Pmax3:.4f} sin(delta)")

    # 4. Clearing angle delta_c
    M = H / (math.pi * f)
    # At t = 0+, Pe(delta0) = Pmax2 * sin(delta0)
    Pe2_0 = Pmax2 * math.sin(delta_0)
    Pa_0 = P - Pe2_0
    delta_c = delta_0 + (Pa_0 / (2.0 * M)) * (tc**2)
    delta_c_deg = math.degrees(delta_c)
    print(f"M = {M:.5f} MJ*s/rad, Pa(0+) = {Pa_0:.4f} pu")
    print(f"Clearing angle delta_c = {delta_c_deg:.4f} deg (tc = {tc:.4f} s)")

if __name__ == '__main__':
    audit_108_q5()
