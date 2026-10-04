"""EE-110-02-3 independent check: half-wave rectifier, resistive load.

Givens (official crop): 110 Vrms, 60 Hz sine, R = 10 ohm, ideal diode (no drop given).
Method: integrate the conduction-interval current with SymPy for average and rms values;
PF = P / (Vs,rms * Is,rms).  Cross-check P by the Fourier route (dc + half-amplitude
fundamental + even harmonics) truncated far out.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


th = sp.symbols("theta")
Vrms, R = 110, 10
Vm = Vrms * sp.sqrt(2)
i = Vm * sp.sin(th) / R                                  # conducts on 0 < theta < pi
I_avg = sp.integrate(i, (th, 0, sp.pi)) / (2 * sp.pi)
I_rms = sp.sqrt(sp.integrate(i**2, (th, 0, sp.pi)) / (2 * sp.pi))
P = I_rms**2 * R
PF = P / (Vrms * I_rms)
# Fourier cross-check: vo = Vm/pi + Vm/2 sin + sum_{n even} -2Vm/(pi (n^2-1)) cos(n th)
Vm_f = float(Vm)
P_f = (Vm_f / sp.pi) ** 2 / R + (Vm_f / 2) ** 2 / (2 * R) + sum(
    (2 * Vm_f / (float(sp.pi) * (n * n - 1))) ** 2 / (2 * R) for n in range(2, 20001, 2))
assert close(P_f, float(P))
assert close(I_avg, 4.952) and close(P, 605) and close(PF, 0.7071)
assert sp.simplify(PF - 1 / sp.sqrt(2)) == 0
print(f"Iavg={float(I_avg):.4f} A P={float(P):.3f} W PF={float(PF):.4f}")
print("PASS EE-110-02-3")
