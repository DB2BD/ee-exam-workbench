"""EE-104-02-3 independent check: three-phase six-diode bridge, resistive load.

Givens (official crop): 380 V rms line-to-line, R = 30 ohm, ideal diodes; D1/D3/D5 on top
(a, b, c), D4/D6/D2 on the bottom (a, b, c).
Method: sample the three phase voltages over one period; the top node is the maximum phase and
the bottom node the minimum phase; diode and line currents come from the conduction table.
"""
import numpy as np

VLL, R = 380.0, 30.0
Vp = VLL / np.sqrt(3) * np.sqrt(2)
N = 360000
th = (np.arange(N) + 0.5) / N * 2 * np.pi
v = np.stack([Vp * np.sin(th - k * 2 * np.pi / 3) for k in range(3)])
top, bot = v.max(axis=0), v.min(axis=0)
vo = top - bot
io = vo / R
iD_top = np.where(v == top, io, 0.0)        # D1, D3, D5
iD_bot = np.where(v == bot, io, 0.0)        # D4, D6, D2
ia = iD_top[0] - iD_bot[0]                  # line current of phase a
S = np.sqrt(3) * VLL * np.sqrt(np.mean(ia**2))
S_3ph = 3 * (VLL / np.sqrt(3)) * np.sqrt(np.mean(ia**2))


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


Vm = VLL * np.sqrt(2)
assert close(vo.mean(), 3 * Vm / np.pi) and close(vo.mean(), 513.20)
assert close(io.mean(), 17.11, 0.001)
assert close(iD_top[0].mean(), 5.70, 0.001)
assert close(np.sqrt(np.mean(io**2)), 17.121, 0.001)
assert close(np.sqrt(np.mean(iD_top[0] ** 2)), 9.885, 0.001)
assert close(np.sqrt(np.mean(ia**2)), 13.979, 0.001)
assert close(S, 9201, 0.001) and close(S, S_3ph, 1e-9)
# closed form for the pulse integral
irms_cf = Vm / R * np.sqrt(3 / np.pi * (np.pi / 6 + np.sqrt(3) / 4))
assert close(irms_cf, 17.121, 0.001)
print(f"Vo={vo.mean():.2f} Io={io.mean():.3f} IDavg={iD_top[0].mean():.3f} IDrms={np.sqrt(np.mean(iD_top[0]**2)):.3f} Isrms={np.sqrt(np.mean(ia**2)):.3f} S={S:.1f} VA")
print("PASS EE-104-02-3")
