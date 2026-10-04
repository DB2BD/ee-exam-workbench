"""EE-104-04-5: 6.6 kVA, 380 V, 60 Hz, 3-ph 4-pole sync generator, Ra=0, Xs=1.0 ohm/phase.
Step 1: Ef set so 6.6 kW resistive load gets rated 380 V. Step 2: same Ef, load 6.6 kVA 0.8 lagging; find V_L."""
import numpy as np

def brentq(f, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2

Xs, S = 1.0, 6600.0
Vph = 380 / np.sqrt(3)
I_rated = S / (np.sqrt(3) * 380)
Ef = abs(Vph + 1j * Xs * I_rated)           # resistive: I in phase with V
assert abs(Ef - 219.62) / 219.62 < 0.005
ph = np.arccos(0.8)
# (a) load takes 6.6 kVA at 0.8 lag at the actual terminal voltage (constant S)
def fa(V):
    I = S / (3 * V)
    return abs(V + 1j * Xs * I * np.exp(-1j * ph)) - Ef
Va = brentq(fa, 100, 300)
# (b) constant impedance (6.6 kVA at 380 V, 0.8 lag)
ZL = 380**2 / S * np.exp(1j * ph)
Vb = Ef * abs(ZL) / abs(ZL + 1j * Xs)
# (c) current fixed at rated value
def fc(V):
    return abs(V + 1j * Xs * I_rated * np.exp(-1j * ph)) - Ef
Vc = brentq(fc, 100, 300)
VLa, VLb, VLc = (np.sqrt(3) * v for v in (Va, Vb, Vc))
print(f"Ef={Ef:.3f} VL(a)={VLa:.2f} VL(b)={VLb:.2f} VL(c)={VLc:.2f}")
for v in (VLa, VLb, VLc):
    assert abs(v - 370.0) / 370.0 < 0.005
print("PASS EE-104-04-5")
