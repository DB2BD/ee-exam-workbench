"""EE-105-04-1: +/-10 V square wave (T=1 ms) on L=1 mH, switch closes at the + to - zero crossing, i(0)=0."""
import numpy as np

Vm, T, L = 10.0, 1e-3, 1e-3
t = np.linspace(0, T, 200001)
v = np.where(t < T / 2, -Vm, Vm)          # starts at the + to - crossing, so first half is negative
i = np.cumsum(v) * (t[1] - t[0]) / L       # numerical integral of v/L
i_half = np.interp(T / 2, t, i)
assert abs(i_half - (-5.0)) / 5.0 < 0.005
assert abs(i[-1]) < 0.01                   # returns to 0 at end of period
assert abs(i.min() - (-5.0)) / 5.0 < 0.005 and i.max() < 0.01
# symbolic cross-check of slope magnitude
assert abs(Vm / L - 1e4) < 1e-9
print("PASS EE-105-04-1")
