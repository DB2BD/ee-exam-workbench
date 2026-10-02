"""EE-114-05-1 independent check: complex power of a single load.

Givens (official crop): V = 100∠alpha (RMS), I = I_rms∠60°, P = 500√3 W, Q = 500 var.
"""
import sympy as sp

I, a = sp.symbols("I alpha", real=True)
S = 500 * sp.sqrt(3) + 500 * sp.I

# Method 1: S = V I*  ->  |S| = 100 I, angle(S) = alpha - 60°.
I_rms = sp.solve(sp.Eq(100 * I, sp.Abs(S)), I)[0]
alpha = sp.deg(sp.arg(S)) + 60
assert I_rms == 10
assert sp.simplify(alpha - 90) == 0

# Method 2: rebuild S from the phasors with numeric complex arithmetic.
import cmath, math
V = cmath.rect(100, math.radians(float(alpha)))
Ip = cmath.rect(float(I_rms), math.radians(60))
S_back = V * Ip.conjugate()
assert abs(S_back - complex(500 * math.sqrt(3), 500)) < 1e-9
print("PASS EE-114-05-1")
