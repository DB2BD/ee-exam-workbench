"""EE-111-06-3: cogeneration plant, subtransient 3-phase fault at F and breaker A current.

Stem givens: G 25 MW 22.8 kV Xd''=12 %; each motor 6000 kW 3.3 kV Xd''=15 % (Xd'=25 %);
T 25 MVA 22.8/3.3 kV X=8 %; base 25 MVA, 22.8/3.3 kV; diagram: G-T-A-bus with three M branches,
F on the middle motor feeder.  Rating conversions MW->MVA are not in the stem:
reference-book convention PF_G = 1 and motor eta*pf = 1 (named constants) is the main branch.
"""
import numpy as np

SB, VB_LV = 25.0, 3.3
XG_PU_OWN, XT = 0.12, 0.08
XM_PU_OWN = 0.15
N_M = 3
PF_G = 1.0               # 25 MW treated as 25 MVA (reference-book convention)
K_M = 1.0                # 6000 kW treated as 6000 kVA

IB = SB / (np.sqrt(3) * VB_LV)          # kA
xg = XG_PU_OWN * SB / (25 / PF_G)
xm = XM_PU_OWN * SB / (6 / K_M)
assert abs(IB - 4.373866) < 1e-6 and abs(xm - 0.625) < 1e-12

# nodal analysis: bus node with sources behind reactances, fault at bus (F is on a zero-impedance feeder)
# Thevenin: all EMFs 1 pu; fault current = sum of branch currents
y = np.array([1 / (xg + XT)] + [1 / xm] * N_M)
i_f = y.sum() * IB
i_a = y[0] * IB
assert abs(i_f - 42.86) / 42.86 < 0.005    # boxed 42.86 kA (book 42.83)
assert abs(i_a - 21.87) / 21.87 < 0.005    # boxed 21.87 kA (book 21.85)
assert abs(i_a - 21.8693) < 5e-5
# independent: superposition with prefault V=1 at bus, Zth = (xg+xt) || xm/3
zth = 1 / (1 / (xg + XT) + N_M / xm)
assert abs(IB / zth - i_f) < 1e-9
# breaker A sees only the generator contribution (motor in-feed flows bus -> F, not through A)
v_bus_during = 0.0
assert abs((1 - v_bus_during) / (xg + XT) * IB - i_a) < 1e-12
# PF_G sensitivity listed in 「條件與疑義」
for pf, ka in ((0.9, 23.2652), (0.8, 24.8515)):
    assert abs(IB / (XG_PU_OWN * pf + XT) - ka) < 5e-5
print("PASS EE-111-06-3")
