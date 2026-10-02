"""EE-114-02-1 independent check: BJT differential pair, Ri = v1/i1 and Av = vo/v1.

Givens (official crop): Q1 = Q2 active, beta = 40, ro = inf, VT = 25 mV, IS = 2 mA,
RC = RS = 2 kohm; Q1 base = v1, Q2 base = v2, vo = vc2 - vc1 (+ at Q2 collector).
Main branch: IS sets the total emitter current (IE = 1 mA each, IC = alpha IE).
Alternative branch: IC ~= IE = 1 mA.
Method: full hybrid-pi nodal solve in SymPy (unknown emitter node), compared with
T-model closed forms Ri = (beta+1)re v1/(v1-ve), Av = alpha RC (1-k)/re.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005 if y else abs(float(x)) < 1e-12


def solve(IC):
    beta, VT, RC, RS = 40, sp.Rational(1, 40), 2000, 2000
    gm = IC / VT
    rpi = beta / gm
    v1, k, ve = sp.symbols("v1 k ve")
    v2 = k * v1
    ib1, ib2 = (v1 - ve) / rpi, (v2 - ve) / rpi
    kcl = sp.Eq((beta + 1) * (ib1 + ib2), ve / RS)
    ves = sp.solve(kcl, ve)[0]
    vc1 = -beta * ib1.subs(ve, ves) * RC
    vc2 = -beta * ib2.subs(ve, ves) * RC
    Ri = sp.simplify(v1 / ib1.subs(ve, ves))
    Av = sp.simplify((vc2 - vc1) / v1)
    return {kk: (Ri.subs(k, kk), Av.subs(k, kk)) for kk in (-1, 1, -3)}


exact = solve(sp.Rational(40, 41) / 1000)
expect = {-1: (1025.0, 156.097561), 1: (165025.0, 0.0), -3: (514.096573, 312.195122)}
for kk, (ri, av) in expect.items():
    assert close(exact[kk][0], ri), (kk, exact[kk])
    assert close(exact[kk][1], av), (kk, exact[kk])

# T-model closed forms (different route): re = VT/IE, alpha = 40/41.
re, alpha, RS, RC = 25.0, 40 / 41, 2000.0, 2000.0
for kk, (ri, av) in expect.items():
    ve = (1 + kk) / (2 + re / RS)
    assert close(41 * re / (1 - ve), ri)
    assert close(alpha * RC * (1 - kk) / re, av)
assert close(41 * (re + 2 * RS), 165025.0)  # common-mode: (beta+1)(re + 2RS)

approx = solve(sp.Rational(1, 1000))
for kk, (ri, av) in {-1: (1000.0, 160.0), 1: (165000.0, 0.0), -3: (501.52, 320.0)}.items():
    assert close(approx[kk][0], ri) and close(approx[kk][1], av), (kk, approx[kk])

print("alpha branch:", {kk: (round(float(a), 3), round(float(b), 4)) for kk, (a, b) in exact.items()})
print("PASS EE-114-02-1")
