"""EE-109-01-4 independent check: impulse + step response by Laplace transform.

Givens (official crop): 10u(t) V source (+ top) on the left; 4 delta(t) V source
on the bottom wire (+ left, - right = output reference); top branch: C1 = 1 F ||
R1 = 1 ohm || 6 delta(t) A source pointing left (from node b to node a); right
branch R2 = 1 ohm + L2 = 1 H from node b to the reference; v2 = v_b.
Zero initial state.  (The note solves in the time domain; this is s-domain.)
"""
import sympy as sp

s, t = sp.symbols("s t", positive=True)
Va = 10 / s + 4                      # node a relative to the output reference
Vb = sp.symbols("Vb")
# KCL at b: (Vb - Va)(1/R1 + s C1) + 6 (source leaves b) + Vb/(R2 + s L2) = 0
sol = sp.solve(sp.Eq((Vb - Va) * (1 + s) + 6 + Vb / (1 + s), 0), Vb)[0]
sol = sp.apart(sp.simplify(sol), s)
print("V2(s) =", sol)
v2 = sp.inverse_laplace_transform(sol, s, t)
expected = 4 * sp.DiracDelta(t) + (5 + sp.exp(-t) * (sp.sin(t) - sp.cos(t))) * sp.Heaviside(t)
assert sp.simplify(v2 - expected) == 0, v2
print("PASS EE-109-01-4")
