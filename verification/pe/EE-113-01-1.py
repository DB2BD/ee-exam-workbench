"""EE-113-01-1 independent check: nodal solve + whole-circuit power balance.

Givens (official crop): single top node vx over bottom reference; 6 A up (into
top), 3 ohm (i3 downward), 9 ohm, CCCS 0.9 i3 up, 15 ohm + (6||6), 4 A down.
"""
import sympy as sp

vx = sp.symbols("vx")
i3 = vx / 3
Rright = 15 + sp.Rational(6 * 6, 6 + 6)
vx_val = sp.solve(sp.Eq(6 + sp.Rational(9, 10) * i3, vx / 3 + vx / 9 + vx / Rright + 4), vx)[0]
assert vx_val == 10
Pdep = vx_val * sp.Rational(9, 10) * i3.subs(vx, vx_val)   # current leaves + terminal -> delivered
assert Pdep == 30
# Power balance: delivered by sources = absorbed by resistors + 4 A sink.
delivered = 6 * vx_val + Pdep
absorbed = vx_val**2 * (sp.Rational(1, 3) + sp.Rational(1, 9) + 1 / Rright) + 4 * vx_val
assert delivered == absorbed
print("PASS EE-113-01-1")
