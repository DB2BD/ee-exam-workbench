"""EE-105-02-5 independent check (descriptive question, numeric support only).

Question: compare half-wave vs full-wave rectifiers, and half-bridge (center-tapped) vs
full-bridge rectifiers; draw circuits.  The script verifies the quantitative claims used in
the answer with an ideal-diode simulation: average and RMS output, ripple frequency, diode
peak inverse voltage and transformer DC component.
"""
import numpy as np

N = 20000
t = np.arange(N) / N * 2 * np.pi * 4  # four cycles
Vm = 1.0
vs = Vm * np.sin(t)
hw = np.maximum(vs, 0)
fw = np.abs(vs)


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


assert close(hw.mean(), 1 / np.pi) and close(fw.mean(), 2 / np.pi)
assert close(np.sqrt((hw**2).mean()), 0.5) and close(np.sqrt((fw**2).mean()), 1 / np.sqrt(2))


def ripple_fundamental(x):
    X = np.abs(np.fft.rfft(x - x.mean()))
    return int(np.argmax(X[1:]) + 1) / 4  # multiples of line frequency (4 cycles)

assert ripple_fundamental(hw) == 1 and ripple_fundamental(fw) == 2
# transformer secondary current mean: half-wave has a DC component, full-wave bridge none
i_sec_hw = hw
i_sec_bridge = np.where(vs >= 0, 1, -1) * fw  # alternating-sign current through the secondary
assert abs(i_sec_hw.mean()) > 0.3 and abs(i_sec_bridge.mean()) < 1e-3
# center-tap: each half winding peak Vm, the OFF diode sees the two halves in series: 2 Vm
va, vb = vs, -vs
pc = np.where(va > 0, va, vb)
off_diode_v = np.where(va > 0, vb - pc, va - pc)
assert close(abs(off_diode_v).max(), 2 * Vm, 0.001)
assert close(abs(vs).max(), Vm, 0.001)  # bridge: OFF diode sees at most Vm
# diode leg + capacitor leg (doubler): ideal diodes, no load, caps charge to Vm
c1 = c2 = 0.0
for v in vs:
    c1 = max(c1, v)      # D1 charges C1 on positive peaks
    c2 = max(c2, -v)     # D2 charges C2 on negative peaks
assert close(c1, Vm, 0.001) and close(c2, Vm, 0.001) and close(c1 + c2, 2 * Vm, 0.001)
# half-controlled vs fully-controlled bridge average (continuous current), alpha = 60 deg
al = np.radians(60)
ph = t % (2 * np.pi)
half_ctrl = np.where((ph % np.pi) >= al, abs(vs), 0.0)   # SCR pair fires at alpha, diodes free-wheel/commutate
full_ctrl_avg = 2 * Vm / np.pi * np.cos(al)
half_ctrl_avg = Vm / np.pi * (1 + np.cos(al))
assert close(half_ctrl.mean(), half_ctrl_avg, 0.002)
assert close(half_ctrl_avg, 0.4775, 0.001) and close(full_ctrl_avg, 0.3183, 0.001)
print("PASS EE-105-02-5 (descriptive)")
