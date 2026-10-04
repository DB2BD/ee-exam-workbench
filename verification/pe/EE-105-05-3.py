"""EE-105-05-3: SLG fault at terminals of an unloaded generator, neutral reactor 0.32 ohm.

Given (crop): 100 MVA, 20 kV, X''d = X1 = X2 = 20 %, X0 = 5 %, Xn = 0.32 ohm, V = rated.
"""
import math


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


S, V = 100.0, 20.0                     # MVA, kV (line-to-line)
X1 = X2 = 0.20
X0 = 0.05
Xn = 0.32

# --- method A: per unit ---
Zb = V**2 / S                          # ohm
xn = Xn / Zb
close(xn, 0.08, 1e-9)
Zsum = X1 + X2 + X0 + 3 * xn
close(Zsum, 0.69, 1e-9)
If_pu = 3 * 1.0 / Zsum
Ib = S * 1e3 / (math.sqrt(3) * V)      # A
If_A = If_pu * Ib
close(If_pu, 4.3478)
close(If_A, 12551, 1e-3)

# --- method B: actual ohms, phase quantities ---
Vph = V * 1e3 / math.sqrt(3)
Z1 = 0.20 * Zb
Z0 = 0.05 * Zb
Z2 = 0.20 * Zb
Ia1 = Vph / (Z1 + Z2 + Z0 + 3 * Xn)
close(3 * Ia1, If_A, 1e-9)

# neutral current equals fault current; neutral voltage rise
Vn = 3 * Ia1 * Xn
close(Vn, 3 * Ia1 * 0.32, 1e-12)

# the 'X0 = 8 %' value (not in the figure) would give a different answer
If_wrong = 3 / (0.40 + 0.08 + 0.24) * Ib
assert abs(If_wrong - If_A) / If_A > 0.04

print(f"If={If_pu:.4f} pu = {If_A/1e3:.3f} kA")
print("PASS EE-105-05-3")
