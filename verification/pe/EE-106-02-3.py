"""EE-106-02-3 independent check: BJT CE amplifier, high-frequency 3-dB point.

Givens (official crop): +5 V / -5 V supplies; base divider 20 k (to +5 V) and 20 k (to -5 V); RE = 5 k to -5 V (bypassed by an infinite capacitor);
RC = 2.5 k to +5 V; coupling capacitors infinite; RL = 5 k; source 1 k; beta = 100, VBE(on) = 0.7 V, VA = infinity,
Cpi = 25 pF, Cmu = 3 pF.   Assumed (not given): thermal voltage VT = 25 mV.
Method: Thevenin bias -> IC; hybrid-pi: gm, r_pi; Miller input capacitance; dominant input pole, output pole as a check.
"""
import math


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


beta, VBE, VT = 100, 0.7, 0.025
RB1 = RB2 = 20e3
VTH = -5 + 10 * RB2 / (RB1 + RB2)          # divider between +5 and -5
RTH = RB1 * RB2 / (RB1 + RB2)
RE, RC, RL, Rs = 5e3, 2.5e3, 5e3, 1e3
IB = (VTH - VBE - (-5)) / (RTH + (beta + 1) * RE)
IC = beta * IB
IE = (beta + 1) * IB
assert abs(VTH) < 1e-12 and close(RTH, 10e3) and close(IC * 1e3, 0.8350)
# KVL cross-check: base loop
assert abs(VTH - IB * RTH - VBE - IE * RE + 5) < 1e-9
VCE = (5 - IC * RC) - (-5 + IE * RE)
assert VCE > 0.3                             # active region

gm = IC / VT
rpi = beta / gm
RLp = RC * RL / (RC + RL)
Cmu, Cpi = 3e-12, 25e-12
CM = Cmu * (1 + gm * RLp)
Rs_eq = Rs * RTH / (Rs + RTH)                # source with the bias divider as seen from the base node
Rin = Rs_eq * rpi / (Rs_eq + rpi)
fH = 1 / (2 * math.pi * Rin * (Cpi + CM))
assert close(gm * 1e3, 33.4) and close(rpi, 2994) and close(RLp, 1666.7)
assert close(CM * 1e12, 170.0) and close(Rin, 697.9) and close(fH / 1e6, 1.17)
# output-side Miller pole as a check (much higher)
CMo = Cmu * (1 + 1 / (gm * RLp))
fo = 1 / (2 * math.pi * RLp * CMo)
assert fo > 20 * fH and close(fo / 1e6, 31.3)
# exact two-pole check: solve the small-signal nodal equations at the -3 dB point of the input-pole-only model is not exact;
# instead compare to |H(jw)| of the full Cmu-bridged model numerically
import numpy as np


def H(w):
    s = 1j * w
    gs = 1 / Rs
    # nodes: b (base), c (collector).  Vs = 1.  Rs to source, RTH is part of Thevenin: use Thevenin source (Vs*RTH/(Rs+RTH)) with Rs_eq
    Vth = RTH / (Rs + RTH)
    G1 = 1 / Rs_eq
    Y = np.array([[G1 + 1 / rpi + s * (Cpi + Cmu), -s * Cmu],
                  [gm - s * Cmu, 1 / RLp + s * Cmu]], dtype=complex)
    b = np.array([Vth * G1, 0], dtype=complex)
    v = np.linalg.solve(Y, b)
    return v[1]


w = np.logspace(5, 10, 60001)
mag = np.array([abs(H(x)) for x in w])
mid = abs(H(1e3))
w3 = w[np.argmax(mag < mid / math.sqrt(2))]
f3_full = w3 / (2 * math.pi)
assert abs(f3_full - fH) / fH < 0.05, (f3_full, fH)
print(f"IC={IC*1e3:.4f} mA gm={gm*1e3:.2f} mS rpi={rpi:.0f} CM={CM*1e12:.1f} pF fH={fH/1e6:.3f} MHz (full-model -3 dB {f3_full/1e6:.3f} MHz)")
print("PASS EE-106-02-3")
