"""EE-109-02-1 independent check: BJT saturated switch with overdrive factor 6.

Givens (official crop): RC = 11 ohm, VCC = 200 V, VB = 10 V, VCE(sat) = 1.0 V,
VBE(sat) = 1.5 V, beta_F in [8, 40], ODF = 6.
Method: worst case beta_min guarantees saturation; ODF = IB / IBS. Solve RB from
the base loop with SymPy, then PT = VBE IB + VCE IC; cross-check PT by the
power balance P_sources - P_resistors.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


RC, VCC, VB, VCEs, VBEs, bmin, ODF = 11, 200, 10, 1, sp.Rational(3, 2), 8, 6
ICS = sp.Rational(VCC - VCEs, RC)
IBS = ICS / bmin
IB = ODF * IBS
RB = sp.symbols("RB", positive=True)
RB = sp.solve(sp.Eq(VB, IB * RB + VBEs), RB)[0]
PT = VBEs * IB + VCEs * ICS
# power balance: sources deliver VCC*IC + VB*IB; resistors burn IC^2 RC + IB^2 RB
PT_balance = VCC * ICS + VB * IB - ICS**2 * RC - IB**2 * RB
assert sp.simplify(PT - PT_balance) == 0
# forced beta stays below beta_min, so saturation is guaranteed across 8..40
assert ICS / IB < bmin
assert close(ICS, 18.0909) and close(IB, 13.5682)
assert close(RB, 0.6265) and close(PT, 38.443)
print(f"ICS={float(ICS):.4f} A IB={float(IB):.4f} A RB={float(RB):.5f} ohm PT={float(PT):.4f} W")
print("PASS EE-109-02-1")
