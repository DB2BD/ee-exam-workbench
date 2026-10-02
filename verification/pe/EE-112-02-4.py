"""EE-112-02-4 independent check: half-wave rectifier with freewheeling diode, R-L-Vdc load.

Givens (official crop): vs = 170 sin(377 t) V, R = 10 ohm, Vdc = 24 V, ideal diodes.
The load voltage is the half-wave sine (continuous conduction is checked).
Main method: Fourier series of the half-wave sine, current phasors per harmonic,
peak-to-peak from the summed series, root-find L for delta_io = 1 A.
Cross-check: direct periodic time-domain ODE integration (piecewise exact steps).
"""
import math

import numpy as np


def brentq(f, lo, hi, xtol=1e-7):
    flo = f(lo)
    while hi - lo > xtol:
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2

Vm, w, R, Vdc = 170.0, 377.0, 10.0, 24.0
N = 400
theta = np.linspace(0, 2 * np.pi, 20001)


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


def series_current(L):
    I0 = (Vm / np.pi - Vdc) / R
    i = np.full_like(theta, I0)
    ms = I0 ** 2
    terms = [(1, 0.0, Vm / 2)]  # (n, a_n cos, b_n sin)
    terms += [(2 * k, -2 * Vm / (np.pi * (4 * k * k - 1)), 0.0) for k in range(1, N)]
    for n, a, b in terms:
        z = complex(R, n * w * L)
        # v = a cos + b sin  <-> phasor (a - j b) on e^{j n theta}
        ph = complex(a, -b) / z
        i += (ph * np.exp(1j * n * theta)).real
        ms += abs(ph) ** 2 / 2
    return i, I0, ms


def ptp(L):
    i, _, _ = series_current(L)
    return i.max() - i.min()


L = brentq(lambda x: ptp(x) - 1.0, 0.2, 1.0, xtol=1e-7)
i, I0, ms = series_current(L)
assert i.min() > 0  # continuous conduction: half-wave sine is the load voltage
P_dc = Vdc * I0
P_R = R * ms
assert close(L, 0.4962, 0.001), L
assert close(P_dc, 72.2704, 1e-4), P_dc
assert close(P_R, 91.7538, 1e-3), P_R

# Fundamental-only estimate (delta_io ~= 2 I1) for the conditions section.
L1 = math.sqrt((Vm / 2 / 0.5) ** 2 - R ** 2) / w
assert close(L1, 0.4502), L1
assert ptp(L1) > 1.0  # the fundamental-only L does not meet the 1 A limit

# Independent time-domain check: exact piecewise integration over many cycles.
def simulate(L, steps=20000, cycles=30):
    dt = 2 * np.pi / w / steps
    a = math.exp(-R * dt / L)
    t = 0.0
    x = I0
    ys = []
    for c in range(cycles):
        for k in range(steps):
            v = max(Vm * math.sin(w * t), 0.0) - Vdc
            x = v / R + (x - v / R) * a
            t += dt
            if c == cycles - 1:
                ys.append(x)
    ys = np.array(ys)
    return ys.max() - ys.min(), ys.mean(), (ys ** 2).mean()


p2p, mean, msq = simulate(L)
assert close(p2p, 1.0, 0.003), p2p
assert close(Vdc * mean, P_dc, 0.003)
assert close(R * msq, P_R, 0.003)
print(f"L={L:.5f} H Pdc={P_dc:.4f} W PR={P_R:.4f} W (fundamental-only L={L1:.4f} H, ptp={ptp(L1):.3f} A); ODE ptp={p2p:.5f}")
print("PASS EE-112-02-4")
