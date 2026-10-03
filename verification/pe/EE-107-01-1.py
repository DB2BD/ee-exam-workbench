"""EE-107-01-1 independent check: nodal analysis with a CCVS, power in the 4 ohm resistor.

Givens (official crop): 50 V source (+ top) from node 1 to ground; 1 ohm from node 1 to node 3;
5 ohm node 1 -> node 2; 4 ohm node 2 -> node 3; 20 ohm node 2 -> ground with i_phi
flowing downward through it; CCVS 15*i_phi (+ top) from node 3 to ground.
"""
import sympy as sp

V2, V3, I50, Iccvs = sp.symbols("V2 V3 I50 Iccvs")
V1 = 50
iphi = V2 / 20
eqs = [
    sp.Eq(V3, 15 * iphi),                                  # CCVS constraint
    sp.Eq((V1 - V2) / 5, V2 / 20 + (V2 - V3) / 4),         # KCL node 2
]
sol = sp.solve(eqs, [V2, V3], dict=True)[0]
I4 = (sol[V2] - sol[V3]) / 4
P4 = I4**2 * 4
assert sol[V2] == 32 and sol[V3] == 24
assert I4 == 2 and P4 == 16
# independent check: power balance over all elements
I_1ohm = (V1 - sol[V3]) / 1
I_5ohm = (V1 - sol[V2]) / 5
P_src50 = V1 * (I_1ohm + I_5ohm)                           # current leaving + terminal
P_ccvs = -sol[V3] * (I_1ohm + I4)                          # current enters + terminal from node 3
P_res = I_1ohm**2 * 1 + I_5ohm**2 * 5 + I4**2 * 4 + iphi.subs(V2, sol[V2])**2 * 20
assert P_src50 + P_ccvs == P_res, (P_src50, P_ccvs, P_res)
print("PASS EE-107-01-1")
