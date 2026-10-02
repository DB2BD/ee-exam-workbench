"""EE-112-06-4: LV three-phase fault current and inverse-time relay k value."""
import math
import sympy as sp

Sb = 750e3
X = Sb / 500e6 + 0.057
IF = Sb / (math.sqrt(3) * 380) / X
# ohmic check
Zs = 380**2 / 500e6; Zt = 0.057 * 380**2 / Sb
assert abs(IF - 380 / (math.sqrt(3) * (Zs + Zt))) < 1e-6
assert abs(IF - 19478.754) < 1e-3
IFH = IF * 380 / 11400
Is = 1.35 * Sb / (math.sqrt(3) * 11400)
ratio = IFH / Is
k = sp.symbols("k")
ks = float(sp.solve(sp.Eq(k * 80 / (ratio**2 - 1) / 0.808, 0.3), k)[0])
assert abs(ratio**2 - 1 - 159.3321923) < 1e-6
assert abs(ks - 0.4827765) < 1e-6 and round(ks, 2) == 0.48
print("PASS EE-112-06-4")
