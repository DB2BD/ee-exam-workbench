"""EE-106-04-3: 200 V shunt DC motor, Rf = 200 ohm, Ra = 0.5 ohm; no load 1000 rpm, If = 1 A, Ia = 4 A;
external load 100 N-m; no saturation, no armature reaction.
Rotational-loss model is NOT given -> two explicit branches (needs_manual_review)."""
import math
Vt, Ra, n0, Ia0, TL = 200.0, 0.5, 1000.0, 4.0, 100.0
assert Vt / 200.0 == 1.0                       # field current 1 A consistent with the stem
Ea0 = Vt - Ia0 * Ra
w0 = 2 * math.pi * n0 / 60
Kphi = Ea0 / w0
# branch A: loss torque constant (no-load electromagnetic torque Kphi*Ia0 stays), Te = TL + Kphi*Ia0
IaA = Ia0 + TL / Kphi
EaA = Vt - IaA * Ra
nA = n0 * EaA / Ea0
assert abs(IaA - 56.89) / 56.89 <= 0.005 and abs(nA - 866.4) / 866.4 <= 0.005
# branch B: rotational loss neglected, Te = 100 N-m
IaB = TL / Kphi
EaB = Vt - IaB * Ra
nB = n0 * EaB / Ea0
assert abs(IaB - 52.89) / 52.89 <= 0.005 and abs(nB - 876.5) / 876.5 <= 0.005
# independent: solve the motor torque-speed line  w = (Vt - Ra*Te/Kphi)/Kphi  for each torque demand
for Te, n_expect in ((TL + Kphi * Ia0, nA), (TL, nB)):
    w = (Vt - Ra * Te / Kphi) / Kphi
    assert abs(w * 60 / (2 * math.pi) - n_expect) < 1e-9
# branch A also reproduces the stem's no-load point exactly
assert abs((Vt - Ra * Ia0) / Kphi * 60 / (2 * math.pi) - n0) < 1e-9
print(f"Kphi={Kphi:.7f} A: Ia={IaA:.4f} n={nA:.3f} | B: Ia={IaB:.4f} n={nB:.3f}")
print("PASS EE-106-04-3")
