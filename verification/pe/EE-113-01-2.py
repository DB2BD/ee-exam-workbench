"""EE-113-01-2 independent check: element-by-element nodal solve (no series-parallel pre-combination).

Givens (official crop): 1∠0° A up into V1; 5 ohm and -j10 ohm V1-gnd;
(-j5 || j10) between V1 and an internal node equal to V2; j5 ohm, 10 ohm V2-gnd;
0.5∠-90° A source pointing down (leaving V2). omega = 10 rad/s, cosine reference.
"""
import cmath
import math
import sympy as sp

V1, V2 = sp.symbols("V1 V2")
I = sp.I
Is2 = sp.Rational(1, 2) * sp.exp(-I * sp.pi / 2)  # leaves node V2
eqs = [
    sp.Eq(V1 / 5 + V1 / (-10 * I) + (V1 - V2) / (-5 * I) + (V1 - V2) / (10 * I), 1),
    sp.Eq(V2 / (5 * I) + V2 / 10 + (V2 - V1) / (-5 * I) + (V2 - V1) / (10 * I) + Is2, 0),
]
s = sp.solve(eqs, [V1, V2], dict=True)[0]
v1, v2 = complex(s[V1]), complex(s[V2])
assert abs(v1 - (1 - 2j)) < 1e-12 and abs(v2 - (-2 + 4j)) < 1e-12
assert abs(abs(v1) - math.sqrt(5)) < 1e-9 and abs(math.degrees(cmath.phase(v1)) + 63.4349) < 1e-3
assert abs(abs(v2) - math.sqrt(20)) < 1e-9 and abs(math.degrees(cmath.phase(v2)) - 116.5651) < 1e-3
print("PASS EE-113-01-2")
