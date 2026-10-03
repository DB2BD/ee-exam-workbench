"""EE-110-02-4 independent check: full-bridge square-wave inverter, RL load.

Givens (official crop): R = 12 ohm, L = 10 mH, f = 300 Hz, fundamental load current 6 Arms.
Method: Vdc from the fundamental of a +/-Vdc square wave (Fourier projection by SymPy);
THD from the exact periodic steady-state current (closed-form exponential segments, rms by
integration): THD = sqrt(Irms^2 - I1^2) / I1.  Cross-check with the odd-harmonic sum.
"""
import numpy as np
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


R, L, f, I1 = 12.0, 10e-3, 300.0, 6.0
w = 2 * np.pi * f
th = sp.symbols("theta")
# fundamental peak of a unit square wave by projection
b1 = float(2 / (2 * sp.pi) * (sp.integrate(sp.sin(th), (th, 0, sp.pi)) - sp.integrate(sp.sin(th), (th, sp.pi, 2 * sp.pi))))
Z1 = np.hypot(R, w * L)
Vdc = I1 * np.sqrt(2) * Z1 / b1

# exact steady state: on 0<t<T/2, v = +Vdc: i = Vdc/R + (Imin - Vdc/R) e^{-t/tau}, Imin = -Imax
tau, T = L / R, 1 / f
a = np.exp(-(T / 2) / tau)
Imax = (Vdc / R) * (1 - a) / (1 + a)
t = sp.symbols("t")
i_t = Vdc / R + (-Imax - Vdc / R) * sp.exp(-t / tau)
assert abs(float(i_t.subs(t, T / 2)) - Imax) < 1e-9
Irms = np.sqrt(float(sp.Integral(i_t**2, (t, 0, T / 2)).evalf()) / (T / 2))
THD = np.sqrt(Irms**2 - I1**2) / I1
# harmonic sum cross-check
n = np.arange(3, 400001, 2)
Ih = (4 * Vdc / (n * np.pi) / np.sqrt(2)) / np.hypot(R, n * w * L)
THD_sum = np.sqrt(np.sum(Ih**2)) / I1
assert close(THD, THD_sum)
assert close(Vdc, 148.92) and close(THD * 100, 14.08)
print(f"Z1={Z1:.4f} Vdc={Vdc:.4f} V Irms={Irms:.6f} A THD={THD*100:.4f}% (sum {THD_sum*100:.4f}%) Imax={Imax:.4f}")
print("PASS EE-110-02-4")
