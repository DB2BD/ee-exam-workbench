"""EE-104-02-2 independent check: common-base BJT stage with ICC feeding the collector node.

Givens (official crop): beta=100, VA=inf, +5 V, ICC=0.5 mA (into the collector node), RE=1k,
RB=100k (collector node to base), RL=1.5k, Rs=50, CB / CC1 / CC2 are ac shorts.
Assumptions not on the crop: VBE=0.7 V, VT=25 mV, NPN (emitter arrow out of the symbol).
Method: DC KCL at the collector node, then hybrid-pi nodal analysis of the ac circuit.
"""
import numpy as np
import sympy as sp

beta, ICC, RE, RB, RL, Rs = 100, sp.Rational(1, 2), 1, 100, sp.Rational(3, 2), sp.Rational(1, 20)  # mA, kOhm
VBE, VT = sp.Rational(7, 10), sp.Rational(25, 1000)

# DC: node C: ICC = IC + IRB, IRB = IB (flows C -> B), IC = beta IB, VE = (beta+1) IB RE
IB = sp.symbols("IB")
IBs = sp.solve(sp.Eq(ICC, beta * IB + IB), IB)[0]
IC, IE = beta * IBs, (beta + 1) * IBs
VE = IE * RE
VB = VE + VBE
VC = VB + IBs * RB


def close(x, y, tol=0.005):
    return abs(float(x) - y) / abs(y) <= tol


assert IE == ICC and close(IBs, 0.0049505, 1e-4) and close(IC, 0.49505, 1e-4)
assert close(VE, 0.5) and close(VB, 1.2) and close(VC, 1.69505, 1e-4)

# ac: hybrid-pi, base grounded.  unknowns ve (emitter), vc.  vs = 1
gm = IC / VT
rpi = beta / gm
ve, vc, vs, itest = sp.symbols("ve vc vs itest")
# emitter node: (ve - vs)/Rs + ve/RE + (ve - 0)/rpi + gm*(0 - ve)*(-1)... carefully:
# current gm*vbe flows collector->emitter, vbe = 0 - ve
eqE = sp.Eq((ve - vs) / Rs + ve / RE + ve / rpi - gm * (-ve), 0)   # current leaving emitter node toward ground paths
eqC = sp.Eq(vc / RL + vc / RB + gm * (-ve), 0)                      # collector: current gm*vbe drawn out of node
sol = sp.solve([eqE, eqC], [ve, vc], dict=True)[0]
Av = float((sol[vc] / vs).subs(vs, 1))
# input resistance looking into emitter node (vs source removed, Rs excluded)
Ri = float(1 / (1 / RE + 1 / rpi + gm))   # kOhm: RE || rpi || (1/gm) path of the controlled source
re = VT / IE
assert close(re * 1000, 50)
assert close(Ri * 1000, 47.619, 0.001)
assert close(Av, 14.275, 0.001)
# cross-check by closed form
Av2 = float(Ri / (Rs + Ri) * gm * (RL * RB / (RL + RB)))
assert close(Av, Av2, 1e-9)
print(f"IE={IE} IC={float(IC):.5f} VE={float(VE)} VB={float(VB)} VC={float(VC):.5f} Ri={Ri*1000:.3f} ohm Av={Av:.4f}")
print("PASS EE-104-02-2")
