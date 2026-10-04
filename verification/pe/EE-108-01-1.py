"""EE-108-01-1 independent check: superposition of the 5 rad/s source and the 6 A dc source.

Givens (official crop): v(t)=12cos5t V in series with 1 ohm and L=1/5 H; then L=1/5 H
in parallel with C=1/10 F; node a to ground has 2 ohm in parallel with a 6 A source
(arrow pointing up into node a). i flows left to right through the 1 ohm resistor.
"""
import numpy as np
import sympy as sp

# --- ac part (w = 5 rad/s) : full nodal solve, nodes n2 (after 1 ohm), n3 (after series L), a
w = 5.0
Zl1 = 1j * w * (1 / 5)
Zpar = 1 / (1 / (1j * w * (1 / 5)) + 1j * w * (1 / 10))
Y = np.zeros((3, 3), dtype=complex)
def stamp(i, j, y):
    Y[i, i] += y
    if j is not None:
        Y[j, j] += y
        Y[i, j] -= y
        Y[j, i] -= y
Vs = 12.0
# source node is known: n2 connected to Vs through 1 ohm -> Norton injection
stamp(0, None, 1.0)               # 1 ohm n2-source
stamp(0, 1, 1 / Zl1)              # series inductor n2-n3
stamp(1, 2, 1 / Zpar)             # parallel L||C n3-a
stamp(2, None, 1 / 2.0)           # 2 ohm a-ground
I_inj = np.array([Vs / 1.0, 0, 0], dtype=complex)
V = np.linalg.solve(Y, I_inj)
I_ac = (Vs - V[0]) / 1.0
assert abs(abs(I_ac) - 2 * np.sqrt(2)) / (2 * np.sqrt(2)) < 5e-3
assert abs(np.degrees(np.angle(I_ac)) + 45) < 0.05

# --- dc part: L short, C open, source 0 V, 6 A into a, 2 ohm and (1 ohm path) in parallel
Va = sp.symbols("Va")
sol = sp.solve(sp.Eq(6, Va / 2 + Va / 1), Va)[0]
I_dc = -sol / 1                   # current rightward through the 1 ohm is opposite to Va/1
assert I_dc == -4

# --- power in 1 ohm by numerical averaging over one period
T = 2 * np.pi / 5
t = np.linspace(0, T, 200001)
i = I_dc + abs(I_ac) * np.cos(5 * t + np.angle(I_ac))
integrate = getattr(np, "trapezoid", None) or np.trapz
P = integrate(i**2, t) / T
assert abs(P - 20) / 20 < 5e-3
print("PASS EE-108-01-1")
