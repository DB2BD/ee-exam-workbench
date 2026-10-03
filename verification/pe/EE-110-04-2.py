"""EE-110-04-2: 220/160 V, 30 kVA two-winding transformer as 380/220 V step-down auto;
two units in open-delta (V-V) for 3-phase 380 -> 220 V.
"""
import numpy as np

S, VA, VB = 30e3, 220.0, 160.0
assert VA + VB == 380                       # additive series connection
Ise = S / VB                                # series (160 V) winding rated current
Ic = S / VA                                 # common (220 V) winding rated current
IH = Ise
IL = Ise + Ic
S_auto = 380 * IH
assert abs(S_auto - 71.25e3) / 71.25e3 <= 0.005
assert abs(220 * IL - S_auto) < 1e-6        # power balance both sides
assert abs(IL - 323.86) / 323.86 <= 0.005
# conducted vs transformed split
assert abs(S_auto - S - 220 * IH) < 1e-6
# (3)(4) open-delta: phasor check that two autos on AB and CB (common B) give balanced 220 V
a = np.exp(2j * np.pi / 3)
VAn, VBn, VCn = 380 / np.sqrt(3) * np.array([1, a**-1, a**-2])
k = 220 / 380
Va = VBn + k * (VAn - VBn)
Vc = VBn + k * (VCn - VBn)
Vb = VBn
for x, y in ((Va, Vb), (Vb, Vc), (Vc, Va)):
    assert abs(abs(x - y) - 220) < 1e-9
S3 = np.sqrt(3) * 220 * IL                  # line current limited by unit output current
assert abs(S3 - np.sqrt(3) * S_auto) < 1e-6
assert abs(S3 / 1e3 - 123.41) / 123.41 <= 0.005
print(f"S_auto={S_auto/1e3:.2f} kVA IL={IL:.2f} A S3={S3/1e3:.2f} kVA")
print("PASS EE-110-04-2")
