"""EE-106-02-2 independent check (reference-book problem): MOS diff pair + PMOS mirror, divider feedback.

Givens (official crop): M1 gate = Vin; M1/M2 sources on ideal tail ISS; M3 (diode-connected, drain = gates of M3/M4)/M4 PMOS mirror;
output node = M4 drain = M2 drain = top of R2; R2 over R1 to ground; M2 gate = divider centre -> beta = R1/(R1+R2).
No numerical element values are given, so the check is symbolic (reference-book convention r_ON = r_OP = r_o, gmN = gm1 = gm2).
Method: exact small-signal nodal solution with all four gm and ro, compared with
  A_L = gmN [(ro/2) || (R1+R2)],  A_f = A_L/(1+A_L beta),  R_out,f = [(ro/2)||(R1+R2)]/(1+A_L beta)
in the limit gmP*ro >> 1, and with the reference-book unloaded A = gmN ro/2 (valid only for R1+R2 >> ro/2).
"""
import sympy as sp

gmN, gmP, ro, R1, R2, vin, vt = sp.symbols("gmN gmP ro R1 R2 vin vt", positive=True)
vs, vd1, vo = sp.symbols("vs vd1 vo")
beta = R1 / (R1 + R2)


def solve_gain(drive_in=True, test=False):
    vf = beta * vo
    vi = vin if drive_in else 0
    id1 = gmN * (vi - vs) + (vd1 - vs) / ro               # M1 drain -> source
    id2 = gmN * (vf - vs) + (vo - vs) / ro                # M2 drain -> source
    i3 = -gmP * vd1 - vd1 / ro                            # M3 source -> drain  (vsg = -vd1)
    i4 = -gmP * vd1 - vo / ro                             # M4 source -> drain into the output node
    eqs = [sp.Eq(id1 + id2, 0),                           # ideal tail current source
           sp.Eq(i3, id1),                                # node vd1
           sp.Eq(i4 - id2 - vo / (R1 + R2) + (vt if test else 0), 0)]   # output node (vt: test current injected)
    return sp.solve(eqs, [vs, vd1, vo], dict=True)[0]


sol = solve_gain()
Af_exact = sp.simplify(sol[vo] / vin)
Rout_exact = sp.simplify(solve_gain(drive_in=False, test=True)[vo] / vt)   # injected test current vt (A) -> vo/vt = ohm

Rl = sp.Rational(1, 2) * ro * (R1 + R2) / (sp.Rational(1, 2) * ro + R1 + R2)    # (ro/2) || (R1+R2)
A_L = gmN * Rl
Af_formula = A_L / (1 + A_L * beta)
Rout_formula = Rl / (1 + A_L * beta)

# exact -> formula as the mirror becomes ideal (gmP*ro >> 1) with gmP = k gmN, k fixed, ro large: compare numerically
vals = {gmN: 1e-3, ro: 100e3, R1: 10e3, R2: 90e3}
for k in (1, 3):
    v = {**vals, gmP: k * 1e-3}
    ex = float(Af_exact.subs(v)); fo = float(Af_formula.subs(v))
    assert abs(ex - fo) / abs(fo) < 0.02, (k, ex, fo)        # gmP*ro = 100..300 -> within 2 %
    rex = float(Rout_exact.subs(v)); rfo = float(Rout_formula.subs(v))
    assert abs(rex - rfo) / abs(rfo) < 0.03, (k, rex, rfo)
# strict limit gmP -> infinity
lim = sp.limit(Af_exact, gmP, sp.oo)
assert sp.simplify(lim - Af_formula) == 0
limR = sp.limit(Rout_exact, gmP, sp.oo)
assert sp.simplify(limR - Rout_formula) == 0
# high-loop-gain limit 1 + R2/R1
assert sp.simplify(sp.limit(Af_formula, gmN, sp.oo) - (1 + R2 / R1)) == 0
# reference-book unloaded A  vs loaded A_L
A_book = gmN * ro / 2
v = {**vals, gmP: 1e-3}
ratio = float((A_L / A_book).subs(v))
assert abs(ratio - (R1 + R2).subs(v) / ((R1 + R2).subs(v) + 50e3)) < 1e-9 and abs(ratio - 0.6667) < 1e-3
Af_book = float((A_book / (1 + A_book * beta)).subs(v))
Af_loaded = float(Af_formula.subs(v))
Af_ex = float(Af_exact.subs(v))
print(f"numbers (gm=1mS ro=100k R1=10k R2=90k gmP=1mS): exact={Af_ex:.3f} loaded-formula={Af_loaded:.3f} "
      f"book-unloaded={Af_book:.3f} ideal 1+R2/R1=10")
assert abs(Af_ex - Af_loaded) / Af_loaded < 0.02 and abs(Af_book - Af_loaded) / Af_loaded > 0.01
Ro_book = float(((R1 + R2) * ro / 2 / ((R1 + R2) + ro / 2) / (1 + A_book * beta)).subs(v))
print(f"Rout: exact={float(Rout_exact.subs(v)):.1f} loaded-formula={float(Rout_formula.subs(v)):.1f} book-form-with-unloaded-A={Ro_book:.1f} ohm")
print("PASS EE-106-02-2")
