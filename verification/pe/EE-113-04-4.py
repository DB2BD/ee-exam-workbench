"""EE-113-04-4: 220 V, 60 Hz, 1120 rpm 3-phase IM, per-phase circuit of the crop:
Z1 = 0.1 + j0.25, X2 = j0.35, rotor 0.2/s (figure), Rc = 60 || Xm = j15.
The hint text says the mechanical load resistance is 0.1(1-s)/s (conflict).
Branch A (main): R2 = 0.2 (figure).  Branch B: R2 = 0.1 (hint).  Also the
reference book's mixed convention (I from 0.2/s, P from 0.1(1-s)/s)."""
import numpy as np

V = 220 / np.sqrt(3)
ns = 1200.0                       # 6 poles: largest sync speed above 1120 rpm
s = (ns - 1120) / ns
ws = 2 * np.pi * ns / 60
Z1, X2 = 0.1 + 0.25j, 0.35j
Zm = 1 / (1 / 60 + 1 / 15j)

def branch(R2):
    Zr = lambda sl: R2 / sl + X2
    Ist = abs(V / (Z1 + Zr(1)))
    I = V / (Z1 + Zr(s))
    pf = np.cos(np.angle(Z1 + Zr(s)))
    Pin = 3 * (V * np.conj(I)).real
    Pmech = 3 * abs(I) ** 2 * R2 * (1 - s) / s
    T = Pmech / ((1 - s) * ws)
    smax = R2 / abs(Z1.real + 1j * (Z1.imag + X2.imag))
    Imax = abs(V / (Z1 + Zr(smax)))
    Istm = abs(V / (Z1 + 1 / (1 / Zm + 1 / Zr(1))))
    # independent torque: T = 3 I^2 R2/s / ws (air-gap power over sync speed)
    assert abs(T - 3 * abs(I) ** 2 * R2 / s / ws) < 1e-9
    return dict(Ist=Ist, I=abs(I), pf=pf, T=T, eta=Pmech / Pin, smax=smax, Imax=Imax, Istm=Istm)

A, B = branch(0.2), branch(0.1)
ref = dict(Ist=189.346, I=40.2267, pf=0.981780, T=115.894, eta=0.903226, smax=0.328798, Imax=136.834, Istm=192.301)
for k, v in ref.items():
    assert abs(A[k] - v) / v <= 0.005, (k, A[k])
refB = dict(Ist=200.832, I=74.331, pf=0.936329, T=197.854, eta=0.875, smax=0.164399, Imax=136.834, Istm=203.69)
for k, v in refB.items():
    assert abs(B[k] - v) / v <= 0.005, (k, B[k])
# reference-book mixed convention: current from 0.2/s, power from 0.1(1-s)/s, s=0.067
Pm_book = 3 * 40.23**2 * 0.1 * (1 - 0.067) / 0.067
T_book = Pm_book / ((1 - 0.067) * ws)
assert abs(Pm_book - 6761.3) / 6761.3 <= 0.005 and abs(T_book - 57.67) / 57.67 <= 0.005
# the mixed convention violates P_ag = P_cu2 + P_mech (branch A air-gap power)
Pag = 3 * A["I"] ** 2 * 0.2 / s
assert Pag - 3 * A["I"] ** 2 * 0.2 - Pm_book > 6000
print({k: round(v, 4) for k, v in A.items()})
print({k: round(v, 4) for k, v in B.items()})
print("PASS EE-113-04-4")
