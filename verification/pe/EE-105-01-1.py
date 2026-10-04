"""EE-105-01-1: DC nodal analysis. Ground = bottom rail. Units: V, kOhm, mA.
Top branch: node L -> 6 V source (- left, + right) -> 1k -> node R, so branch current L->R = (VL+6-VR)/1.
2 mA source pushes up into node L; 1k between L and M; 4 mA from M to R; 2k from M and from R to ground."""
import sympy as sp
VL, VM, VR = sp.symbols("VL VM VR")
sol = sp.solve([
    sp.Eq(2, (VL - VM) / 1 + (VL + 6 - VR) / 1),
    sp.Eq((VL - VM) / 1, 4 + VM / 2),
    sp.Eq(4 + (VL + 6 - VR) / 1, VR / 2),
], [VL, VM, VR])
Io = sol[VM] / 2
assert Io == sp.Rational(-4, 3), Io
print("PASS EE-105-01-1")
