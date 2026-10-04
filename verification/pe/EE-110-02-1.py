"""EE-110-02-1 independent check: collector-feedback bias, Q-point shift 25 C -> 75 C.

Givens (official crop): VCC = 12 V, RB = 100 k (collector to base), RC = 10 k (VCC to collector),
25 C: beta = 100, VBE = 0.7 V; 75 C: beta = 150, VBE = 0.5 V.
Method: solve the two KVL loops (collector loop and base loop) as a linear system for
(IB, IC, VCE) at each temperature; then percentage changes.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


VCC, RB, RC = 12, 100_000, 10_000
IB, IC, VCE = sp.symbols("IB IC VCE")


def qpoint(beta, vbe):
    eqs = [sp.Eq(VCC, (IC + IB) * RC + VCE),   # VCC -> RC (carries IC + IB) -> collector
           sp.Eq(VCE, IB * RB + vbe),          # collector -> RB -> base -> emitter
           sp.Eq(IC, beta * IB)]
    s = sp.solve(eqs, [IB, IC, VCE], dict=True)[0]
    return s[IB], s[IC], s[VCE]


ib1, ic1, vce1 = qpoint(100, sp.Rational(7, 10))
ib2, ic2, vce2 = qpoint(150, sp.Rational(1, 2))
dIC = (ic2 - ic1) / ic1 * 100
dVCE = (vce2 - vce1) / vce1 * 100
assert close(ic1 * 1e3, 1.0180) and close(vce1, 1.7180)
assert close(ic2 * 1e3, 1.0714) and close(vce2, 1.2143)
assert close(dIC, 5.2465) and close(dVCE, -29.3205)
assert vce1 > 0.2 and vce2 > 0.2   # still active region
print(f"25C IC={float(ic1)*1e3:.6f} mA VCE={float(vce1):.6f}; 75C IC={float(ic2)*1e3:.6f} mA VCE={float(vce2):.6f}; "
      f"dIC={float(dIC):.4f}% dVCE={float(dVCE):.4f}%")
print("PASS EE-110-02-1")
