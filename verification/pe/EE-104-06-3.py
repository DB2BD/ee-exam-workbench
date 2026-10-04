"""EE-104-06-3: arc furnace melting-period voltage variation, complex Thevenin divider, Sb = 15 MVA."""
import numpy as np

Sb = 15.0                                  # MVA common base
Zb69, Zb114 = 69**2 / Sb, 11.4**2 / Sb     # ohm
Z_line = 0.43 * (0.131 + 0.405j)           # 430 m of 0.131+j0.405 ohm/km
Z_up = Z_line / Zb69 + 1j * (Sb / 1230 + 0.067 * Sb / 15)
X_down = (0.061 + 0.44) * Sb / 12.5        # furnace-transformer 6.1 % + 44 % below, both on 12.5 MVA

def v_bus(R_ohm):
    Zl = R_ohm / Zb114 + 1j * X_down       # R measured on furnace-transformer primary (11.4 kV)
    I = 1 / (Z_up + Zl)                    # source E = 1 pu
    V = I * Zl
    assert abs(V + I * Z_up - 1) < 1e-12   # KVL
    return abs(V)

v0, v10 = v_bus(0.0), v_bus(10.0)
assert abs(v0 - 0.882892) / 0.882892 < 0.005
assert abs(v10 - 0.971006) / 0.971006 < 0.005
dV = (v10 - v0) * 100
assert abs(dV - 8.8114) / 8.8114 < 0.005
# sanity: neglecting line resistance changes the answer by < 0.02 percentage point
Zup2 = 1j * Z_up.imag
f = lambda R: abs((R / Zb114 + 1j * X_down) / (Zup2 + R / Zb114 + 1j * X_down))
assert abs((f(10) - f(0)) * 100 - dV) < 0.02
Zs_ = 1j * Sb / 1230                          # 69 kV point of common coupling branch
def v_pcc(R):
    Zl = R / Zb114 + 1j * X_down
    return abs(1 - Zs_ / (Z_up + Zl))
assert abs((v_pcc(10) - v_pcc(0)) * 100 - 1.33) < 0.02
Xd2 = 0.44 * Sb / 12.5                        # branch: 44 % already includes furnace leakage
g = lambda R: abs((R / Zb114 + 1j * Xd2) / (Z_up + R / Zb114 + 1j * Xd2))
assert abs((g(10) - g(0)) * 100 - 10.41) < 0.02
print("PASS EE-104-06-3")
