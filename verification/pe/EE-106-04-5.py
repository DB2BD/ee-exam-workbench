"""EE-106-04-5: 9 kVA, 208 V, Y 3-phase synchronous generator, Ra = 0.1 ohm/phase, Xs = 5.6 ohm/phase.
Voltage regulation at full load, pf 0.8 lagging and 0.8 leading (terminal voltage held at rated)."""
import numpy as np
S, VL, Ra, Xs = 9e3, 208.0, 0.1, 5.6
Vph = VL / np.sqrt(3)
Ia = S / (np.sqrt(3) * VL)
assert abs(Ia - 24.98) < 0.01
Zs = Ra + 1j * Xs
res = {}
for name, sign in (("lag", -1), ("lead", +1)):
    I = Ia * (0.8 + sign * 0.6j)
    E = Vph + I * Zs
    res[name] = (abs(E) - Vph) / Vph * 100
# phasor-free cross-check with the scalar quadrature formula
for name, sg in (("lag", +1), ("lead", -1)):
    E = np.hypot(Vph + Ia * (Ra * 0.8 + sg * Xs * 0.6), Ia * (Xs * 0.8 - sg * Ra * 0.6))
    assert abs((E - Vph) / Vph * 100 - res[name]) < 1e-9
assert abs(res["lag"] - 94.65) / 94.65 <= 0.005
assert abs(res["lead"] - (-0.36)) / 0.36 <= 0.05
print(f"VR lag={res['lag']:.3f}% lead={res['lead']:.3f}%")
print("PASS EE-106-04-5")
