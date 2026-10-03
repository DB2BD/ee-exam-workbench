"""EE-106-02-4 independent check: half-wave rectifier with freewheeling diode, R-L load, L -> infinity.

Givens (official crop): vs = 340 sin(wt) V, w = 377 rad/s, R = 4 ohm, D1 in series with the source, D2 across the load (cathode to load +).
Method: time-domain numerical average/rms/power with ideal diodes and constant load current (L infinite -> ripple-free).
"""
import numpy as np

Vp, R = 340.0, 4.0
th = np.linspace(0, 2 * np.pi, 2_000_001)
src = Vp * np.sin(th)
vo = np.where(src > 0, src, 0.0)                       # D1 on for positive half, D2 clamps v_o to 0 otherwise
Vavg = np.trapezoid(vo, th) / (2 * np.pi) if hasattr(np, "trapezoid") else np.trapz(vo, th) / (2 * np.pi)
Io = Vavg / R                                          # average inductor voltage is zero
iD1 = np.where(src > 0, Io, 0.0)
iD2 = np.where(src > 0, 0.0, Io)
assert np.allclose(iD1 + iD2, Io)                      # load current continuous (D1 / D2 commutate)
integ = (lambda y: np.trapezoid(y, th)) if hasattr(np, "trapezoid") else (lambda y: np.trapz(y, th))
Is_rms = np.sqrt(integ(iD1**2) / (2 * np.pi))
P = Io**2 * R
Vs_rms = Vp / np.sqrt(2)
S = Vs_rms * Is_rms
PF = P / S
P_src = integ(src * iD1) / (2 * np.pi)                 # real power delivered by the source
for got, exp in ((Vavg, Vp / np.pi), (Io, 27.0563), (Is_rms, 19.1317), (PF, 2 / np.pi), (P, 2928.18), (S, 4599.58)):
    assert abs(got - exp) / abs(exp) <= 0.005, (got, exp)
assert abs(P_src - P) / P < 1e-6                        # power balance source = R I^2
print(f"Vavg={Vavg:.3f} V Io={Io:.4f} A Is_rms={Is_rms:.4f} A P={P:.2f} W S={S:.2f} VA PF={PF:.4f}")
print("PASS EE-106-02-4")
