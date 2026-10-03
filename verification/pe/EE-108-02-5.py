"""EE-108-02-5 independent check: three-phase interleaved buck converter.

Givens (official crop): Vs = 9 V, RL = 1 ohm, fs = 20 kHz, D = 1/6, only S1 operating -> V_L = 3 V (as printed),
single-phase current ripple < 0.5 A with the smallest L; S1,S2,S3 pulses of width T/6 spaced T/3 apart.
Method: inductor slopes in each state, sum of the three phase currents on a fine time grid.
Note: ideal buck would give D*Vs = 1.5 V; the printed V_L = 3 V is used as the primary datum, the 1.5 V reading is
checked as an alternative branch.
"""
import numpy as np
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


Vs, D, fs, RL, dI_max = 9, sp.Rational(1, 6), 20_000, 1, sp.Rational(1, 2)
T = sp.Rational(1, fs)
VL = 3

# primary: on-interval rise of one inductor = (Vs - VL) D T / L <= 0.5 A
L_min = (Vs - VL) * D * T / dI_max
assert close(L_min * 1e6, 100)
f_ripple = 3 * fs
assert f_ripple == 60_000

Lv = float(L_min)
Tf = float(T)
n = 60_000
t = np.linspace(0, Tf, n, endpoint=False)
dt = t[1] - t[0]


def gate(phase_shift):
    ph = np.mod(t - phase_shift * Tf / 3, Tf)
    return ph < Tf / 6


def total_slope(vl, L):
    s = np.zeros_like(t)
    for k in range(3):
        on = gate(k)
        s += np.where(on, (Vs - vl) / L, -vl / L)
    return s


sl = total_slope(VL, Lv)
# exactly one switch on -> total slope 0 ; none on -> -9/L
vals = sorted(set(np.round(sl * Lv, 9)))
assert vals == [-9.0, 0.0], vals
t_fall = np.count_nonzero(np.isclose(sl * Lv, -9.0)) * dt
assert abs(t_fall - Tf / 2) < 3 * dt   # three falling segments of T/6 per switching period
dI_tot = 9 / Lv * (Tf / 6)
assert close(dI_tot, 0.75)
Iavg = VL / RL
Imax, Imin = Iavg + dI_tot / 2, Iavg - dI_tot / 2
assert close(Imax, 3.375) and close(Imin, 2.625)
# single-phase check with the smallest L
assert close((Vs - VL) / Lv * Tf / 6, 0.5)

# alternative branches (reported in the note, not the primary answer)
L_off = VL * (1 - D) * T / dI_max                     # off-interval formula with V_L = 3 V
assert close(float(L_off) * 1e6, 250)
VL2 = float(D) * Vs                                   # ideal buck: 1.5 V
L_alt = (Vs - VL2) * float(D) * Tf / 0.5
assert close(L_alt * 1e6, 125)
sl2 = total_slope(VL2, L_alt)
vals2 = sorted(set(np.round(sl2 * L_alt, 9)))
assert vals2 == [-4.5, 4.5], vals2
assert abs(np.sum(sl2) * dt) < 1e-3 * 4.5 / L_alt * Tf / 2   # periodic: zero net change
dI_alt = 4.5 / L_alt * Tf / 6
assert close(dI_alt, 0.3)
# net change of the total current per T/3 at the stated V_L = 3 V (no periodic steady state) vs the self-consistent 1.5 V
net_stated = float(np.sum(sl) * dt) / 3
assert close(net_stated, -0.75), net_stated
assert close(float(D) * Vs, 1.5) and abs((Vs - 1.5) * float(D) - 1.5 * (1 - float(D))) < 1e-12
assert abs((Vs - VL) * float(D) - VL * (1 - float(D))) > 1
assert close(1.5 + dI_alt / 2, 1.65) and close(1.5 - dI_alt / 2, 1.35)
print(f"L={Lv*1e6:.3f} uH, dI_tot={dI_tot:.4f} A, Imax={Imax:.4f}, Imin={Imin:.4f}; alt L_off={float(L_off)*1e6:.1f} uH, "
      f"alt L={L_alt*1e6:.1f} uH dI={dI_alt:.3f} A")
print("PASS EE-108-02-5")
