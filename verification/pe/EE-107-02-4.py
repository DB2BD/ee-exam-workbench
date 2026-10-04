"""EE-107-02-4 independent check: Cuk converter.

Givens (official crop): Vs = 10 V, L1 = 200 uH, L2 = 100 uH, C1 = 100 uF, C2 = 200 uF, D = 0.2, f = 20 kHz, Io = 2 A.
Method: average currents from lossless power balance; ripple from capacitor charge on each switch state and inductor slopes.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


Vs, L1, L2 = 10, sp.Rational(200, 10**6), sp.Rational(100, 10**6)
C1, C2 = sp.Rational(100, 10**6), sp.Rational(200, 10**6)
D, f, Io = sp.Rational(1, 5), 20_000, 2
T = sp.Rational(1, f)
Vo = Vs * D / (1 - D)
IL2 = Io
IL1 = Vo * Io / Vs                               # Pin = Po
assert close(Vo, 2.5) and close(IL1, 0.5)
# C1 ripple: during DT it carries IL2 (discharge), during (1-D)T it carries IL1 (charge)
dVC1_on = IL2 * D * T / C1
dVC1_off = IL1 * (1 - D) * T / C1
assert close(dVC1_on, 0.2) and close(dVC1_off, 0.2)
# inductor ripples
dIL1 = Vs * D * T / L1
dIL2 = Vs * D * T / L2
assert close(dIL1, 0.5) and close(dIL2, 1.0)
# C2 carries the triangular ripple of IL2 (load current is DC): dV = dIL2 / (8 f C2)
dVC2 = dIL2 / (8 * f * C2)
assert close(dVC2, 0.03125)
# C2 charge integral check: area of the triangle above the mean = dIL2*T/8
assert close((dIL2 / 2) * (T / 2) / 2 / C2, float(dVC2))
Ip = IL1 + dIL1 / 2 + IL2 + dIL2 / 2
assert close(Ip, 3.25)
print(f"dVC1={float(dVC1_on):.4f} V dVC2={float(dVC2):.5f} V Ip={float(Ip):.3f} A")
print("PASS EE-107-02-4")
