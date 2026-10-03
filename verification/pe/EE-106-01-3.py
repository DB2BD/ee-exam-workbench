"""EE-106-01-3 independent check: two ideal op-amps (generalized impedance converter), Z_in = V1 / Is.

Givens (official crop): Is (arrow up) into node 1; Z1: V1-V2; Z2: V2-V3; Z3: V3-V4; Z4: V4-V5; Z5: V5-ground.
Op-amp A: + at V1, - at V3, output node V4.  Op-amp B: - at V3, + at V5, output node V2.
Ideal op-amps: V+ = V-, zero input current.  Five equations: KCL at nodes 1, 3, 5 and the two virtual shorts.
"""
import sympy as sp

Z1, Z2, Z3, Z4, Z5, Is = sp.symbols("Z1 Z2 Z3 Z4 Z5 Is")
V1, V2, V3, V4, V5 = sp.symbols("V1 V2 V3 V4 V5")
eqs = [
    sp.Eq(Is, (V1 - V2) / Z1),                               # node 1 (op-amp input draws no current)
    sp.Eq((V3 - V2) / Z2 + (V3 - V4) / Z3, 0),               # node 3
    sp.Eq((V5 - V4) / Z4 + V5 / Z5, 0),                      # node 5
    sp.Eq(V1, V3),                                           # op-amp A virtual short
    sp.Eq(V3, V5),                                           # op-amp B virtual short
]
sol = sp.solve(eqs, [V1, V2, V3, V4, V5], dict=True)[0]
Zin = sp.simplify(sol[V1] / Is)
assert sp.simplify(Zin - Z1 * Z3 * Z5 / (Z2 * Z4)) == 0, Zin
# numeric spot check with arbitrary complex impedances, plus KCL at the op-amp output nodes is not needed
vals = {Z1: 2 + 1j, Z2: 3 - 2j, Z3: 5 + 0.5j, Z4: 1 + 4j, Z5: 7 - 1j}
num = complex(Zin.subs(vals))
assert abs(num - complex((Z1 * Z3 * Z5 / (Z2 * Z4)).subs(vals))) < 1e-12
# individual node voltages used in the note
assert sp.simplify(sol[V4] / sol[V1] - (1 + Z4 / Z5)) == 0
assert sp.simplify(sol[V2] / sol[V1] - (1 - Z2 * Z4 / (Z3 * Z5))) == 0
print("PASS EE-106-01-3")
