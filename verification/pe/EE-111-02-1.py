"""EE-111-02-1 independent check: single-phase diode bridge, series RL load.

Givens (official crop): Vm = 100 V, f = 60 Hz, R = 10 ohm, L = 12 mH,
vo = Vo + sum_{n=2,4,...} Vn cos(n w t + pi), Vn = Vo (1/(n-1) - 1/(n+1)).
Method: (1) Vo from the average of |Vm sin|; (2) harmonic currents from |Z_n|;
(3) load power from the exact periodic time-domain current (ODE closed form,
numerically integrated with SymPy), cross-checked by the Fourier power sum;
(4) PF = P / (Vs,rms * Is,rms) with Is,rms = Io,rms for an ideal bridge.
"""
import sympy as sp
import numpy as np


def close(x, y, tol=0.005):
    return abs(float(x) - y) / abs(y) <= tol


Vm, f, R, L = 100.0, 60.0, 10.0, 12e-3
w = 2 * np.pi * f
th = sp.symbols("theta", real=True)

# (1) Vo = average of |Vm sin|, computed by integration (not by formula recall)
Vo = float(sp.integrate(Vm * sp.sin(th), (th, 0, sp.pi)) / sp.pi)
# check the Fourier coefficient given in the stem against a direct projection
for n in (2, 4):
    an = float(sp.integrate(Vm * sp.sin(th) * sp.cos(n * th), (th, 0, sp.pi)) * 2 / sp.pi)
    assert close(abs(an), Vo * (1 / (n - 1) - 1 / (n + 1)), 1e-9) and an < 0  # cos(n wt + pi)

# (2) harmonic current amplitudes
def In(n):
    Vn = Vo * (1 / (n - 1) - 1 / (n + 1))
    return Vn / np.hypot(R, n * w * L)

I0, I2, I4 = Vo / R, In(2), In(4)

# (3) exact periodic current on one half cycle: i = (Vm/Z) sin(th - phi) + K exp(-th/(wL/R))
Z, phi, wt = np.hypot(R, w * L), np.arctan2(w * L, R), w * L / R
# periodicity i(0) = i(pi): (Vm/Z) sin(-phi) + K = (Vm/Z) sin(pi - phi) + K e^{-pi/wt}
K = (Vm / Z) * (np.sin(np.pi - phi) - np.sin(-phi)) / (1 - np.exp(-np.pi / wt))
i_expr = (Vm / Z) * sp.sin(th - phi) + K * sp.exp(-th / wt)
assert float(i_expr.subs(th, 0)) > 0  # continuous conduction, so vo is the full-wave sine
Irms2 = float(sp.Integral(i_expr**2, (th, 0, sp.pi)).evalf() / sp.pi)
P = R * Irms2
# Fourier cross-check (truncated far out)
n = np.arange(2, 200001, 2)
P_fourier = R * (I0**2 + 0.5 * np.sum((2 * Vo / (n**2 - 1) / np.hypot(R, n * w * L)) ** 2))
assert close(P, P_fourier, 1e-6)
P_024 = R * (I0**2 + (I2**2 + I4**2) / 2)

# (4) power factor
PF = P / ((Vm / np.sqrt(2)) * np.sqrt(Irms2))

assert close(Vo, 63.662)
assert close(I2, 3.147) and close(I4, 0.4106)
assert close(P, 455.75) and close(P_024, 455.65)
assert close(PF, 0.9547)
print(f"Vo={Vo:.6f} I0={I0:.6f} I2={I2:.6f} I4={I4:.6f} P={P:.4f} P024={P_024:.4f} PF={PF:.6f}")
print("PASS EE-111-02-1")
