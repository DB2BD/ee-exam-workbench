"""EE-108-02-2 independent check: three-phase triangular-wave rectifier with five diodes.

Givens (official crop): Van, Vbn, Vcn = +-90 V triangular waves, Van rises through 0 V at theta = 0,
Vbn, Vcn lag by 120 and 240 deg.  Figure topology (traced wire by wire):
  top (cathodes to load +):    D1 from a, D2 from c, phase b has NO top diode (open gap);
  bottom (anodes to load -):   D3 from a, D4 from b, D5 from c.
Ideal diodes: load + node = highest of the connected top sources, load - node = lowest source.
"""
import numpy as np


def tri(theta):
    t = np.mod(theta, 360.0)
    return np.where(t <= 90, t, np.where(t <= 270, 180 - t, t - 360))


th = np.arange(0.0, 360.0 + 1e-9, 0.01)
va, vb, vc = tri(th), tri(th - 120), tri(th - 240)
top = np.maximum(va, vc)                          # only D1 (a) and D2 (c) exist on top
bot = np.minimum(np.minimum(va, vb), vc)          # D3 (a), D4 (b), D5 (c)
VL = top - bot
vdc = np.trapezoid(VL, th) / 360.0 if hasattr(np, "trapezoid") else np.trapz(VL, th) / 360.0
assert abs(vdc - 100.0) / 100.0 <= 0.005, vdc

# conduction table at segment midpoints
names_top = {"D1": 0, "D2": 2}
def conducting(theta):
    a, b, c = (float(tri(theta)), float(tri(theta - 120)), float(tri(theta - 240)))
    tp = "D1" if a >= c else "D2"
    bt = {a: "D3", b: "D4", c: "D5"}[min(a, b, c)]
    return tp, bt, max(a, c) - min(a, b, c)

expected = [
    (15, "D2", "D4", 120), (60, "D1", "D4", 120), (120, "D1", "D5", 120), (180, "D1", "D5", 60),
    (240, "D2", "D3", 60), (300, "D2", "D3", 120), (345, "D2", "D4", 120),
]
for theta, tp, bt, v in expected:
    got = conducting(theta)
    assert got[0] == tp and got[1] == bt and abs(got[2] - v) < 1e-6, (theta, got)
# the notch: V_L = 420 - 2 theta on 150..210, 2 theta - 420 on 210..270, zero at 210
assert abs(conducting(210.0)[2]) < 1e-9 and abs(conducting(150.0)[2] - 120) < 1e-9 and abs(conducting(270.0)[2] - 120) < 1e-9
assert abs(float(VL.min())) < 1e-9 and abs(float(VL.max()) - 120) < 1e-9
# a full six-diode bridge would give 120 V flat (the wrong-topology value)
assert abs(120 - vdc) > 10
print(f"Vdc={vdc:.4f} V  VLmin={VL.min():.3f} VLmax={VL.max():.3f}")
print("PASS EE-108-02-2")
