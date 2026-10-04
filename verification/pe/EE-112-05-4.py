"""EE-112-05-4 independent check: critical clearing angle by equal-area criterion.

Givens (official crop): 60 Hz, H = 5, X'd = 0.2, Xt = 0.2, two parallel lines 0.2 each,
Pe = 0.8, Q = 0.074 delivered to infinite bus V = 1; three-phase fault at sending
end F of line 2 through 0.01 pu; after clearing the line recloses to original state.
"""
import numpy as np

V = 1.0
I = np.conj((0.8 + 0.074j) / V)
E = V + 1j * 0.5 * I
Em, d0 = abs(E), np.angle(E)
Pm, Pmax = 0.8, abs(E) * V / 0.5


def fault_power(Zf):
    """Electrical output during fault from nodal solution at bus 1."""
    yg, yL, yf = 1 / 0.4j, 2 / 0.2j, 1 / Zf
    def P(d):
        Ep = Em * np.exp(1j * d)
        V1 = (yg * Ep + yL * V) / (yg + yL + yf)
        return (Ep * np.conj((Ep - V1) * yg)).real
    return P


def quad(f, a, b, n=20001):
    x = np.linspace(a, b, n)
    y = np.array([f(t) for t in x])
    return (np.sum(y) - 0.5 * (y[0] + y[-1])) * (x[1] - x[0]), 0.0


def brentq(f, lo, hi):
    flo = f(lo)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def critical_angle(P_fault):
    du = np.pi - d0
    def residual(dc):
        a1 = quad(lambda d: Pm - P_fault(d), d0, dc)[0]
        a2 = quad(lambda d: Pmax * np.sin(d) - Pm, dc, du)[0]
        return a1 - a2
    return brentq(residual, d0 + 1e-6, du - 1e-6)


dc_main = np.degrees(critical_angle(fault_power(0.01j)))
dc_real = np.degrees(critical_angle(fault_power(0.01)))
assert abs(np.degrees(d0) - 21.093) / 21.093 <= 0.005
assert abs(Pmax - 2.2229) / 2.2229 <= 0.005
assert abs(fault_power(0.01j)(np.pi / 2) - 0.24699) / 0.24699 <= 0.005
assert abs(dc_main - 101.0936492) / 101.09 <= 0.005
assert abs(dc_real - 102.0837294) / 102.08 <= 0.005

# Closed-form check for the reactive-fault branch (pure sine curves).
P2 = Em * V / ((0.4 * 0.1 + 0.1 * 0.01 + 0.01 * 0.4) / 0.01)
du = np.pi - d0
cos_dc = (Pm * (du - d0) + Pmax * np.cos(du) - P2 * np.cos(d0)) / (Pmax - P2)
assert abs(np.degrees(np.arccos(cos_dc)) - dc_main) < 1e-6
print("PASS EE-112-05-4")
