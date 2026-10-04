"""EE-105-04-5: separately excited DC motor, Vt=300 V, Ra=0.1 ohm, Ia=600 A, If=12 A, n=800 rpm.
Half rated torque, Vt=240 V, If=6 A. Flux ratio r unknown (no magnetization curve); linear assumption r=0.5."""
import sympy as sp

Ra, Vt1, Ia1, n1, Vt2 = 0.1, 300.0, 600.0, 800.0, 240.0
Ea1 = Vt1 - Ia1 * Ra
r = sp.symbols("r", positive=True)
Ia2 = 0.5 * Ia1 / r                         # T ~ phi*Ia
Ea2 = Vt2 - Ia2 * Ra
n2 = n1 * (Ea2 / Ea1) / r                   # Ea ~ phi*n
assert abs(Ea1 - 240.0) < 1e-9
assert sp.simplify(n2 - (800 / r - 100 / r**2)) == 0
assert abs(float(n2.subs(r, 0.5)) - 1200.0) / 1200.0 < 0.005
assert abs(float(Ia2.subs(r, 0.5)) - 600.0) < 1e-9
assert abs(float(Ea2.subs(r, 0.5)) - 180.0) < 1e-9
for rv, ia, ea, nn in [(0.45, 666.667, 173.333, 1283.951), (0.55, 545.455, 185.455, 1123.967), (0.60, 500.0, 190.0, 1055.556)]:
    assert abs(float(Ia2.subs(r, rv)) - ia) / ia < 0.005
    assert abs(float(Ea2.subs(r, rv)) - ea) / ea < 0.005
    assert abs(float(n2.subs(r, rv)) - nn) / nn < 0.005
print("PASS EE-105-04-5")
