"""EE-108-05-5: power-angle equations before / during / after a line fault.

Generator Xd'=0.2, step-up transformer 0.1, two parallel lines 0.5 each, infinite
bus.  Pe=0.8, |Vt|=|Vinf|=1.0 (generator terminal reading).  3-phase fault at 30 %
of line 1 from the sending end, cleared by opening both ends of that line.
"""
import cmath
import math

import numpy as np

Xd, Xt, Xl = 0.2, 0.1, 0.5
P0, Vinf = 0.8, 1.0


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


def solve_Eprime(Vt_mag, x_after_vt):
    """Vt at distance x_after_vt (reactance) from the infinite bus."""
    a = math.asin(P0 * x_after_vt / (Vt_mag * Vinf))
    Vt = Vt_mag * cmath.exp(1j * a)
    I = (Vt - Vinf) / (1j * x_after_vt)
    return Vt, I


# Reading A (main): terminal voltage = generator terminals; remaining reactance 0.1 + 0.25
Vt, I = solve_Eprime(1.0, Xt + Xl / 2)
E = Vt + 1j * Xd * I
close(abs(E), 1.03530, 1e-4)
close(math.degrees(cmath.phase(E)), 25.151, 1e-3)
P1 = abs(E) * Vinf / (Xd + Xt + Xl / 2)

# during fault: Y-Delta elimination of the faulted node (fault at 0.3 from sending end)
# network: E'--(0.3)--A, A--(0.15)--ground (faulted node), A--(0.5 line 2)--B(inf)
Xea = Xd + Xt
Xaf = 0.3 * Xl
X2 = Xea + Xl + Xea * Xl / Xaf
# independent: nodal reduction (Kron) of E', A, B with the fault shunt at A
y = lambda x: 1 / (1j * x)
Yf = np.zeros((3, 3), complex)  # nodes: E', A, B
for (i, j, x) in [(0, 1, Xea), (1, 2, Xl)]:
    Yf[i, i] += y(x); Yf[j, j] += y(x); Yf[i, j] -= y(x); Yf[j, i] -= y(x)
Yf[1, 1] += y(Xaf)
keep = [0, 2]
Yred = Yf[np.ix_(keep, keep)] - np.outer(Yf[keep, 1], Yf[1, keep]) / Yf[1, 1]
X2_nodal = abs(1 / Yred[0, 1])
close(X2, 1.8, 1e-9)
close(X2_nodal, 1.8, 1e-9)
P2 = abs(E) * Vinf / X2
X3 = Xea + Xl
P3 = abs(E) * Vinf / X3
close(P1, 1.88236, 1e-4)
close(P2, 0.57516, 1e-4)
close(P3, 1.29412, 1e-4)
d0 = math.degrees(math.asin(P0 / P1))
close(d0, 25.151, 1e-3)

# Reading B (Vt taken at the line sending bus): E' = 1.0520
VtB, IB = solve_Eprime(1.0, Xl / 2)
EB = VtB + 1j * (Xd + Xt) * IB
close(abs(EB) / 0.55, 1.9127045, 1e-6)
close(abs(EB) / 1.8, 0.5844375, 1e-6)
close(abs(EB) / 0.8, 1.3149844, 1e-6)
print("PASS EE-108-05-5")
