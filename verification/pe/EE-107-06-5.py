"""EE-107-06-5: 1200 kVA at pf 0.65 lag, improve to 0.95 lag; 6.6 kV, 60 Hz, delta capacitors."""
import math

S, pf1, pf2 = 1200.0, 0.65, 0.95
V, f = 6600.0, 60.0
P = S * pf1
Q1 = math.sqrt(S**2 - P**2)
Q2 = P * math.tan(math.acos(pf2))
Qc = Q1 - Q2
assert abs(Qc - 655.547) / 655.547 < 5e-4                      # boxed (一)
assert abs(P - 780) < 1e-9
# delta: each phase sees the line voltage, Qc = 3 w C V^2
C = Qc * 1e3 / (3 * 2 * math.pi * f * V**2)
assert abs(C * 1e6 - 13.31) / 13.31 < 5e-4                      # boxed (二)
# back-substitution: compensated pf
S2 = math.hypot(P, Q1 - 3 * 2 * math.pi * f * C * V**2 / 1e3)
assert abs(P / S2 - pf2) < 1e-12
# phase-current route: I_line of the capacitor bank = Qc/(sqrt3 V); phase = line/sqrt3 = V w C
i_line = Qc * 1e3 / (math.sqrt(3) * V)
assert abs(i_line / math.sqrt(3) - V * 2 * math.pi * f * C) < 1e-9
print("PASS EE-107-06-5")
