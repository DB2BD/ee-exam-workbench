"""EE-110-06-5: momentary breaker current at F1 (3.45 kV) with K = 1.6.

Stem givens: S_sc = 1500 MVA; T1 69/3.45 kV 5000 kVA Z 7 %; T2 3.45/0.48 kV 1500 kVA Z 5.75 %;
S/M 2000 HP Xd''=15 %; I/M1 1000 HP Xd''=20 %; I/M2 1500 HP (480 V) Xd''=25 %; K = 1.6.
Motor kVA is not in the stem: reference-book convention 1 HP ~ 1 kVA (named constant).
"""
import numpy as np

SB, VB = 100.0, 3.45
K = 1.6
KVA_PER_HP = 1.0                         # reference-book convention

def fault(mva_of_hp):
    x_src = SB / 1500 + 0.07 * SB / 5
    x_sm = 0.15 * SB / mva_of_hp(2000)
    x_im1 = 0.20 * SB / mva_of_hp(1000)
    x_im2 = 0.0575 * SB / 1.5 + 0.25 * SB / mva_of_hp(1500)
    return (1 / x_src + 1 / x_sm + 1 / x_im1 + 1 / x_im2) * SB / (np.sqrt(3) * VB)

i_sym = fault(lambda hp: KVA_PER_HP * hp / 1000)
assert abs(i_sym - 15.29) / 15.29 < 0.005          # boxed 15.29 kA (book 15.30)
assert abs(K * i_sym - 24.47) / 24.47 < 0.005      # boxed 24.47 kA (book 24.48)
# independent: Thevenin impedance of the parallel network on a 5 MVA base gives the same current
SB5 = 5.0
zs = [SB5 / 1500 + 0.07, 0.15 * SB5 / 2, 0.20 * SB5 / 1, 0.0575 * SB5 / 1.5 + 0.25 * SB5 / 1.5]
zth = 1 / sum(1 / z for z in zs)
assert abs(SB5 / (np.sqrt(3) * VB) / zth - i_sym) < 1e-9
# parameterisation table kept in 「條件與疑義」: S = 0.000746 HP / k
for k, sym, mom in ((0.80, 15.0420, 24.0672), (0.85, 14.8360, 23.7376), (0.90, 14.6522, 23.4435), (1.00, 14.3382, 22.9411)):
    v = fault(lambda hp: 0.000746 * hp / k)
    assert f"{v:.4f}" == f"{sym:.4f}" and f"{K*v:.4f}" == f"{mom:.4f}", (k, v)
print("PASS EE-110-06-5")
