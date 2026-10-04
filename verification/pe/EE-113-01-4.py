"""EE-113-01-4 independent check: y-parameters by definition (short each port, solve, take ratios).

Givens (official crop): port 1 shunt 1 ohm; series 2 F between top nodes;
port 2 shunt 1/3 ohm; VCCS 4 V1 pointing up into the port-2 top node.
I1, I2 enter the network at the top terminals.
"""
import sympy as sp

s = sp.symbols("s")

def port_currents(V1, V2):
    # Network has no internal nodes: KCL at each port's top node gives the entering current.
    I1 = V1 / 1 + (V1 - V2) * 2 * s
    I2 = V2 * 3 + (V2 - V1) * 2 * s - 4 * V1
    return sp.expand(I1), sp.expand(I2)

I1a, I2a = port_currents(1, 0)   # V2 short, V1 = 1 V
I1b, I2b = port_currents(0, 1)   # V1 short, V2 = 1 V
Y = sp.Matrix([[I1a, I1b], [I2a, I2b]])
assert sp.simplify(Y - sp.Matrix([[1 + 2 * s, -2 * s], [-(2 * s + 4), 2 * s + 3]])) == sp.zeros(2)
# Cross-check: parallel-connected sub-two-ports sum to the same matrix.
Ysum = (sp.Matrix([[1, 0], [0, 0]]) + sp.Matrix([[2 * s, -2 * s], [-2 * s, 2 * s]])
        + sp.Matrix([[0, 0], [0, 3]]) + sp.Matrix([[0, 0], [-4, 0]]))
assert sp.simplify(Y - Ysum) == sp.zeros(2)
print("PASS EE-113-01-4")
