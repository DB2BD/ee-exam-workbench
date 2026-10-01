"""EE-112-02-1 independent check: common-base stage, high-frequency poles and midband gain.

Givens (official crop): beta = 100, VBE = 0.7 V, VA = inf, Cpi = 10 pF, Cmu = 1 pF,
Rs = 50, RE = 0.5k, RB = 100k (collector to the bypassed base), RL = 1k, IQ = 0.5 mA
from 5 V into the collector node; the three "inf" capacitors are AC shorts.
VT is not given: 25 mV is the main branch, 26 mV is checked as the alternative.
"""
import math

import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


def solve(VT):
    beta, IQ = 100, sp.Rational(1, 2000)
    Rs, RE, RB, RL = 50, 500, 100_000, 1000
    Cpi, Cmu = sp.Rational(1, 10**11), sp.Rational(1, 10**12)
    IE = IQ                                    # collector-node KCL: IQ = IC + IB
    IC = sp.Rational(beta, beta + 1) * IE
    gm = IC / VT
    rpi = beta / gm
    # DC: forward-active check (VCB > 0).
    VB = sp.Rational(7, 10) + IE * RE
    VC = VB + IE / (beta + 1) * RB
    assert VC - VB > 0

    # Full hybrid-pi nodal model with both capacitors (base = AC ground, vi = 1).
    s, ve, vo = sp.symbols("s ve vo")
    vpi = -ve
    kcl_e = sp.Eq((ve - 1) / Rs + ve / RE + ve * s * Cpi - vpi / rpi - gm * vpi, 0)
    kcl_c = sp.Eq(vo / RL + vo / RB + vo * s * Cmu + gm * vpi, 0)
    sol = sp.solve([kcl_e, kcl_c], [ve, vo], dict=True)[0]
    H = sp.simplify(sol[vo])
    Av = H.subs(s, 0)
    poles = sp.solve(sp.denom(sp.together(H)), s)
    f_poles = sorted(float(-p / (2 * sp.pi)) for p in poles)
    return f_poles, float(Av)


(f_mu, f_pi), Av = solve(sp.Rational(25, 1000))
assert close(f_pi, 668.451e6), f_pi
assert close(f_mu, 160.746e6), f_mu
assert close(Av, 9.336153), Av

# Independent closed forms (open-circuit time constants; current division for Av).
re = 0.025 / 0.5e-3
par = lambda *r: 1 / sum(1 / x for x in r)
assert close(1 / (2 * math.pi * par(50, 500, re) * 10e-12), f_pi)
assert close(1 / (2 * math.pi * par(1000, 100e3) * 1e-12), f_mu)
ie = (1 / (50 + par(500, re))) * 500 / (500 + re)
assert close(100 / 101 * ie * par(1000, 100e3), Av)

(f_mu26, f_pi26), Av26 = solve(sp.Rational(26, 1000))
assert close(f_pi26, 656.21e6) and close(f_mu26, 160.746e6) and close(Av26, 9.1446)
print(f"VT=25mV fHpi={f_pi/1e6:.3f}MHz fHmu={f_mu/1e6:.3f}MHz Av={Av:.6f}; VT=26mV {f_pi26/1e6:.3f}MHz Av={Av26:.4f}")
print("PASS EE-112-02-1")
