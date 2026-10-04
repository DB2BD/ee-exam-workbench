"""EE-108-01-2 independent check: full nodal solve of the resistive circuit with dependent sources.

Givens (official crop): nodes A (left, 6 A source arrow points left INTO A, 6 V source +,
1 ohm v1 to ground), B (6 V source -, 4 ohm v to ground, dependent source 4*i1 '-' side),
C (dependent source 4*i1 '+' side, 1 ohm v2 bottom end '-', dependent current source
(3/2)*v2 arrow up into C), T (top right: 6 A source tail, 1 ohm v2 '+', 2 ohm to ground).
i1 arrow on the bottom wire points left, i.e. it flows ground -> up through the 1 ohm
into A, so i1 = -v1.  v2 = Vt - Vc.
"""
import sympy as sp

VA, VB, VC, VT, I6V, I4i = sp.symbols("VA VB VC VT I6V I4i")
v1 = VA
i1 = -v1
v2 = VT - VC
eqs = [
    sp.Eq(VA - VB, 6),                 # 6 V source, + at A
    sp.Eq(VC - VB, 4 * i1),            # 4*i1 source, + toward C
    # node A: 6 A enters from the current source; leaves via 1 ohm to ground and 6 V source (current I6V from A to B)
    sp.Eq(6, VA / 1 + I6V),
    # node B: I6V enters, leaves through 4 ohm and the dependent voltage source (current I4i from B to C)
    sp.Eq(I6V, VB / 4 + I4i),
    # node C: I4i and the 1 ohm current v2 enter, (3/2)v2 enters from the dependent current source; C has no other branch
    sp.Eq(I4i + v2 / 1 + sp.Rational(3, 2) * v2, 0),
    # node T: 6 A leaves via source, v2/1 leaves via 1 ohm, VT/2 leaves via 2 ohm
    sp.Eq(0, 6 + v2 / 1 + VT / 2),
]
sol = sp.solve(eqs, [VA, VB, VC, VT, I6V, I4i], dict=True)[0]
v = sol[VB]
P2 = sol[VT] ** 2 / 2
assert v == -8, v
assert P2 == 8, P2
# global power balance as an extra assertion (sources deliver = resistors absorb)
v2n = (sol[VT] - sol[VC])
absorbed = sol[VA] ** 2 + sol[VB] ** 2 / 4 + v2n**2 + sol[VT] ** 2 / 2
delivered = (
    6 * (sol[VA] - sol[VT])                       # 6 A source: current leaves at A, so A is its + side
    - 6 * sol[I6V]                                # 6 V source absorbs 6*I6V
    + (sol[VC] - sol[VB]) * sol[I4i]              # 4*i1 source: current enters - (B) and leaves + (C)
    + sp.Rational(3, 2) * v2n * sol[VC]           # (3/2)v2 source: current up into C, voltage VC
)
print("absorbed", absorbed, "delivered", sp.simplify(delivered))
assert sp.simplify(absorbed - delivered) == 0
print("PASS EE-108-01-2")
